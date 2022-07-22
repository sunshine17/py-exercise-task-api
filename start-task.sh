#!/bin/sh
pipenv install
export FLASK_APP=./app/task.py
export FLASK_ENV=development
#export FLASK_APP=./task/index.py
source $(pipenv --venv)/bin/activate
flask run -h 0.0.0.0 -p 5100
