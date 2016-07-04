
HOST=${1-"http://41ef204124da40f253e0872beb39e886.us-east-1.aws.found.io:9200"}
echo "Host -> $HOST"

curl -XPUT -H --silent "Content-Type: application/json" --data @people-template.json $HOST/_template/people --user admin:admin123 

#curl -XDELETE $HOST/people --user admin:admin123
#curl -XDELETE $HOST/people_bp --user admin:admin123
#curl -XDELETE $HOST/tech-team --user admin:admin123