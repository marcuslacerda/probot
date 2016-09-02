import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth
from elasticsearch import Elasticsearch

import urlparse
from lxml import html

username = raw_input("Enter Username for basic auth. Default mlacerda => ") or "mlacerda"
password = raw_input("Enter Password. => ")
string_input = raw_input("Enter list of cities ids. Default BH,CPS,SP,RJ,HOU,NJ,NGB,ATL,CAL => ") or "BH,CPS,SP,RJ,HOU,NJ,NGB,ATL,CAL"

def loadPeople(type, *login):
	try:
		resp = es_target.get(index="people", doc_type="login", id=login)
		return resp['_source']
	except Exception, e:
		print ("exception %s : " % e)

## Insert documentos to target elasticsearch
es_target = Elasticsearch(
    ['http://4c9752a7100ba7cb95034a4d458e17f6.sa-east-1.aws.found.io:9200'],
    http_auth=('admin', 'admin')
)

for city_id in string_input.split(",") :
	## Reference:
	## http://jakeaustwick.me/python-web-scraping-resource/#commonproblems

	url = 'https://people.cit.com.br/search/json/?q='+ city_id
	print url

	response = requests.get(url=url, auth=HTTPBasicAuth(username, password))

	data = response.json();

	for hit in data['data'] :
		print ("login %s" % hit[1])
		doc = {
	       'name' : hit[0],
	       'login': hit[1],
	       'role' : hit[4],
	       'coach' : loadPeople("coach", hit[5]),
	       'manager' : loadPeople("manager", hit[6]),
	       'city' : hit[7]
			}
		#print doc
		## create index doc
		res = es_target.index(index="coach", doc_type="login", body=doc, id=hit[1])
		print("Created documento ID %s para %s" % (res['_id'], hit[0]))