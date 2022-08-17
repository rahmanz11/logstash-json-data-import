from elasticsearch import Elasticsearch, helpers
import json

es = Elasticsearch(['http://95.179.199.14:9200'], basic_auth=('elastic', 'ksk3WMVlUlKXfm8pKXNP'))
import json
  
# Opening JSON file
f = open('data.json', encoding="utf8")
  
# returns JSON object as a dictionary
data = json.load(f)

# Closing file
f.close()

# Get the brands
brands = data['brands']['brand']

if brands is not None:
    # Insert the docs in bulk in elasticsearch
    helpers.bulk(es, brands, index='car-brands')
