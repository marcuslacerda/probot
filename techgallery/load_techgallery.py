import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth
from elasticsearch import Elasticsearch

import urlparse
from lxml import html

username = raw_input("Enter Username for basic auth. Default admin => ") or "admin"
password = raw_input("Enter Password. Default admin => ") or "admin"

def loadTechnologies(login):
	url = 'https://tech-gallery.appspot.com/_ah/api/rest/v1/profile?email='+ login + '@ciandt.com'

	response = requests.get(url=url)

	return response;

def findPeople():
	try:
		resp = es_people.search(index="people", doc_type="login", body={"query": {"match_all": {}}}, size=2500)
		print("%d documents found" % resp['hits']['total'])

		return resp['hits']['hits']
	except Exception, e:
		print ("exception %s : " % e)

## Insert documentos to target elasticsearch
es_people = Elasticsearch(
    ['http://4c9752a7100ba7cb95034a4d458e17f6.sa-east-1.aws.found.io:9200'],
    http_auth=(username, password)
)

## Insert documentos to target elasticsearch
es_target = Elasticsearch(
    ['http://104.197.92.45:9200']
)


for item in findPeople():
	people = item['_source']

	response = loadTechnologies(people['login'])
	techs = response.json()

	if response.status_code != 200:
		print ("%s not has login on Tech Gallery" % people['login'])
		continue

	#docs = []

	if 'technologies' in techs:
		for tech in techs['technologies'] :
			doc = {
		       'login': people['login'],
		       'name' : people['name'],		       
		       'role' : people['role'],
		       'city' : people['city'],
		       'project' : people['contract'],
		       'technologyName': tech['technologyName'],
		       'endorsementsCount' : tech['endorsementsCount'],
		       'skillLevel' : tech['skillLevel']
				}
			# bulk insert doc
			#print doc
			#docs.append(doc)
			#res = es_target.bulk(index="tc", doc_type="skill", body=doc, id_field='id', parent_field='_parent')
			#print("Bulk index " % res)
			
			## create index doc
			res = es_target.index(index="skill", doc_type="technology", body=doc)
			print("Created documento ID %s para %s " % (res['_id'], tech['technologyName']))