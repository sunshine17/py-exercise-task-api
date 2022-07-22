DUE_DATE_NOW="$(date --iso-8601=seconds)"
#DUE_DATE_NOW="$(date)"
#DUE_DATE_NOW="05/06/2019 14:33:01"

echo "=== 1. GET lst: \n"
curl http://localhost:5100/tasks

echo "=== 2. POST \n"
curl -X POST -H "Content-Type: application/json" -d '{
    "title": "task-1",
    "due_date": "'"$DUE_DATE_NOW"'"
}' http://localhost:5100/task 


#echo "=== 3. PUT \n"
#curl -X PUT -H "Content-Type: application/json" -d '{
#    "title": "task-1",
#    "due_date": "'"$DUE_DATE_NOW"'"
#}' http://localhost:5100/task/1

#echo "=== 4. POST toggle \n"
#curl -X POST -H "Content-Type: application/json" -d '{}' http://localhost:5100/task/1/toggle 
