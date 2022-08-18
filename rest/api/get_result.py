from flask_app import app
from api.elastic_test import connect_elasticsearch
from flask import jsonify, request

es = connect_elasticsearch()

@app.route('/search', methods=['GET'])
def search_user():
    keyword = request.form['keyword']
    query_body = {
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
        "highlight": {
            "fields": {
            "models.model.generations.generation.modifications.modification.generation": {},
            "models.model.generations.generation.modifications.modification.brand": {},
            "models.model.generations.generation.modifications.modification.model": {},
            "models.model.generations.generation.modifications.modification.coupe": {},
            "models.model.generations.generation.modifications.modification.engine": {}
            }
        }
    }

    res = es.search(index="car_information", body=query_body)

    return jsonify(res['hits']['hits'])