
HOST=${1-"http://104.197.92.45:9200"}
echo "Host -> $HOST"

curl -XPUT -H --silent "Content-Type: application/json" --data @people-template.json $HOST/_template/people --user witix:witix

#curl -XDELETE $HOST/people --user admin:admin123
#curl -XDELETE $HOST/people_bp --user admin:admin123
#curl -XDELETE $HOST/tech-team --user admin:admin123