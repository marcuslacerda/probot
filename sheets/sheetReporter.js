#!/usr/bin/env node
var request = require('request');
var elasticsearch = require('elasticsearch');
var program = require('commander');
var fs = require('fs');
var readline = require('readline');
var google = require('googleapis');
var googleAuth = require('google-auth-library');

program
	.version('0.0.1')
	.usage('[options] executa coleta de informações de uma planilha do google')
	.option('-c, --config [type]', 'arquivo de configuracao')
	.parse(process.argv);

if(!program.config){
	console.log("Para utilizar o script é necessário informar o arquivo de configuração com -c ou --config e o endereço relativo do arquivo")
	process.exit(1);
}

var params = JSON.parse(fs.readFileSync(program.config, 'utf8'));

// If modifying these scopes, delete your previously saved credentials
// at ~/.credentials/sheets.googleapis.com-nodejs-quickstart.json
var SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly'];
var TOKEN_DIR = (process.env.HOME || process.env.HOMEPATH ||
    process.env.USERPROFILE) + '/.credentials/';
var TOKEN_PATH = TOKEN_DIR + 'sheets.googleapis.com-nodejs-quickstart.json';

// Load client secrets from a local file.
fs.readFile('client_secret.json', function processClientSecrets(err, content) {
  if (err) {
    console.log('Error loading client secret file: ' + err);
    return;
  }
  // Authorize a client with the loaded credentials, then call the
  // Google Sheets API.
  authorize(JSON.parse(content), importSheet);
});

/**
 * Create an OAuth2 client with the given credentials, and then execute the
 * given callback function.
 *
 * @param {Object} credentials The authorization client credentials.
 * @param {function} callback The callback to call with the authorized client.
 */
function authorize(credentials, callback) {
  var clientSecret = credentials.installed.client_secret;
  var clientId = credentials.installed.client_id;
  var redirectUrl = credentials.installed.redirect_uris[0];
  var auth = new googleAuth();
  var oauth2Client = new auth.OAuth2(clientId, clientSecret, redirectUrl);

  // Check if we have previously stored a token.
  fs.readFile(TOKEN_PATH, function(err, token) {
    if (err) {
      getNewToken(oauth2Client, callback);
    } else {
      oauth2Client.credentials = JSON.parse(token);
      callback(oauth2Client);
    }
  });
}

/**
 * Get and store new token after prompting for user authorization, and then
 * execute the given callback with the authorized OAuth2 client.
 *
 * @param {google.auth.OAuth2} oauth2Client The OAuth2 client to get token for.
 * @param {getEventsCallback} callback The callback to call with the authorized
 *     client.
 */
function getNewToken(oauth2Client, callback) {
  var authUrl = oauth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES
  });
  console.log('Authorize this app by visiting this url: ', authUrl);
  var rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  rl.question('Enter the code from that page here: ', function(code) {
    rl.close();
    oauth2Client.getToken(code, function(err, token) {
      if (err) {
        console.log('Error while trying to retrieve access token', err);
        return;
      }
      oauth2Client.credentials = token;
      storeToken(token);
      callback(oauth2Client);
    });
  });
}

/**
 * Store token to disk be used in later program executions.
 *
 * @param {Object} token The token to store to disk.
 */
function storeToken(token) {
  try {
    fs.mkdirSync(TOKEN_DIR);
  } catch (err) {
    if (err.code != 'EEXIST') {
      throw err;
    }
  }
  fs.writeFile(TOKEN_PATH, JSON.stringify(token));
  console.log('Token stored to ' + TOKEN_PATH);
}

/**
 * Import all skills in the tech skill managment spreadsheet
 */
function importSheet(auth) {
  var sheets = google.sheets('v4');
  sheets.spreadsheets.values.get({
    auth: auth,
    spreadsheetId: params.sheetId,
    range: params.skillRange,
  }, function(err, response) {
    if (err) {
      console.log('The API returned an error: ' + err);
      return;
    }
    var rows = response.values;
    if (rows.length == 0) {
      console.log('No data found.');
    } else {
		var processDate = new Date().toISOString();
		var bulkInsert = [];
		for (var i = 0; i < rows.length; i++) {
			var row = rows[i];

			var sheetData = {};
			for(var j = 0; j < params.fields.length; j++){
				sheetData[params.fields[j]] = row[j];
			}
			sheetData["process_date"] = processDate;

			if(params.idExpression != undefined){
				bulkInsert.push({ index:  { 
					_index: params.elasticsearch.index,
				 	_type: params.elasticsearch.type,
				 	_id: eval(params.idExpression),
				}});
			} else {
				bulkInsert.push({ index:  { 
					_index: params.elasticsearch.index,
				 	_type: params.elasticsearch.type
				}});
			}
			bulkInsert.push(sheetData);
		}

		var client = new elasticsearch.Client({
			host: params.elasticsearch.host,
			log: 'trace'
		});

		client.bulk({body:bulkInsert}, function (error) {
			if (error) {
				console.trace('elasticsearch cluster is down!');
			} else {
				console.log('All is well');
			}
		});
    }
  });
}


/**
 * Import all skills in the tech skill managment spreadsheet
 */
function importSPDex(auth) {
  var sheets = google.sheets('v4');
  sheets.spreadsheets.values.get({
    auth: auth,
    spreadsheetId: params.sheetId,
    range: params.spdexType,
  }, function(err, response) {
    if (err) {
      console.log('The API returned an error: ' + err);
      return;
    }
    var rows = response.values;
    if (rows.length == 0) {
      console.log('No data found.');
    } else {
		var processDate = new Date().toISOString();
		var bulkInsert = [];
		for (var i = 0; i < rows.length; i++) {
			var row = rows[i];

			var sheetData = {};

			sheetData.login = row[0];
			sheetData.tech = row[1];
			sheetData.skillLevel = parseInt(row[2]);
			sheetData.endorsementsCount = parseInt(row[3]);
			sheetData["process_date"] = processDate;

			bulkInsert.push({ index:  { _index: params.elasticsearch.index, _type: params.elasticsearch.skillType} });
			bulkInsert.push(sheetData);
		}

		var client = new elasticsearch.Client({
			host: params.elasticsearch.host,
			log: 'trace'
		});

		client.bulk({body:bulkInsert}, function (error) {
			if (error) {
				console.trace('elasticsearch cluster is down!');
			} else {
				console.log('All is well');
			}
		});
    }
  });
}