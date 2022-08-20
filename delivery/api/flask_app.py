from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
from textwrap import indent
from api.elastic_test import connect_elasticsearch
from flask import request, Flask, Blueprint
from flask_restx import Api, Resource
from flask_httpauth import HTTPBasicAuth
from elasticsearch import helpers, RequestError
import re
import time

app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()

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
        if username == 'm2u' and password == 'Z$KF@S#SmU':
            return True
    return False


@auth.error_handler
def auth_error():
    return {
        'code': 401,
        'message': 'Please provide auth credential'
    }


@ns.route('/search')
class GetSearchResult(Resource):
    @auth.login_required
    def post(self):
        start_time = time.time()
        now = datetime.now()
        keyword = request.json['keyword'].strip()
        logger.debug("keyword - at: %s, value: %s", now, keyword)
        
        letters = "".join(re.findall("[a-zA-Z0-9]+", keyword))
        format = "[^a-zA-Z0-9]*".join(letters)
        value = ".*" + format + ".*"
        logger.debug("search value - at: %s, value: %s", now, value)
        
        case_insensitive = True

        query_body = {
            "size": 10000000,
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
                                    "max_determinized_states": 10000,
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
                                    "max_determinized_states": 10000,
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
                                    "max_determinized_states": 10000,
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
                                    "max_determinized_states": 10000,
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
                                    "max_determinized_states": 10000,
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

        if ' ' in keyword:
            arr = keyword.split()
            if arr is not None and len(arr) > 0:
                query_body['query']['bool']['filter'] = []
                script_str = ''
                for str in arr:
                    letters = "".join(re.findall("[a-zA-Z0-9]+", str))
                    format = "[^a-zA-Z0-9]*".join(letters)
                    value = ".*" + format + ".*"
                    query_body['query']['bool']['should'].append({
                        "regexp": {
                            "generation.keyword": {
                                "value": value,
                                "flags": "ALL",
                                "case_insensitive": case_insensitive,
                                "max_determinized_states": 10000,
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
                                "max_determinized_states": 10000,
                                "rewrite": "constant_score"
                            }
                        }
                    })
                    if script_str:
                        script_str = script_str + ' && '
                    script_str = script_str + '(/' + value + '/i.matcher(doc["generation.keyword"].value).matches() || /' + value + '/i.matcher(doc["engine.keyword"].value).matches())'
                
                _condition_body = ' if (' + script_str + ') { return true } '
                
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

        logger.debug(query_body)
        
        response = {
            'results': []
        }

        try:
            res = es.search(index="car_search_data", body=query_body)
        except RequestError as e:
            logger.error(e.info['error']['caused_by']['caused_by']['reason'])
            response['code'] = 500
            response['message'] = 'Error occurred while querying'
            return response
        _list = []
        hits = res['hits']['hits']
        for hit in hits:
            data = {
                'generationyears': None,
                'brand': None,
                'coupe': None,
                'model': None,
                'generation': None,
                'productionyears': None,
            }
            data['id'] = hit['_id']
            source = hit['_source']
            if 'generationyears' in source \
                and source['generationyears'] is not None \
                    and source['generationyears']:
                data['generationyears'] = ''.join(source['generationyears'])
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
                data['productionyears'] = ''.join(source['productionyears'])

            _list.append(data)

        response['results'] = _list
        logger.debug("total time spent - at: %s, value: %s", now, (time.time() - start_time) )
        return response


@ns.route('/search/detail')
class GetSearchResultDetail(Resource):
    @auth.login_required
    def post(self):
        time = datetime.now()
        keyword = request.json['keyword']
        logger.debug("keyword at %s: %s", time, keyword)

        false = False
        query_body = {
            "size": 100000,
            "query": {
                "constant_score": {
                    "filter": {
                        "nested": {
                            "path": "models",
                            "query": {
                                "nested": {
                                    "path": "models.model",
                                    "query": {
                                        "nested": {
                                            "path": "models.model.generations",
                                            "query": {
                                                "nested": {
                                                    "path": "models.model.generations.generation",
                                                    "query": {
                                                        "nested": {
                                                            "path": "models.model.generations.generation.modifications",
                                                            "query": {
                                                                "nested": {
                                                                    "path": "models.model.generations.generation.modifications.modification",
                                                                    "query": {
                                                                        "bool": {
                                                                            "should": [
                                                                                {
                                                                                    "match": {
                                                                                        "models.model.generations.generation.modifications.modification.generation": {
                                                                                            "query": keyword,
                                                                                            "minimum_should_match": 1
                                                                                        }
                                                                                    }
                                                                                },
                                                                                {
                                                                                    "match": {
                                                                                        "models.model.generations.generation.modifications.modification.brand": {
                                                                                            "query": keyword,
                                                                                            "minimum_should_match": 1
                                                                                        }
                                                                                    }
                                                                                },
                                                                                {
                                                                                    "match": {
                                                                                        "models.model.generations.generation.modifications.modification.model": {
                                                                                            "query": keyword,
                                                                                            "minimum_should_match": 1
                                                                                        }
                                                                                    }
                                                                                },
                                                                                {
                                                                                    "match": {
                                                                                        "models.model.generations.generation.modifications.modification.coupe": {
                                                                                            "query": keyword,
                                                                                            "minimum_should_match": 1
                                                                                        }
                                                                                    }
                                                                                },
                                                                                {
                                                                                    "match": {
                                                                                        "models.model.generations.generation.modifications.modification.engine": {
                                                                                            "query": keyword,
                                                                                            "minimum_should_match": 1
                                                                                        }
                                                                                    }
                                                                                }
                                                                            ]
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
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
                "models.model.generations.generation.modifications.modification.productionyears",
                "models.model.generations.generation.generationyears"
            ],
            "_source": false,
            "highlight": {
                "fields": {
                    "models.model.generations.generation.modifications.modification.generation": {},
                    "models.model.generations.generation.modifications.modification.brand": {},
                    "models.model.generations.generation.modifications.modification.model": {},
                    "models.model.generations.generation.modifications.modification.coupe": {},
                    "models.model.generations.generation.modifications.modification.engine": {},
                    "models.model.generations.generation.modifications.modification.productionyears": {},
                    "models.model.generations.generation.generationyears": {}
                }
            }
        }

        response = {
            'results': []
        }

        try:
            res = es.search(index="car_information", body=query_body)
        except Exception as e:
            logger.error(e)
            response['code'] = 500
            response['message'] = 'Error occurred while querying'
            return response

        hits = res['hits']['hits']

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
                                                data = {}
                                                data_available = False
                                                if 'generationyears' in gn:
                                                    data['generationyears'] = ''.join(
                                                        gn['generationyears'])
                                                    data_available = True

                                                if 'modifications' in gn:
                                                    for ms in gn['modifications']:
                                                        for m in ms.values():
                                                            for modification in m:
                                                                if 'brand' in modification:
                                                                    data['brand'] = ''.join(
                                                                        modification['brand'])
                                                                    data_available = True
                                                                if 'coupe' in modification:
                                                                    data['coupe'] = ''.join(
                                                                        modification['coupe'])
                                                                    data_available = True
                                                                if 'model' in modification:
                                                                    data['model'] = ''.join(
                                                                        modification['model'])
                                                                    data_available = True
                                                                if 'generation' in modification:
                                                                    data['generation'] = ''.join(
                                                                        modification['generation'])
                                                                    data_available = True
                                                                if 'engine' in modification:
                                                                    data['engine'] = ''.join(
                                                                        modification['engine'])
                                                                    data_available = True
                                                                if 'productionyears' in modification:
                                                                    data['productionyears'] = ''.join(
                                                                        modification['productionyears'])
                                                                    data_available = True

                                                if data_available:
                                                    response['results'].append(
                                                        data)

        response['total'] = len(response['results'])
        logger.debug("total hits at: %s is %s", time, response['total'])
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
                "models.model.generations.generation.modifications.modification.productionyears",
                "models.model.generations.generation.generationyears"
            ],
            "_source": False
        }
        response = {}
        try:
            res = es.search(index="car_information", body=query_body)
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
                                                                    'generation': None,
                                                                    'productionyears': None,
                                                                }
                                                                data['generationyears'] = generationyears
                                                                if 'brand' in modification:
                                                                    data['brand'] = ''.join(
                                                                        modification['brand'])
                                                                if 'coupe' in modification:
                                                                    data['coupe'] = ''.join(
                                                                        modification['coupe'])
                                                                if 'model' in modification:
                                                                    data['model'] = ''.join(
                                                                        modification['model'])
                                                                if 'generation' in modification:
                                                                    data['generation'] = ''.join(
                                                                        modification['generation'])
                                                                if 'engine' in modification:
                                                                    data['engine'] = ''.join(
                                                                        modification['engine'])
                                                                if 'productionyears' in modification:
                                                                    data['productionyears'] = ''.join(
                                                                        modification['productionyears'])

                                                                list.append(
                                                                    data)
        if list is not None and len(list) > 0:
            helpers.bulk(es, list, index='car_search_data')
        return response


blueprint = Blueprint('api', __name__)
api.init_app(blueprint)
api.add_namespace(ns)
app.register_blueprint(blueprint)

if __name__ == '__main__':
    app.run(host='0.0.0.0' , port=4928, debug=False)