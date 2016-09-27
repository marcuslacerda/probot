import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth
from elasticsearch import Elasticsearch

import urlparse
from lxml import html
import sys

username = raw_input("Enter Username for basic auth. Default mlacerda => ") or "mlacerda" or sys.argv[1]
password = raw_input("Enter Password. => ") or sys.argv[2]
#string_input = raw_input("Enter list of cities ids. Default BH,CPS,SP,RJ,HOU,NJ,NGB,ATL,CAL,TOK => ") or "BH,CPS,SP,RJ,HOU,NJ,NGB,ATL,CAL,TOK"

def loadProjectFromHtml(login):
	url = 'https://people.cit.com.br/profile/'+ login
	#print url

	response = requests.get(url=url, auth=HTTPBasicAuth(username, password))

	# Response
	#print response.status_code # Response Code  

	parsed_body = html.fromstring(response.text)
	elements =  parsed_body.xpath('.//div[@class="user-projects"]//ul//li[1]//a')
	
	if elements:
		project = elements[0]
		return project.text_content()
	return "Empty"

def loadAllPeople():
	headers = {'app_token': 'Blpy2nNXnjya'}
	url = 'https://wsgateway.cit.com.br/cit/api/v2/people/'
	#print url
	response = requests.get(url=url, headers=headers)
	
	print response.status_code
	#print response.headers

	return response.json()


def loadPeopleAPI(login):
	headers = {'app_token': 'Blpy2nNXnjya'}
	url = 'https://wsgateway.cit.com.br/cit/api/v2/people/'+ login
	#print url
	response = requests.get(url=url, headers=headers)
	
	print response.status_code
	#print response.headers

	return response.json()

## Insert documentos to target elasticsearch
es_target = Elasticsearch(
    ['http://104.197.92.45:9200'],
    http_auth=('admin', 'admin')
)

count = 0

#for city_id in string_input.split(",") :
	## Reference:
	## http://jakeaustwick.me/python-web-scraping-resource/#commonproblems

#	url = 'https://people.cit.com.br/search/json/?q='+ city_id
#	print url

#	response = requests.get(url=url, auth=HTTPBasicAuth(username, password))

#	data = response.json();

#	for hit in data['data'] :

data = loadAllPeople()

for hit in data:
	count = count + 1
	print ("Loading %s - %s  " % (hit['login'],count))
	project = loadProjectFromHtml(hit['login'])
	doc = {
       'name' : hit['name'],
       'login': hit['login'],
       'role' : hit['role'],
       'cityBase' : hit['cityBase'],
       'project': {
       		'code' : hit['project']['code'],
       		'name' : project
       },
       'area' : hit['area'],
       'company' : hit['company']
		}
	#print doc
	## create index doc
	res = es_target.index(index="people", doc_type="login", body=doc, id=hit['login'])
	print("Created documento ID %s para %s on %s" % (res['_id'], hit['login'], project))