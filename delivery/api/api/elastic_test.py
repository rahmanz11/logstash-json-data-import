from elasticsearch import Elasticsearch
from config.config_handling import get_config_value


def connect_elasticsearch(**kwargs):
    _es_host = get_config_value('elastic', 'es_host')
    _es_user = get_config_value('elastic', 'es_user')
    _es_secret = get_config_value('elastic', 'es_secret')
    _es_port = get_config_value('elastic', 'es_port')
    _es_config = ['http://' + _es_user + ':' + _es_secret + '@' + _es_host + ':' + _es_port + '/']
    _es_obj = None
    _es_obj = Elasticsearch(_es_config, timeout=10)
    if _es_obj.ping():
        print('Connected to Elasticsearch!')
    else:
        print('Could not connect to Elasticsearch!')
    return _es_obj

es = connect_elasticsearch()
