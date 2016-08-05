import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth
from elasticsearch import Elasticsearch

import urlparse
from lxml import html

username = raw_input("Enter Username for basic auth. Default mlacerda => ") or "mlacerda"
password = raw_input("Enter Password. => ")
string_input = raw_input("Enter list of cities ids. Default BH,CPS,SP,RJ,HOU,NJ,NGB => ") or "BH,CPS,SP,RJ,HOU,NJ,NGB"

def loadTechnologies(login):
	url = 'https://tech-gallery.appspot.com/_ah/api/rest/v1/profile?email='+ login + '@ciandt.com'
	#print url

	response = requests.get(url=url)

	# Response
	#print response.status_code # Response Code  
	# print response.content

	return response;


## Insert documentos to target elasticsearch
es_target = Elasticsearch(
    ['http://104.197.92.45:9200'],
    http_auth=('witix', 'witix'),
    port=9200
)


for city_id in string_input.split(",") :
	## Reference:
	## http://jakeaustwick.me/python-web-scraping-resource/#commonproblems

	url = 'https://people.cit.com.br/search/json/?q='+ city_id
	response = requests.get(url=url, auth=HTTPBasicAuth(username, password)) 

    # curl -XPUT -H --silent "Content-Type: application/json" --data @people_template.json http://localhost:9200/_template/people

	data = response.json();

	for hit in data['data'] :
		print("Loading technologies for %s" % hit[1])

		response = loadTechnologies(hit[1])
		techs = response.json()

		if response.status_code != 200:
			print ("%s not has login on Tech Gallery" % hit[1])
			continue

		#docs = []

		if 'technologies' in techs:
			for tech in techs['technologies'] :
				doc = {
				   'id' : tech['technologyName']+hit[1],
			       'name' : hit[0],
			       'login': hit[1],
			       'role' : hit[4],
			       'city' : hit[7],
			       'technologyName': tech['technologyName'],
			       'endorsementsCount' : tech['endorsementsCount'],
			       'skillLevel' : tech['skillLevel'],
			       'load_date': datetime.now()
					}
				# bulk insert doc
				#print doc
				#docs.append(doc)
				#res = es_target.bulk(index="tc", doc_type="skill", body=doc, id_field='id', parent_field='_parent')
				#print("Bulk index " % res)
				
				## create index doc
				res = es_target.index(index="tc", doc_type="skill", body=doc)
				print("Created documento ID %s para %s " % (res['_id'], tech['technologyName']))