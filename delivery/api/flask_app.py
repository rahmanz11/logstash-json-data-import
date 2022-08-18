from flask import Flask
from api.elastic_test import connect_elasticsearch

es = connect_elasticsearch()

app = Flask(__name__)

from api.get_result import *

if __name__ == '__main__':
    app.run(host='0.0.0.0' , port=4928)