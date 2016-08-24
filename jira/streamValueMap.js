#!/usr/bin/env node
var request = require('request');
var elasticsearch = require('elasticsearch');
var program = require('commander');
var fs = require('fs');


program
	.version('0.0.1')
	.usage('[options] executa coleta de informações do jira, e organiza a mesma para montagem da ')
	.option('-c, --config [type]', 'arquivo de configuracao')
	.parse(process.argv);


if(!program.config){
	console.log("Para utilizar o script é necessário informar o arquivo de configuração com -c ou --config e o endereço relativo do arquivo")
	process.exit(1);
}

var params = JSON.parse(fs.readFileSync(program.config, 'utf8'));
params.url = params.gateway + "/rest/api/2/search?jql=" + params.jql 
                                    + "&startAt=" + params.startAt 
                                    + "&maxResults=" + params.maxResults
                                    + "&expand=changelog";

var d1 = new Date();

console.log("Enviando requisição ao Jira: " + params.url);

var options = {
  "rejectUnauthorized": false,
  "url": params.url,
  "headers": params.headers
};

function callback(error, response, body) {

  console.log("Processando resposta ...");

  if (!error && response.statusCode == 200) {
    var result = JSON.parse(body);
    var rowData = new Array();
    var processDate = new Date().toISOString();
    var bulkInsert = [];
    var client = new elasticsearch.Client({
			host: params.elasticsearch.host,
			log: 'trace'
		});

    var elements = [];
    // itera na lista de itens retornados pelo Jira
    for(var i = 0; i < result.issues.length; i++){  
      var issue = result.issues[i];
      var lastStatus = "Open";
      var startDate = issue.fields.created;
      console.log("Processando jira: " + issue.key);


      for(var h = 0; h < issue.changelog.histories.length; h++){ 
        var history = issue.changelog.histories[h];

        for(var t = 0; t < history.items.length; t++){ 
          var item = history.items[t];
          
          if(item.field == "status"){
            var jiraObject = {}

            //coloca a informação de data inicial
            for( var j = 0; j < params.keys.length; j++){
                jiraObject[params.keys[j]] = eval(params.config[params.keys[j]]);
            }
            
            jiraObject["process_date"] = processDate;
            jiraObject.startDate = startDate;
            jiraObject.endDate = history.created;
            
            var start = new Date(jiraObject.startDate);
            var end = new Date(jiraObject.endDate);

            jiraObject.streamTimeMin = (end - start)/(1000*60);
            jiraObject.streamTimeHours = (end - start)/(1000*3600);
            jiraObject.streamItem = item.fromString;
            lastStatus = item.toString;
            startDate = jiraObject.endDate;
            elements.push(jiraObject);
          }
        }
      }

      // push do ultimo elemento
      var jiraObject = {};
      jiraObject["process_date"] = processDate;

      //coloca a informação de data inicial
      jiraObject.startDate = startDate;

      for( var j = 0; j < params.keys.length; j++){
          jiraObject[params.keys[j]] = eval(params.config[params.keys[j]]);
      }
      
      if(lastStatus == "Closed" || lastStatus == "Cancelled"){
        jiraObject.streamTimeMin = 0;
        jiraObject.streamTimeHours = 0;
        jiraObject.endDate = jiraObject.startDate;
      } else {
        jiraObject.endDate = issue.fields.updated;
        jiraObject.streamTimeMin = (new Date(jiraObject.endDate) - new Date(jiraObject.startDate))/(1000*60);
        jiraObject.streamTimeHours = (new Date(jiraObject.endDate) - new Date(jiraObject.startDate))/(1000*3600);
      }

      jiraObject.streamItem = lastStatus;
      elements.push(jiraObject);
    }

    for(var i = 0; i < elements.length; i ++){
      bulkInsert.push({ 
        index:  { 
          _index: params.elasticsearch.index, 
          _type: params.elasticsearch.type, 
          _id: elements[i].jira+elements[i].streamItem
        }
      });
      bulkInsert.push(elements[i]);
    }

    console.log("Enviando informações ao Elasticsearch");

    client.bulk({body:bulkInsert}, function (error) {
      if (error) {
        console.trace('elasticsearch cluster is down!');
      } else {
        console.log('All is well');
        console.log("Done in: " + ((new Date() - d1)/1000) + " segundos")
      }
    });

  } else {
    console.log("response.statusCode=" + response.statusCode);
  	console.log("Ocorreu um erro ao realizar a solicitação no jira.");
  }
}

request(options, callback);