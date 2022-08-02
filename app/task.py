from flask_restful import Api
from flask import Flask
from marshmallow import ( ValidationError,)

import logging
logging.basicConfig(filename="/tmp/task-app.log",
	format='%(asctime)s`%(name)s`%(levelname)s`%(message)s',
	filemode='w',
	level=logging.DEBUG
)

from app.models import (
    create_tables,
)

app = Flask(__name__)
api = Api(app)

from app.resources import (
    TaskListAPI,
    TaskAPI,
    TaskToggleAPI,
)

api.add_resource(TaskListAPI, 
    '/tasks', 
    '/tasks/expire-in-days/<int:exp_days>'
)

api.add_resource(TaskAPI, 
    '/task',
    '/task/<int:id>',
)

api.add_resource(TaskToggleAPI, 
    '/task/<int:id>/toggle',
)

if __name__ == "__main__":
    create_tables()
    app.run(port=5100, debug=True)
