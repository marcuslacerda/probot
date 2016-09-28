from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

from elasticsearch import Elasticsearch

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'

global TOTAL_ERRS
TOTAL_ERRS = 0

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


# return float number. if exists ',' character, it will be change to '.'' 
def formatFloat(value):
    if value.find(',') == -1: 
        # convert string br to float
        return float(value) 
    else:
        return float(value.replace(',','.'))

def findSpreadsheetIds():
  try:
    resp = es.search(index="project", doc_type="settings", body={"query": {"match_all": {}}}, size=2500)
    print("%d documents found" % resp['hits']['total'])

    global TOTAL_HITS
    TOTAL_HITS = resp['hits']['total']

    return resp['hits']['hits']
  except Exception, e:
    print ("exception %s : " % e)


## Insert documentos to target elasticsearch
es = Elasticsearch(
    ['http://104.197.92.45:9200']
)
        
# https://developers.google.com/sheets/reference/rest/v4/spreadsheets/get
def main():
    """Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints lines of a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1uzyIZf2r3DLKptr8ikeym1NNwiav-BwmtX3qbtDzhA4/edit
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

#    spreadsheetIds = '1uzyIZf2r3DLKptr8ikeym1NNwiav-BwmtX3qbtDzhA4,1bPKnCx9nhcpEHoY9iMsW3LSDe5cORlkV2eLmHr6Wl5Y'
#    spreadsheets = spreadsheetIds.split(',')

    spreadsheets = findSpreadsheetIds()

    for item in spreadsheets:
        spreadsheetId = item['_source']['sheet_id']
        print ('processing spreadsheet: %s ' % spreadsheetId) 
        rangeName = 'TC_Report!A2:K'

        values = []
        try:
          result = service.spreadsheets().values().get(
              spreadsheetId=spreadsheetId, range=rangeName).execute()
          values = result.get('values', [])          

          if not values:
              print('No data found.')
          else:
              items = readSheetData(spreadsheetId, values)
              print(' %s technologies on this spreadsheet ' % len(items))

              q = "sheet_id:"+spreadsheetId
              delete_docs(q)

              pushDataToElasticsearch(items)
        except Exception, e:
          print ("exception %s : " % e)
          global TOTAL_ERRS
          TOTAL_ERRS = TOTAL_ERRS + 1


def readSheetData(spreadsheetId, values):
    items = []
    for row in values:
      # Print columns A and E, which correspond to indices 0 and 4.
      doc = {
         'technology': row[0],
         'tower': row[1],            
         'contract': row[2],
         'flow': row[3],
         'gap': row[4],
         'weight': row[5],
         'necessity': row[6],
         'requirement': row[7],
         'relevancy': formatFloat(row[8]),
         'skill_index': formatFloat(row[9]),
         'achieve': row[10],
         'sheet_id': spreadsheetId
      }
      items.append(doc)
    return items


def pushDataToElasticsearch(documents):
    for doc in documents:     
      ## create index doc
      res = es.index(index="knowledge", doc_type="tech", body=doc)
      
 
def delete_docs(search, number=10):   
  
  # Start the initial search. 
  hits=es.search(
    q=search,
    index="*knowledge",
    fields="_id",
    size=number,
    search_type="scan",
    scroll='5m',
  )
  print ('DELETE %s ' % hits['hits']['total'])
  # Now remove the results. 
  while True:
    try: 
      # Git the next page of results. 
      scroll=es.scroll( scroll_id=hits['_scroll_id'], scroll='5m', )

      # We have results initialize the bulk variable. 
      bulk = ""
      
      # Remove the variables. 
      for result in scroll['hits']['hits']:
        bulk = bulk + '{ "delete" : { "_index" : "' + str(result['_index']) + '", "_type" : "' + str(result['_type']) + '", "_id" : "' + str(result['_id']) + '" } }\n'
      
      es.bulk( body=bulk )

    except Exception, e: 
      break 
    

if __name__ == '__main__':
    main()
    print ('%s spreadsheets with %s errors' % (TOTAL_HITS, TOTAL_ERRS))