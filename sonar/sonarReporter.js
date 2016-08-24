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

request(params.sonarApi
	+ "?metrics=ncloc,coverage,comment_lines_density,public_documented_api_density,"
	+ "violations_density,coverage,tests,test_execution_time,test_errors,test_failures,"
	+ "test_success_density,duplicated_lines_density,package_tangle_index"
	+ "&format=json", 
	function(error, response, body){
		var sonarData = JSON.parse(body);

		var client = new elasticsearch.Client({
			host: params.elasticsearch.host,
			log: 'trace'
		});
		
		var bulkInsert = [];
		var processDate = new Date().toISOString();


		for(var i = 0; i < sonarData.length; i ++){
			sonarData[i].metrics = {};

			for(var j = 0; j < sonarData[i].msr.length; j++){
				sonarData[i].metrics[sonarData[i].msr[j].key] = sonarData[i].msr[j].val;
			}
			
			sonarData[i].msr = null
			sonarData[i]["process_date"] = processDate;
			
			bulkInsert.push({ index:  { _index: params.elasticsearch.index, _type: params.elasticsearch.type} });
			bulkInsert.push(sonarData[i]);
		}

		client.bulk({body:bulkInsert}, function (error) {
			if (error) {
				console.trace('elasticsearch cluster is down!');
			} else {
				console.log('All is well');
			}
		});
	}
);