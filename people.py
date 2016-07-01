import requests
import sys  
import urlparse
from lxml import html
from requests.auth import HTTPBasicAuth

username = raw_input("Enter Username for basic auth. Default mlacerda: ") or "mlacerda"
password = raw_input("Enter Password.")
string_input = raw_input("Enter list of people ids ")

for people_id in string_input.split(",") :
	## Reference:
	## http://jakeaustwick.me/python-web-scraping-resource/#commonproblems

	url = 'https://people.cit.com.br/profile/'+ people_id
	print url

	response = requests.get(url=url, auth=HTTPBasicAuth(username, password))

	# Response
	print response.status_code # Response Code  
	print response.headers # Response Headers  
	# print response.content # Response Body Content

	# Request
	print response.request.headers

	parsed_body = html.fromstring(response.text)
	for atag in  parsed_body.xpath('.//div[@class="user-projects"]//ul//li[1]//a') : # Get href attribute of all links 
		print(atag.text_content())
