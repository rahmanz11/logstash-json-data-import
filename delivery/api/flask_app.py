from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
from api.elastic_test import connect_elasticsearch
from flask import request, Flask, Blueprint
from flask_restx import Api, Resource
from flask_httpauth import HTTPBasicAuth
from elasticsearch import helpers, RequestError
import re
import time
from flask_cors import CORS
from flask_restx import fields

app = Flask(__name__)
authorizations = {
    "Authorization": {
        "type": "basic",
        "in": "header",
        "name": "Authorization",
    }
}
api = Api(
    app,
    title="Search API",
    version="1.0",
    authorizations=authorizations,
    security="Authorization",
)

auth = HTTPBasicAuth()

CORS(app, resources={r"/car/*": {"origins": "*"}})
formatter = logging.Formatter(fmt='%(asctime)s %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger("Car Search Log")
logger.setLevel(logging.DEBUG)

handler = TimedRotatingFileHandler('search.log',
                                   when="d",
                                   interval=1,
                                   backupCount=15)
handler.setFormatter(formatter)
logger.addHandler(handler)

es = connect_elasticsearch()

ns = api.namespace('car', description='Car Search API')


@auth.verify_password
def authenticate(username, password):
    if username and password:
        if username == 'user' and password == 'pass':
            return True
        elif username == 'uu' and password == 'pp':
            return True
    return False


@auth.error_handler
def auth_error():
    return {
        'code': 401,
        'message': 'Please provide valid auth credential'
    }

v2_search_request = api.model('Search Request', {
    'brand': fields.String(readOnly=True, description='The engine keyword', required=False),
    'model': fields.String(readOnly=True, description='The engine keyword', required=False),
    'generation': fields.String(readOnly=True, description='The engine keyword', required=False),
    'engine': fields.String(readOnly=True, description='The engine keyword', required=False),
    'engineDisplacement': fields.String(readOnly=True, description='The engine keyword', required=False),
    'acceleration': fields.String(readOnly=True, description='The engine keyword', required=False),
    'maxspeed': fields.String(readOnly=True, description='The engine keyword', required=False),
    'productionyears': fields.String(readOnly=True, description='Generation years', required=False),
    'generationyears': fields.String(readOnly=True, description='Generation years', required=False),
    'coupe': fields.String(readOnly=True, description='Generation years', required=False),
    'page': fields.Integer,
    'size': fields.Integer
})

search_request = api.model('Search Request', {
    'keyword': fields.String(readOnly=True, description='The search keyword', required=True),
    'page': fields.Integer,
    'size': fields.Integer
})

response_body = api.model('Response Body', {
    'generationyears': fields.String(description='Generation years'),
    'brand': fields.String(description='Car brand'),
    'coupe': fields.String(description='Coupe'),
    'model': fields.String(description='Car model'),
    'engine': fields.String(description='Car engine'),
    'generation': fields.String(description='Car generation'),
    'productionyears': fields.String(description='Production years')
})

search_response = api.model('Search Response', {
    'results': fields.Nested(response_body)
})

v2_response_body = api.model('Response Body', {
    'brand': fields.String(description='Car brand'),
    'model': fields.String(description='Car model'),
    'engine': fields.String(description='Car engine'),
    'generation': fields.String(description='Car generation'),
    'coupe': fields.String(description='Coupe'),
    'engineDisplacement': fields.String(description='EngineDisplacement'),
    'maxspeed': fields.String(description='Maxspeed'),
    'acceleration': fields.String(description='Acceleration'),
    'generationyears': fields.String(description='Generation years'),
    'productionyears': fields.String(description='Production years')
})

v2_search_response = api.model('V2 Search Response', {
    'results': fields.Nested(v2_response_body)
})

def has_numbers_in_3rd_brackets(s):
    return bool(re.search(r'\[\[\d+\]\]', s))


def get_values(s):
    m = re.search(r"\[\[(\w+)\]\]", s)
    co2 = m.group(1)
    keyword = s.split("[[")
    return keyword[0], co2


def validate(value):
    regex_letters = "[a-zA-Z0-9]+"
    if re.search(regex_letters, value):
        return "".join(re.findall(regex_letters, value))
    else:
        return None

def is_numeric_present(value):
    regex_numbers = "[0-9]+"
    if re.search(regex_numbers, value):
        return value
    else:
        return None

def is_alpha_numeric_present(value):
    regex_letters = "[a-zA-Z0-9]+"
    if re.search(regex_letters, value):
        return value
    else:
        return None


def prepare_value(request, field, query_body):
    now = datetime.now()
    regex_query = "[^a-zA-Z0-9$&+,:;=?@#|'<>.^*()%!]*"
    value = request[field].strip()
    logger.debug("time: %s, %s value: %s", now, field, value)
    value = validate(value)
    logger.debug('valid? %s', value)
    if value:
        format = regex_query.join(value)
        value = ".*" + format + ".*"
        query_body['query']['bool']['should'].append(
            build_query_param(value, field)
        )

    return value, query_body


def build_query_param(value, field_name):

    max_determinized_states = 10000000
    case_insensitive = True

    return {
        "regexp": {
            field_name + ".keyword": {
                "value": value,
                "flags": "ALL",
                "case_insensitive": case_insensitive,
                "max_determinized_states": max_determinized_states,
                "rewrite": "constant_score"
            }
        }
    }


def build_range_query(value, field, query_body, left, right):
    query_body['query']['bool']['must'].append(
        {"range":  {field: {"gte": left, "lte": right, "boost": 2.0}}}
    )
    return value, query_body

def build_match_query(request, field, query_body):
    now = datetime.now()
    value = request[field].strip()

    logger.debug("time: %s, %s value: %s", now, field, value)

    value = is_alpha_numeric_present(value)
    if value:
        query_body['query']['bool']['must'].append(
            {"match":  {field: value}}
        )
        return value, query_body
    
    return None, None


@ns.route('/v2/search')
class GetSearchResult(Resource):
    @auth.login_required
    @api.marshal_with(v2_search_response)
    @api.expect(search_request)
    def post(self):

        _list = []
        start_time = time.time()
        now = datetime.now()
        response = {
            'results': _list
        }

        page = 0
        if 'page' in request.json:
            page = request.json['page']
            if page is None:
                page = 0
            elif page > 0:
                page = page - 1

        size = 50
        if 'size' in request.json:
            size = request.json['size']
            if size is None or size < 0:
                size = 50

        query_body = {
            "from": page,
            "size": size,
            "query": {
                "bool": {
                    "must": []
                }
            },
            "sort": [
                {
                    "_score": {
                        "order": "desc"
                    }
                }
            ]
        }

        brand = None
        model = None
        coupe = None
        engine = None
        generation = None
        generationyears = None
        productionyears = None
        engineDisplacement = None
        maxspeed = None
        acceleration = None

        i = 0
        if 'brand' in request.json:
            i += 1
            brand, query_body = build_match_query(
                request.json, 'brand', query_body)

        if 'model' in request.json:
            i += 1
            model, query_body = build_match_query(
                request.json, 'model', query_body)

        if 'coupe' in request.json:
            i += 1
            coupe, query_body = build_match_query(
                request.json, 'coupe', query_body)

        if 'engine' in request.json:
            i += 1
            engine, query_body = build_match_query(
                request.json, 'engine', query_body)

        if 'generation' in request.json:
            i += 1
            generation, query_body = build_match_query(
                request.json, 'generation', query_body)

        if 'generationyears' in request.json:
            i += 1
            generationyears, query_body = build_match_query(
                request.json, 'generationyears', query_body)

        if 'productionyears' in request.json:
            i += 1
            productionyears, query_body = build_match_query(
                request.json, 'productionyears', query_body)

        if 'engineDisplacement' in request.json:
            i += 1
            engineDisplacement, query_body = build_match_query(
                request.json, 'engineDisplacement', query_body)

        if 'maxspeed' in request.json:
            i += 1
            now = datetime.now()
            value = request.json['maxspeed'].strip()

            logger.debug("time: %s, %s value: %s", now, 'maxspeed', value)

            value = is_numeric_present(value)
            if value and (int(value) > 0):
                left = int(value) - 1
                right = int(value) + 1
                maxspeed, query_body = build_range_query(
                    value, 'maxspeed', query_body, left, right)

        if 'acceleration' in request.json:
            i += 1
            now = datetime.now()
            value = request.json['acceleration'].strip()

            logger.debug("time: %s, %s value: %s", now, 'acceleration', value)

            value = is_numeric_present(value)
            if value and (float(value) > 0):
                left = float(value) - 0.1
                right = float(value) + 0.1
                maxspeed, query_body = build_range_query(
                    value, 'acceleration', query_body, left, right)

        if not (brand or model
                or engine or engineDisplacement
                or coupe or generation
                or generationyears or productionyears
                or maxspeed or acceleration):
            return {
                'code': 401,
                'message': 'Please provide input'
            }

        logger.debug("search query: %s", query_body)
        index_name = "car_search_data"
        try:
            res = es.search(index=index_name, body=query_body)
        except RequestError as e:
            logger.error(e.info['error']['caused_by']
                         ['caused_by']['reason'])
            response['code'] = 500
            response['message'] = 'Error occurred while querying'
            return response

        hits = res['hits']['hits']

        if hits and len(hits) > 0:
            for hit in hits:
                data = {
                    'brand': None,
                    'coupe': None,
                    'model': None,
                    'engine': None,
                    'generation': None,
                    'engineDisplacement': None,
                    'maxspeed': None,
                    'acceleration': None,
                    'productionyears': None,
                    'generationyears': None
                }
                data['id'] = hit['_id']
                source = hit['_source']
                if 'brand' in source \
                    and source['brand'] is not None \
                        and source['brand']:
                    data['brand'] = ''.join(source['brand'])
                if 'coupe' in source \
                    and source['coupe'] is not None \
                        and source['coupe']:
                    data['coupe'] = ''.join(source['coupe'])
                if 'model' in source \
                    and source['model'] is not None \
                        and source['model']:
                    data['model'] = ''.join(source['model'])
                if 'generation' in source \
                    and source['generation'] is not None \
                        and source['generation']:
                    data['generation'] = ''.join(source['generation'])
                if 'engine' in source \
                    and source['engine'] is not None \
                        and source['engine']:
                    data['engine'] = ''.join(source['engine'])
                if 'maxspeed' in source \
                    and source['maxspeed'] is not None \
                        and source['maxspeed']:
                    data['maxspeed'] = ''.join(source['maxspeed'])
                if 'engineDisplacement' in source \
                    and source['engineDisplacement'] is not None \
                        and source['engineDisplacement']:
                    data['engineDisplacement'] = ''.join(source['engineDisplacement'])
                if 'acceleration' in source \
                    and source['acceleration'] is not None \
                        and source['acceleration']:
                    data['acceleration'] = ''.join(source['acceleration'])
                if 'productionyears' in source \
                    and source['productionyears'] is not None \
                        and source['productionyears']:
                    data['productionyears'] = ''.join(
                        source['productionyears'])
                if 'generationyears' in source \
                    and source['generationyears'] is not None \
                        and source['generationyears']:
                    data['generationyears'] = ''.join(
                        source['generationyears'])

                _list.append(data)

        logger.debug("total time spent - at: %s, value: %s",
                     now, (time.time() - start_time))

        response['results'] = _list
        
        return response

# @ns.route('/v2/search_')


class GetSearchResult(Resource):
    @auth.login_required
    @api.marshal_with(search_response)
    @api.expect(search_request)
    def post(self):

        _list = []
        start_time = time.time()
        now = datetime.now()
        response = {
            'results': _list
        }

        page = 0
        if 'page' in request.json:
            page = request.json['page']
            if page is None:
                page = 0
            elif page > 0:
                page = page - 1

        size = 50
        if 'size' in request.json:
            size = request.json['size']
            if size is None or size < 0:
                size = 50

        query_body = {
            "from": page,
            "size": size,
            "query": {
                "bool": {
                    "minimum_should_match": "75%",
                    "should": []
                }
            },
            "sort": [
                {
                    "_score": {
                        "order": "desc"
                    }
                }
            ]
        }

        brand = None
        model = None
        coupe = None
        engine = None
        generation = None
        generationyears = None
        productionyears = None
        engineDisplacement = None
        maxspeed = None
        acceleration = None

        i = 0
        if 'brand' in request.json:
            i += 1
            brand, query_body = prepare_value(
                request.json, 'brand', query_body)

        if 'model' in request.json:
            i += 1
            model, query_body = prepare_value(
                request.json, 'model', query_body)

        if 'coupe' in request.json:
            i += 1
            coupe, query_body = prepare_value(
                request.json, 'coupe', query_body)

        if 'engine' in request.json:
            i += 1
            engine, query_body = prepare_value(
                request.json, 'engine', query_body)

        if 'generation' in request.json:
            i += 1
            generation, query_body = prepare_value(
                request.json, 'generation', query_body)

        if 'generationyears' in request.json:
            i += 1
            generationyears, query_body = prepare_value(
                request.json, 'generationyears', query_body)

        if 'productionyears' in request.json:
            i += 1
            productionyears, query_body = prepare_value(
                request.json, 'productionyears', query_body)

        if 'engineDisplacement' in request.json:
            i += 1
            engineDisplacement, query_body = prepare_value(
                request.json, 'engineDisplacement', query_body)

        if 'maxspeed' in request.json:
            i += 1
            maxspeed, query_body = prepare_value(
                request.json, 'maxspeed', query_body)

        if 'acceleration' in request.json:
            i += 1
            acceleration, query_body = prepare_value(
                request.json, 'acceleration', query_body)

        if not (brand or model
                or engine or engineDisplacement
                or coupe or generation
                or generationyears or productionyears
                or maxspeed or acceleration):
            return {
                'code': 401,
                'message': 'Please provide input'
            }

        query_body['query']['bool']['minimum_should_match'] = i

        logger.debug("search query: %s", query_body)
        index_name = "car_search_data"
        try:
            res = es.search(index=index_name, body=query_body)
        except RequestError as e:
            logger.error(e.info['error']['caused_by']
                         ['caused_by']['reason'])
            response['code'] = 500
            response['message'] = 'Error occurred while querying'
            return response

        hits = res['hits']['hits']

        if hits and len(hits) > 0:
            for hit in hits:
                data = {
                    'generationyears': None,
                    'brand': None,
                    'coupe': None,
                    'model': None,
                    'engine': None,
                    'generation': None,
                    'productionyears': None
                }
                data['id'] = hit['_id']
                source = hit['_source']
                if 'brand' in source \
                    and source['brand'] is not None \
                        and source['brand']:
                    data['brand'] = ''.join(source['brand'])
                if 'coupe' in source \
                    and source['coupe'] is not None \
                        and source['coupe']:
                    data['coupe'] = ''.join(source['coupe'])
                if 'model' in source \
                    and source['model'] is not None \
                        and source['model']:
                    data['model'] = ''.join(source['model'])
                if 'generation' in source \
                    and source['generation'] is not None \
                        and source['generation']:
                    data['generation'] = ''.join(source['generation'])
                if 'engine' in source \
                    and source['engine'] is not None \
                        and source['engine']:
                    data['engine'] = ''.join(source['engine'])
                if 'productionyears' in source \
                    and source['productionyears'] is not None \
                        and source['productionyears']:
                    data['productionyears'] = ''.join(
                        source['productionyears'])
                if 'generationyears' in source \
                    and source['generationyears'] is not None \
                        and source['generationyears']:
                    data['generationyears'] = ''.join(
                        source['generationyears'])

                _list.append(data)

        logger.debug("total time spent - at: %s, value: %s",
                     now, (time.time() - start_time))

        if _list is not None and len(_list) > 0:
            response['results'] = _list
        else:
            return {
                'code': 200,
                'message': 'No cars matching your search'
            }

        return response


@ns.route('/search')
class GetSearchResult(Resource):
    @auth.login_required
    @api.marshal_with(search_response)
    @api.expect(search_request)
    def post(self):

        max_determinized_states = 10000000
        start_time = time.time()
        now = datetime.now()
        response = {
            'results': []
        }

        value = ''
        search_text = None
        if 'keyword' in request.json:
            search_text = request.json['keyword'].strip()
            logger.debug("search_text - at: %s, value: %s", now, search_text)

        if search_text is None or not search_text:
            return {
                'code': 401,
                'message': 'Please provide input'
            }

        page = 0
        if 'page' in request.json:
            page = request.json['page']
            if page is None:
                page = 0
            elif page > 0:
                page = page - 1

        size = 50
        if 'size' in request.json:
            size = request.json['size']
            if size is None or size < 0:
                size = 50

        keyword = None
        co2 = None
        if has_numbers_in_3rd_brackets(search_text):
            keyword, co2 = get_values(search_text)
        else:
            keyword = search_text

        _list = []
        index_name = "car_search_data"

        if keyword is None or keyword.strip() == "":
            query_body = {
                "from": page,
                "size": size,
                "query": {
                    "bool": {
                        "minimum_should_match": 1,
                        "should": [
                            {
                                "match": {
                                    "co2": {
                                        "query": co2
                                    }
                                }
                            },
                            {
                                "match": {
                                    "co2Min": {
                                        "query": co2
                                    }
                                }
                            }
                        ]
                    }
                },
                "sort": [
                    {
                        "_score": {
                            "order": "desc"
                        }
                    }
                ]
            }
            logger.debug("co2-search, query : %s", query_body)
            try:
                res = es.search(index=index_name, body=query_body)
            except RequestError as e:
                logger.error(e.info['error']['caused_by']
                             ['caused_by']['reason'])
                response['code'] = 500
                response['message'] = 'Error occurred while querying'
                return response

            hits = res['hits']['hits']
        else:
            keyword = keyword.strip()
            logger.debug("keyword - at: %s, value: %s", now, keyword)
            logger.debug("co2 - at: %s, value: %s", now, co2)

            regex_letters = "[a-zA-Z0-9]+"
            if re.search(regex_letters, keyword) is None or len(keyword) < 3:
                return {
                    'code': 401,
                    'message': 'Please provide valid input of minimum 3 characters'
                }

            regex_query = "[^a-zA-Z0-9$&+,:;=?@#|'<>.^*()%!]*"

            letters = "".join(re.findall(regex_letters, keyword))

            format = regex_query.join(letters)
            value = ".*" + format + ".*"
            logger.debug("search value - at: %s, value: %s", now, value)

            case_insensitive = True
            query_body = {
                "from": page,
                "size": size,
                "query": {
                    "bool": {
                        "minimum_should_match": 1,
                        "should": [
                            {
                                "regexp": {
                                    "generation.keyword": {
                                        "value": value,
                                        "flags": "ALL",
                                        "case_insensitive": case_insensitive,
                                        "max_determinized_states": max_determinized_states,
                                        "rewrite": "constant_score"
                                    }
                                }
                            },
                            {
                                "regexp": {
                                    "brand.keyword": {
                                        "value": value,
                                        "flags": "ALL",
                                        "case_insensitive": case_insensitive,
                                        "max_determinized_states": max_determinized_states,
                                        "rewrite": "constant_score"
                                    }
                                }
                            },
                            {
                                "regexp": {
                                    "model.keyword": {
                                        "value": value,
                                        "flags": "ALL",
                                        "case_insensitive": case_insensitive,
                                        "max_determinized_states": max_determinized_states,
                                        "rewrite": "constant_score"
                                    }
                                }
                            },
                            {
                                "regexp": {
                                    "coupe.keyword": {
                                        "value": value,
                                        "flags": "ALL",
                                        "case_insensitive": case_insensitive,
                                        "max_determinized_states": max_determinized_states,
                                        "rewrite": "constant_score"
                                    }
                                }
                            },
                            {
                                "regexp": {
                                    "engine.keyword": {
                                        "value": value,
                                        "flags": "ALL",
                                        "case_insensitive": case_insensitive,
                                        "max_determinized_states": max_determinized_states,
                                        "rewrite": "constant_score"
                                    }
                                }
                            },
                            {
                                "match": {
                                    "productionyears": {
                                        "query": value
                                    }
                                }
                            },
                            {
                                "match": {
                                    "generationyears": {
                                        "query": value
                                    }
                                }
                            },
                            {
                                "term": {
                                    "engineDisplacement.keyword": {
                                        "value": keyword
                                    }
                                }
                            },
                            {
                                "term": {
                                    "acceleration.keyword": {
                                        "value": keyword
                                    }
                                }
                            },
                            {
                                "term": {
                                    "maxspeed.keyword": {
                                        "value": keyword
                                    }
                                }
                            }
                        ]
                    }
                },
                "sort": [
                    {
                        "_score": {
                            "order": "desc"
                        }
                    }
                ]
            }

            if co2 is not None:
                script_str = '(doc["co2Min.keyword"] != null && doc["co2Min.keyword"].value == "' + \
                    co2 + \
                    '") || (doc["co2.keyword"] != null && doc["co2.keyword"].value == "' + co2 + '")'
                _condition_body = ' if (doc["co2Min.keyword"].size() != 0 || doc["co2.keyword"].size() != 0) { if (' + \
                    script_str + ') { return true } } '
                query_body['query']['bool']['filter'] = []
                query_body['query']['bool']['filter'].append(
                    {
                        "script": {
                            "script": {
                                "source": _condition_body,
                                "lang": "painless"
                            }
                        }
                    }
                )

            logger.debug("search query: %s", query_body)

            try:
                res = es.search(index=index_name, body=query_body)
            except RequestError as e:
                logger.error(e.info['error']['caused_by']
                             ['caused_by']['reason'])
                response['code'] = 500
                response['message'] = 'Error occurred while querying'
                return response

            hits = res['hits']['hits']

            if hits is None or len(hits) <= 0:
                value = ''
                if ' ' in keyword:
                    arr = keyword.split()
                    if arr is not None and len(arr) > 0:
                        for str in arr:
                            letters = "".join(re.findall(regex_letters, str))
                            format = regex_query.join(letters)
                            if not value:
                                value = value + ".*" + format + ".*"
                            else:
                                value = value + format + ".*"
                else:
                    letters = "".join(re.findall(regex_letters, keyword))
                    format = regex_query.join(letters)
                    value = ".*" + format + ".*"

                logger.debug("search value - at: %s, value: %s", now, value)

                case_insensitive = True
                if co2 is not None:
                    combined_query_body = {
                        "from": page,
                        "size": size,
                        "query": {
                            "bool": {
                                "minimum_should_match": 1,
                                "should": [
                                    {
                                        "regexp": {
                                            "combined.keyword": {
                                                "value": value,
                                                "flags": "ALL",
                                                "case_insensitive": case_insensitive,
                                                "max_determinized_states": max_determinized_states,
                                                "rewrite": "constant_score"
                                            }
                                        }
                                    }
                                ]
                            }
                        },
                        "sort": [
                            {
                                "_score": {
                                    "order": "desc"
                                }
                            }
                        ]
                    }
                    script_str = '(doc["co2Min.keyword"] != null && doc["co2Min.keyword"].value == "' + \
                        co2 + \
                        '") || (doc["co2.keyword"] != null && doc["co2.keyword"].value == "' + co2 + '")'
                    _condition_body = ' if (doc["co2Min.keyword"].size() != 0 || doc["co2.keyword"].size() != 0) { if (' + \
                        script_str + ') { return true } } '
                    combined_query_body['query']['bool']['filter'] = []
                    combined_query_body['query']['bool']['filter'].append(
                        {
                            "script": {
                                "script": {
                                    "source": _condition_body,
                                    "lang": "painless"
                                }
                            }
                        }
                    )
                else:
                    combined_query_body = {
                        "from": page,
                        "size": size,
                        "query": {
                            "regexp": {
                                "combined.keyword": {
                                    "value": value,
                                    "flags": "ALL",
                                    "case_insensitive": case_insensitive,
                                    "max_determinized_states": max_determinized_states,
                                    "rewrite": "constant_score"
                                }
                            }
                        },
                        "sort": [
                            {
                                "_score": {
                                    "order": "desc"
                                }
                            }
                        ]
                    }

                logger.debug("re-search, query : %s", combined_query_body)

                try:
                    res = es.search(index=index_name, body=combined_query_body)
                except RequestError as e:
                    logger.error(e.info['error']['caused_by']
                                 ['caused_by']['reason'])
                    response['code'] = 500
                    response['message'] = 'Error occurred while querying'
                    return response

                hits = res['hits']['hits']

            if hits is None or len(hits) <= 0:
                if ' ' in keyword:
                    arr = keyword.split()
                    if arr is not None and len(arr) > 0:
                        query_body['query']['bool']['filter'] = []
                        script_str = ''
                        for str in arr:
                            letters = "".join(re.findall(regex_letters, str))
                            format = regex_query.join(letters)
                            value = ".*" + format + ".*"
                            query_body['query']['bool']['should'].append({
                                "regexp": {
                                    "generation.keyword": {
                                        "value": value,
                                        "flags": "ALL",
                                        "case_insensitive": case_insensitive,
                                        "max_determinized_states": max_determinized_states,
                                        "rewrite": "constant_score"
                                    }
                                }
                            })
                            query_body['query']['bool']['should'].append({
                                "regexp": {
                                    "engine.keyword": {
                                        "value": value,
                                        "flags": "ALL",
                                        "case_insensitive": case_insensitive,
                                        "max_determinized_states": max_determinized_states,
                                        "rewrite": "constant_score"
                                    }
                                }
                            })
                            query_body['query']['bool']['should'].append({
                                "term": {
                                    "engineDisplacement.keyword": {
                                        "value": keyword
                                    }
                                }
                            })
                            query_body['query']['bool']['should'].append({
                                "term": {
                                    "acceleration.keyword": {
                                        "value": keyword
                                    }
                                }
                            })
                            query_body['query']['bool']['should'].append({
                                "term": {
                                    "maxspeed.keyword": {
                                        "value": keyword
                                    }
                                }
                            })

                            if script_str:
                                script_str = script_str + ' && '
                            script_str = script_str + \
                                '(/' + value + '/i.matcher(doc["generation.keyword"].value).matches() || /' + \
                                value + \
                                '/i.matcher(doc["engine.keyword"].value).matches())'

                        if co2 is not None:
                            co2_script_str = '(doc["co2Min.keyword"].size() != 0 || doc["co2.keyword"].size() != 0) && ((doc["co2Min.keyword"] != null && doc["co2Min.keyword"].value == "' + \
                                co2 + \
                                '") || (doc["co2.keyword"] != null && doc["co2.keyword"].value == "' + co2 + '"))'
                            script_str = script_str + ' && ' + co2_script_str
                            _condition_body = ' if (' + \
                                script_str + ') { return true } '

                        query_body['query']['bool']['filter'].append(
                            {
                                "script": {
                                    "script": {
                                        "source": _condition_body,
                                        "lang": "painless"
                                    }
                                }
                            }
                        )

                    logger.debug("re-re-search, query : %s", query_body)
                    try:
                        res = es.search(index=index_name, body=query_body)
                    except RequestError as e:
                        logger.error(
                            e.info['error']['caused_by']['caused_by']['reason'])
                        response['code'] = 500
                        response['message'] = 'Error occurred while querying'
                        return response

                    hits = res['hits']['hits']

        if hits and len(hits) > 0:
            for hit in hits:
                data = {
                    'generationyears': None,
                    'brand': None,
                    'coupe': None,
                    'model': None,
                    'engine': None,
                    'generation': None,
                    'productionyears': None
                }
                data['id'] = hit['_id']
                source = hit['_source']
                if 'brand' in source \
                    and source['brand'] is not None \
                        and source['brand']:
                    data['brand'] = ''.join(source['brand'])
                if 'coupe' in source \
                    and source['coupe'] is not None \
                        and source['coupe']:
                    data['coupe'] = ''.join(source['coupe'])
                if 'model' in source \
                    and source['model'] is not None \
                        and source['model']:
                    data['model'] = ''.join(source['model'])
                if 'generation' in source \
                    and source['generation'] is not None \
                        and source['generation']:
                    data['generation'] = ''.join(source['generation'])
                if 'engine' in source \
                    and source['engine'] is not None \
                        and source['engine']:
                    data['engine'] = ''.join(source['engine'])
                if 'productionyears' in source \
                    and source['productionyears'] is not None \
                        and source['productionyears']:
                    data['productionyears'] = ''.join(
                        source['productionyears'])
                if 'generationyears' in source \
                    and source['generationyears'] is not None \
                        and source['generationyears']:
                    data['generationyears'] = ''.join(
                        source['generationyears'])

                _list.append(data)

        logger.debug("total time spent - at: %s, value: %s",
                     now, (time.time() - start_time))

        if _list is not None and len(_list) > 0:
            response['results'] = _list
        else:
            return {
                'code': 200,
                'message': 'No cars matching your search'
            }

        return response


@ns.route('/reindex')
class ReIndex(Resource):
    def post(self):

        query_body = {
            "size": 1000000,
            "query": {
                "constant_score": {
                    "filter": {
                        "match_all": {}
                    },
                    "boost": 1.2
                }
            },
            "fields": [
                "models.model.generations.generation.modifications.modification.generation",
                "models.model.generations.generation.modifications.modification.brand",
                "models.model.generations.generation.modifications.modification.model",
                "models.model.generations.generation.modifications.modification.coupe",
                "models.model.generations.generation.modifications.modification.engine",
                "models.model.generations.generation.modifications.modification.co2",
                "models.model.generations.generation.modifications.modification.co2Min",
                "models.model.generations.generation.modifications.modification.productionyears",
                "models.model.generations.generation.generationyears",
                "models.model.generations.generation.modifications.modification.maxspeed",
                "models.model.generations.generation.modifications.modification.acceleration",
                "models.model.generations.generation.modifications.modification.engineDisplacement",
                "models.model.generations.generation.modelYear"
            ],
            "_source": False
        }
        response = {}
        try:
            res = es.search(index="car_information_2", body=query_body)
        except Exception as e:
            logger.error(e)
            response['code'] = 500
            response['message'] = 'Error occurred while querying'
            return response

        hits = res['hits']['hits']
        list = []
        if hits is not None and len(hits) > 0:
            for hit in hits:
                if hit['fields'] is not None and hit['fields']['models'] is not None and len(hit['fields']['models']) > 0:
                    for model in hit['fields']['models']:
                        for mv in model.values():
                            for imv in mv:
                                for imvs in imv.values():
                                    for gns in imvs:
                                        for gnv in gns.values():
                                            for gn in gnv:
                                                generationyears = None
                                                if 'generationyears' in gn:
                                                    generationyears = ''.join(
                                                        gn['generationyears'])
                                                if 'modifications' in gn:
                                                    for ms in gn['modifications']:
                                                        for m in ms.values():
                                                            for modification in m:
                                                                data = {
                                                                    'generationyears': None,
                                                                    'brand': None,
                                                                    'coupe': None,
                                                                    'model': None,
                                                                    'co2': None,
                                                                    'co2Min': None,
                                                                    'generation': None,
                                                                    'maxspeed': None,
                                                                    'engine': None,
                                                                    'acceleration': None,
                                                                    'engineDisplacement': None,
                                                                    'productionyears': None,
                                                                    'combined': None
                                                                }
                                                                space = ' '
                                                                combined = ''

                                                                if 'brand' in modification:
                                                                    data['brand'] = ''.join(
                                                                        modification['brand']).replace('T-modell', 'Saloon')
                                                                    combined = combined + \
                                                                        data['brand'] + \
                                                                        space
                                                                if 'coupe' in modification:
                                                                    data['coupe'] = ''.join(
                                                                        modification['coupe']).replace('T-modell', 'Saloon')
                                                                    combined = combined + \
                                                                        data['coupe'] + \
                                                                        space
                                                                if 'model' in modification:
                                                                    data['model'] = ''.join(
                                                                        modification['model']).replace('T-modell', 'Saloon')
                                                                    combined = combined + \
                                                                        data['model'] + \
                                                                        space
                                                                if 'co2' in modification:
                                                                    data['co2'] = ''.join(
                                                                        modification['co2'])
                                                                if 'co2Min' in modification:
                                                                    data['co2Min'] = ''.join(
                                                                        modification['co2Min'])
                                                                if 'generation' in modification:
                                                                    data['generation'] = ''.join(
                                                                        modification['generation']).replace('T-modell', 'Saloon')
                                                                    combined = combined + \
                                                                        data['generation'] + \
                                                                        space
                                                                if 'engine' in modification:
                                                                    data['engine'] = ''.join(
                                                                        modification['engine']).replace('T-modell', 'Saloon')
                                                                    combined = combined + \
                                                                        data['engine'] + \
                                                                        space
                                                                if 'maxspeed' in modification:
                                                                    data['maxspeed'] = ''.join(
                                                                        modification['maxspeed'])
                                                                    combined = combined + \
                                                                        data['maxspeed'] + \
                                                                        space
                                                                if 'acceleration' in modification:
                                                                    data['acceleration'] = ''.join(
                                                                        modification['acceleration'])
                                                                    combined = combined + \
                                                                        data['acceleration'] + space
                                                                if 'engineDisplacement' in modification:
                                                                    data['engineDisplacement'] = ''.join(
                                                                        modification['engineDisplacement'])
                                                                    combined = combined + \
                                                                        data['engineDisplacement'] + space
                                                                if 'productionyears' in modification:
                                                                    data['productionyears'] = ''.join(
                                                                        modification['productionyears'])
                                                                    combined = combined + \
                                                                        data['productionyears'] + space
                                                                if generationyears:
                                                                    data['generationyears'] = generationyears
                                                                    combined = combined + \
                                                                        data['generationyears']

                                                                data['combined'] = combined

                                                                list.append(
                                                                    data)
        if list is not None and len(list) > 0:
            helpers.bulk(es, list, index='car_search_data')
        return response

@ns.route('/reindex3')
class ReIndex(Resource):
    def post(self):

        query_body = {
            "size": 1000000,
            "query": {
                "constant_score": {
                    "filter": {
                        "match_all": {}
                    },
                    "boost": 1.2
                }
            },
            "fields": [
                "models.model.generations.generation.modifications.modification.generation",
                "models.model.generations.generation.modifications.modification.brand",
                "models.model.generations.generation.modifications.modification.model",
                "models.model.generations.generation.modifications.modification.coupe",
                "models.model.generations.generation.modifications.modification.engine",
                "models.model.generations.generation.modifications.modification.co2",
                "models.model.generations.generation.modifications.modification.co2Min",
                "models.model.generations.generation.modifications.modification.productionyears",
                "models.model.generations.generation.generationyears",
                "models.model.generations.generation.modifications.modification.maxspeed",
                "models.model.generations.generation.modifications.modification.acceleration",
                "models.model.generations.generation.modifications.modification.engineDisplacement",
                "models.model.generations.generation.modelYear"
            ],
            "_source": False
        }
        response = {}
        try:
            res = es.search(index="car_information_3", body=query_body)
        except Exception as e:
            logger.error(e)
            response['code'] = 500
            response['message'] = 'Error occurred while querying'
            return response

        hits = res['hits']['hits']
        list = []
        if hits is not None and len(hits) > 0:
            for hit in hits:
                if hit['fields'] is not None and hit['fields']['models'] is not None and len(hit['fields']['models']) > 0:
                    for model in hit['fields']['models']:
                        for mv in model.values():
                            for imv in mv:
                                for imvs in imv.values():
                                    for gns in imvs:
                                        for gnv in gns.values():
                                            for gn in gnv:
                                                generationyears = None
                                                if 'generationyears' in gn:
                                                    generationyears = ''.join(
                                                        gn['generationyears'])
                                                if 'modifications' in gn:
                                                    for ms in gn['modifications']:
                                                        for m in ms.values():
                                                            for modification in m:
                                                                data = {
                                                                    'generationyears': None,
                                                                    'brand': None,
                                                                    'coupe': None,
                                                                    'model': None,
                                                                    'co2': None,
                                                                    'co2Min': None,
                                                                    'generation': None,
                                                                    'maxspeed': None,
                                                                    'engine': None,
                                                                    'acceleration': None,
                                                                    'engineDisplacement': None,
                                                                    'productionyears': None,
                                                                    'combined': None
                                                                }
                                                                space = ' '
                                                                combined = ''

                                                                if 'brand' in modification:
                                                                    data['brand'] = ''.join(
                                                                        modification['brand']).replace('T-modell', 'Saloon')
                                                                    combined = combined + \
                                                                        data['brand'] + \
                                                                        space
                                                                if 'coupe' in modification:
                                                                    data['coupe'] = ''.join(
                                                                        modification['coupe']).replace('T-modell', 'Saloon')
                                                                    combined = combined + \
                                                                        data['coupe'] + \
                                                                        space
                                                                if 'model' in modification:
                                                                    data['model'] = ''.join(
                                                                        modification['model']).replace('T-modell', 'Saloon')
                                                                    combined = combined + \
                                                                        data['model'] + \
                                                                        space
                                                                if 'co2' in modification:
                                                                    data['co2'] = ''.join(
                                                                        modification['co2'])
                                                                if 'co2Min' in modification:
                                                                    data['co2Min'] = ''.join(
                                                                        modification['co2Min'])
                                                                if 'generation' in modification:
                                                                    data['generation'] = ''.join(
                                                                        modification['generation']).replace('T-modell', 'Saloon')
                                                                    combined = combined + \
                                                                        data['generation'] + \
                                                                        space
                                                                if 'engine' in modification:
                                                                    data['engine'] = ''.join(
                                                                        modification['engine']).replace('T-modell', 'Saloon')
                                                                    combined = combined + \
                                                                        data['engine'] + \
                                                                        space
                                                                if 'maxspeed' in modification:
                                                                    data['maxspeed'] = ''.join(
                                                                        modification['maxspeed'])
                                                                    combined = combined + \
                                                                        data['maxspeed'] + \
                                                                        space
                                                                if 'acceleration' in modification:
                                                                    data['acceleration'] = ''.join(
                                                                        modification['acceleration'])
                                                                    combined = combined + \
                                                                        data['acceleration'] + space
                                                                if 'engineDisplacement' in modification:
                                                                    data['engineDisplacement'] = ''.join(
                                                                        modification['engineDisplacement'])
                                                                    combined = combined + \
                                                                        data['engineDisplacement'] + space
                                                                if 'productionyears' in modification:
                                                                    data['productionyears'] = ''.join(
                                                                        modification['productionyears'])
                                                                    combined = combined + \
                                                                        data['productionyears'] + space
                                                                if generationyears:
                                                                    data['generationyears'] = generationyears
                                                                    combined = combined + \
                                                                        data['generationyears']

                                                                data['combined'] = combined

                                                                list.append(
                                                                    data)
        if list is not None and len(list) > 0:
            helpers.bulk(es, list, index='car_search_data')
        return response


blueprint = Blueprint('api', __name__)
api.init_app(blueprint)
api.add_namespace(ns)
app.config['RESTX_MASK_HEADER'] = None
app.register_blueprint(blueprint)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4928, debug=False)
