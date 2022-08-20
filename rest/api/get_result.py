from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
from api.elastic_test import connect_elasticsearch
from flask import request
from flask_app import ns, api, logger
from flask_restx import Resource, fields
from flask import Flask, Blueprint
from flask_restx import Api
from api.elastic_test import connect_elasticsearch

request_schema = api.model('Search Request Body', {
    'keyword': fields.String(readOnly=True, description='keyword')
})

search_result = {
    'generationyears': fields.String(readOnly=True, description='generationyears'),
    'brand': fields.String(readOnly=True, description='brand'),
    'coupe': fields.String(readOnly=True, description='coupe'),
    'model': fields.String(readOnly=True, description='model'),
    'generation': fields.String(readOnly=True, description='generation'),
    'engine': fields.String(readOnly=True, description='engine'),
    'productionyears': fields.String(readOnly=True, description='productionyears')
}

response_schema = api.model('Search Response Body', {
    'code': fields.Integer(readOnly=True, description='Response code'),
    'message': fields.String(readOnly=True, description='Response message'),
    'results': fields.List(fields.Nested(search_result)),
    'total': fields.Integer(readOnly=True, description='Total')
})

formatter = logging.Formatter(fmt='%(asctime)s %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger("Car Search Log")
logger.setLevel(logging.ERROR)

handler = TimedRotatingFileHandler('search.log',
                                    when="d",
                                    interval=1,
                                    backupCount=15)
handler.setFormatter(formatter)
logger.addHandler(handler)
es = connect_elasticsearch()

app = Flask(__name__)
api = Api(app)

es = connect_elasticsearch()
ns = api.namespace('car', description='Car Search API')

@ns.route('/search')
class GetSearchResult(Resource):
    @api.marshal_with(response_schema)
    @api.expect(request_schema)
    def post(self):
        keyword = request.json['keyword']
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
                                                    "models.model.generations.generation.modifications.modification.generation": keyword
                                                }
                                                },
                                                {
                                                "match": {
                                                    "models.model.generations.generation.modifications.modification.brand": keyword
                                                }
                                                },
                                                {
                                                "match": {
                                                    "models.model.generations.generation.modifications.modification.model": keyword
                                                }
                                                },
                                                {
                                                "match": {
                                                    "models.model.generations.generation.modifications.modification.coupe": keyword
                                                }
                                                },
                                                {
                                                "match": {
                                                    "models.model.generations.generation.modifications.modification.engine": keyword
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
            'code': 200,
            'message': '',
            'results': [],
            'total': 0
        }

        time = datetime.now()
        logger.debug("es query at %s: %s", time, query_body)
        try:
            res = es.search(index="car_information", body=query_body)
        except Exception as e:
            logger.error(e)
            response['code'] = 500
            response['message'] = 'Error occurred while querying'
            return response
        
        hits = res['hits']['hits']
        total_hits = len(hits)
        
        logger.debug("total hits at %s: %s", time, total_hits)

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
                                                    data['generationyears'] = gn['generationyears']
                                                    data_available = True
                                                    
                                                if 'modifications' in gn:
                                                    for ms in gn['modifications']:
                                                        for m in ms.values():
                                                            for modification in m:
                                                                if 'brand' in modification:
                                                                    data['brand'] = modification['brand']
                                                                    data_available = True
                                                                if 'coupe' in modification:
                                                                    data['coupe'] = modification['coupe']
                                                                    data_available = True
                                                                if 'model' in modification:
                                                                    data['model'] = modification['model']
                                                                    data_available = True
                                                                if 'generation' in modification:
                                                                    data['generation'] = modification['generation']
                                                                    data_available = True
                                                                if 'engine' in modification:
                                                                    data['engine'] = modification['engine']
                                                                    data_available = True
                                                                if 'productionyears' in modification:
                                                                    data['productionyears'] = modification['productionyears']
                                                                    data_available = True
                                                            
                                                
                                                if data_available:
                                                    response["results"].append(data)

        return response

@ns.route('/reindex')
class ReIndex(Resource):
    def post(self):
        query_body = {
            "size": 100000,
            "query": {
                "match_all": {
                }
            }
        }
        response = {
            'code': 200,
            'message': '',
            'results': [],
            'total': 0
        }

        time = datetime.now()
        logger.debug("es query at %s: %s", time, query_body)
        try:
            res = es.search(index="car_information", body=query_body)
        except Exception as e:
            logger.error(e)
            response['code'] = 500
            response['message'] = 'Error occurred while querying'
            return response
        
        hits = res['hits']['hits']
        total_hits = len(hits)
        
        logger.debug("total hits at %s: %s", time, total_hits)

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
                                                    data['generationyears'] = gn['generationyears']
                                                    data_available = True
                                                    
                                                if 'modifications' in gn:
                                                    for ms in gn['modifications']:
                                                        for m in ms.values():
                                                            for modification in m:
                                                                if 'brand' in modification:
                                                                    data['brand'] = modification['brand']
                                                                    data_available = True
                                                                if 'coupe' in modification:
                                                                    data['coupe'] = modification['coupe']
                                                                    data_available = True
                                                                if 'model' in modification:
                                                                    data['model'] = modification['model']
                                                                    data_available = True
                                                                if 'generation' in modification:
                                                                    data['generation'] = modification['generation']
                                                                    data_available = True
                                                                if 'engine' in modification:
                                                                    data['engine'] = modification['engine']
                                                                    data_available = True
                                                                if 'productionyears' in modification:
                                                                    data['productionyears'] = modification['productionyears']
                                                                    data_available = True
                                                            
                                                
                                                if data_available:
                                                    response["results"].append(data)

        return response

blueprint = Blueprint('api', __name__)
api.init_app(blueprint)
api.add_namespace(ns)
app.register_blueprint(blueprint)


if __name__ == '__main__':
    app.run()