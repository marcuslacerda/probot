## Reference:
## http://jakeaustwick.me/python-web-scraping-resource/#commonproblems
## http://docs.python-requests.org/en/master/user/advanced/

import requests
import sys  
import urlparse
from lxml import html
from requests.auth import HTTPBasicAuth

username = raw_input("Enter Username for basic auth. Default mlacerda: ") or "mlacerda"
password = raw_input("Enter Password.")
string_input = raw_input("Enter list of cities ids. Default BH,CPS,SP,RJ,HOU,NJ,NGB => ") or "BH,CPS,SP,RJ,HOU,NJ,NGB"

def dumpImage(login):
	response = requests.get(url='https://people.cit.com.br/profile/' + login, auth=HTTPBasicAuth(username, password))

	# Response
	print response.status_code # Response Code  

	parsed_body = html.fromstring(response.text)

	# Grab links to all images
	images = parsed_body.xpath('.//div[@class="container"]/div[@class="photo"]/img/@src')

	if not images:  
	    sys.exit("Found No Images")

	# Convert any relative urls to absolute urls
	images = [urlparse.urljoin(response.url, url) for url in images]  
	print 'Found %s images' % len(images)

	# Only download first 10
	for url in images[0:10]:  
	    r = requests.get(url, auth=HTTPBasicAuth(username, password))
	    f = open('downloaded_images/%s' % url.split('/')[-1], 'w')
	    f.write(r.content)
	    f.close()


for city_id in string_input.split(",") :
	## Reference:
	## http://jakeaustwick.me/python-web-scraping-resource/#commonproblems

	url = 'https://people.cit.com.br/search/json/?q='+ city_id
	print url

	response = requests.get(url=url, auth=HTTPBasicAuth(username, password))

	# Response
	print response.status_code # Response Code  
	print response.headers # Response Headers  
	# print response.content # Response Body Content

	# Request
	print response.request.headers

    # curl -XPUT -H --silent "Content-Type: application/json" --data @people_template.json http://localhost:9200/_template/people

	data = response.json();

	for hit in data['data'] :
		login = hit[1];
		print login
		dumpImage(login)



