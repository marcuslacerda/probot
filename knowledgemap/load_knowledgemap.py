from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

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
    # 
    if value.find(',') == -1: 
        # convert string br to float
        return float(value) 
    else:
        return float(value.replace(',','.'))
        
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

    spreadsheetIds = '1uzyIZf2r3DLKptr8ikeym1NNwiav-BwmtX3qbtDzhA4,1bPKnCx9nhcpEHoY9iMsW3LSDe5cORlkV2eLmHr6Wl5Y'

    for spreadsheetId in spreadsheetIds.split(','):
        print ('processing spreadsheet: %s ' % spreadsheetId) 
        rangeName = 'TC_Report!A2:K'
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheetId, range=rangeName).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
        else:
            print('Name, Major:')
            for row in values:
                # Print columns A and E, which correspond to indices 0 and 4.
                print('%s, %s' % (row[0], formatFloat(row[8])))

  #var flow = Elasticsearch.cleanUp(session.flow); 
  #Elasticsearch.deleteDataByQuery("knowledge", flow, {query : {match_all: {}}});
  #Elasticsearch.pushDataToCluster("knowledge", flow, "knowledge", sheet);

  #              doc = {
  #                 'technology': row[0],
  #                 'tower': row[1],            
  #                 'contract': row[2],
  #                 'flow': row[3],
  #                 'gap': row[4],
  #                 'weight' row[5]: ,
  #                 'necessity': row[6]
  #                 'requirement': row[7],
  #                 'relevancy': row[8],
  #                 'skill_index': row[9],
  #                 'achieve' row[10]: 
  #              }

 
if __name__ == '__main__':
    main()
    #print formatFloat('3,14')