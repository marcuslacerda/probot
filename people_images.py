import requests
import sys  
import urlparse
from lxml import html
from requests.auth import HTTPBasicAuth

username = raw_input("Enter Username for basic auth. Default mlacerda: ") or "mlacerda"
password = raw_input("Enter Password.")

## Reference:
## http://jakeaustwick.me/python-web-scraping-resource/#commonproblems
## http://docs.python-requests.org/en/master/user/advanced/

response = requests.get(url='https://people.cit.com.br/profile/mlacerda', auth=HTTPBasicAuth(username, password))

# Response
print response.status_code # Response Code  
print response.headers # Response Headers  
# print response.content # Response Body Content

# Request
print response.request.headers

parsed_body = html.fromstring(response.text)
images = parsed_body.xpath('//img/@src')  

def downloadImgs (parsed_body)

	# Grab links to all images
	images = parsed_body.xpath('//img/@src')  
	if not images:  
	    sys.exit("Found No Images")

	# Convert any relative urls to absolute urls
	images = [urlparse.urljoin(response.url, url) for url in images]  
	print 'Found %s images' % len(images)

	# Only download first 10
	for url in images[0:10]:  
	    r = requests.get(url, auth=HTTPBasicAuth('mlacerda', 'Inovacao6'))
	    f = open('downloaded_images/%s' % url.split('/')[-1], 'w')
	    f.write(r.content)
	    f.close()

