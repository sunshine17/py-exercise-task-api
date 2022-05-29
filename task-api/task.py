import datetime as dt
from functools import wraps
from flask_restful import abort, Api, Resource 

from flask import Flask, request, g, jsonify
import peewee as pw
from marshmallow import (
    Schema,
    fields,
    validates,
    ValidationError,
)

import logging
 
# Create and configure logger
logging.basicConfig(filename="/tmp/task-app.log",
	format='%(asctime)s`%(name)s`%(levelname)s`%(message)s',
	filemode='w',
	level=logging.DEBUG
)
 
logger = logging.getLogger('__main__')
logger.setLevel(logging.DEBUG)

app = Flask(__name__)
api = Api(app)
db = pw.SqliteDatabase("/tmp/task.db")

###### MODELS #####

class BaseModel(pw.Model):
    """Base model class. All descendants share the same database."""

    class Meta:
        database = db


class Task(BaseModel):
    title = pw.TextField()
    due_date = pw.DateTimeField()
    is_done = pw.BooleanField(default=False)

    class Meta:
        order_by = ("-due_date",)


def create_tables():
    if db.is_closed:
        db.connect()
    Task.create_table()


Task.create_table()

##### SCHEMAS #####


DUE_DATE_FMT = "%d/%m/%Y"


class TaskSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    due_date = fields.DateTime(required=True)
    is_done = fields.Boolean(dump_default=False)

    @validates("due_date")
    def validate_date(self, val):
        if type(val) is dt.datetime:
            return True
        try:
            dt.datetime.strptime(val, DUE_DATE_FMT)
            return True
        except ValueError:
            return False

def task_to_model(dic):
    if not dic:
        return None

    logger.debug("TASK_TO_MODEL`typeof due_date={}".format(type(dic['due_date'])))
    ret = Task(
        title=dic['title'],
        due_date=dic['due_date'],
#        is_done=dic['is_done'],
    )
    if 'is_done' in dic:
        ret.is_done = dic['is_done']
    return ret


task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)


#### API #####

class TaskAPI(Resource):

    def get(self, id):
        try:
            task = Task.get(Task.id == id)
        except Task.DoesNotExist:
            abort(404, message="task {} doesn't exist".format(id))

        logger.debug("======GET`typeOf due_date in task: {}".format(type(task.due_date)))
        logger.debug(task.due_date)
        logger.debug(task.title)
        logger.debug(task.id)
        return task_schema.dump(task)

    def delete(self, id):
        q = Task.delete().where(Task.id == id)
        rows = q.execute()
        logger.info("TASK DELETED`id={id}`affected_rows={cnt}".format(id=id, cnt=rows))
        return 200

    def put(self, id):
        try:
            task = Task.get(Task.id == id)
        except Task.DoesNotExist:
            abort(404, message="task {} doesn't exist".format(id))

        json_input = request.get_json()
        try:
            input_dic = task_schema.load(json_input, partial=("title","due_date",))

            if 'title' not in input_dic and 'due_date' not in input_dic:
                abort(400, message="nothing to update")

            if 'title' in input_dic:
                task.title = input_dic['title']
            if 'due_date' in input_dic:
                i_due_date = input_dic['due_date']
                if type(i_due_date) is dt.datetime:
                    task.due_date = i_due_date
                else:
                    task.due_date = dt.datetime.strptime(i_due_date, DUE_DATE_FMT)

#                task.due_date = input_dic['due_date']
#                task.due_date = dt.datetime.strptime(input_dic['due_date'], DUE_DATE_FMT)
        except ValidationError as err:
            abort(400, message="input error")

        task.save()
        logger.info("TASK UPDATED`id={id},obj={dic}".format(id = id, dic = input_dic))
        return '', 204

    def post(self):
        json_input = request.get_json()
        try:
            task = task_to_model(task_schema.load(json_input))
        except ValidationError as err:
            return {"errors": err.messages, 'post': json_input}, 422
        task.save()
        logger.info("NEW TASK ADDED: {}".format(json_input))
        return task_schema.dump(task), 201

class TaskListAPI(Resource):
    def get(self, exp_days=None):
        if exp_days:
            return self._get_in_exp_days(exp_days)

        tasks = Task.select().order_by(Task.due_date.asc())

        logger.debug('======================== TASKS IN GET ')
        logger.debug(list(tasks))
        for i in list(tasks):
            logger.debug("TASK_ID={id}`DUE_DATE={due_date}".format(
                id=i.id, due_date=i.due_date))

        return tasks_schema.dump(list(tasks))

    def _get_in_exp_days(self, exp_days):
        tasks = Task.select().where(
                Task.due_date <= (dt.datetime.now() + dt.timedelta(days=exp_days))
                )
        return tasks_schema.dump(list(tasks))


class TaskToggleAPI(Resource):
    def put(self, id):
        try:
            task = Task.get(Task.id == id)
        except Task.DoesNotExist:
            abort(404, message="task {} doesn't exist".format(id))

        status = not task.is_done
        query = task.update(is_done=status)
        query.execute()
        logger.info("TASK TOGGLED`id={id},is_done={status}".format(id=id, status=status))
        return '', 200


api.add_resource(TaskListAPI, 
    '/tasks', 
    '/tasks/<int:exp_days>'
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
    app.run(port=5000, debug=True)
