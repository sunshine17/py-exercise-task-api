#!/bin/sh
export FLASK_APP=./task-api/task.py
#export FLASK_APP=./task/index.py
source $(pipenv --venv)/bin/activate
flask run -h 0.0.0.0
