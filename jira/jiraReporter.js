#!/usr/bin/env node
var request = require('request');
var elasticsearch = require('elasticsearch');
var program = require('commander');
var fs = require('fs');


program
	.version('0.0.1')
	.usage('[options] executa coleta de informações do jira respeitando as informações lidas na configuracao')
	.option('-c, --config [type]', 'arquivo de configuracao')
	.parse(process.argv);


if(!program.config){
	console.log("Para utilizar o script é necessário informar o arquivo de configuração com -c ou --config e o endereço relativo do arquivo")
	process.exit(1);
}

var params = JSON.parse(fs.readFileSync(program.config, 'utf8'));
params.url = params.gateway + "/rest/api/2/search?jql=" + params.jql 
                                    + "&startAt=" + params.startAt 
                                    + "&maxResults=" + params.maxResults;

var options = {
  "rejectUnauthorized": false,
  "url": params.url,
  "headers": params.headers
};

function callback(error, response, body) {
  if (!error && response.statusCode == 200) {
    var result = JSON.parse(body);
    var rowData = new Array();
    var processDate = new Date().toISOString();
    var bulkInsert = [];
    var client = new elasticsearch.Client({
			host: params.elasticsearch.host,
			log: 'trace'
		});

    // itera na lista de itens retornados pelo Jira
    for(var i = 0; i < result.issues.length; i++){  
      var issue = result.issues[i];
      var jiraObject = {}

      for( var j = 0; j < params.keys.length; j++){
      	  jiraObject[params.keys[j]] = eval(params.config[params.keys[j]]);
      }

      jiraObject["process_date"] = processDate;


      bulkInsert.push({ 
      	index:  { 
	      	_index: params.elasticsearch.index, 
	      	_type: params.elasticsearch.type, 
	      	_id: jiraObject.jira
      	}
      });
	  bulkInsert.push(jiraObject); 
    }

    client.bulk({body:bulkInsert}, function (error) {
			if (error) {
				console.trace('elasticsearch cluster is down!');
			} else {
				console.log('All is well');
			}
		});
  } else {
  	console.log(error);
  }
}

request(options, callback);