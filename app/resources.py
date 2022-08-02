import datetime as dt
from flask_restful import abort, Api, Resource 
from flask import request

from app.models import (
    Task
)

from app.schemas import (
    DUE_DATE_FMT,
    task_schema,
    tasks_schema,
    task_to_model,
)

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class TaskAPI(Resource):

    def get(self, id=0):
        if id is 0:
            abort(400, message="need task id")
        try:
            task = Task.get(Task.id == id)
        except Task.DoesNotExist:
            abort(404, message="task {} doesn't exist".format(id))

        return task_schema.dumps(task)

    def delete(self, id):
        if id is 0:
            abort(400, message="need task id")
        q = Task.delete().where(Task.id == id)
        rows = q.execute()
        logger.info("TASK DELETED`id={id}`affected_rows={cnt}".format(id=id, cnt=rows))
        return 200

    def put(self, id=0):
        if id is 0:
            abort(400, message="need task id")

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

        # Get all tasks
        tasks = Task.select().order_by(Task.due_date.asc())
        return tasks_schema.dump(list(tasks))

    def _get_in_exp_days(self, exp_days):
        tasks = Task.select().where(
            (Task.is_done == False)
            &
            Task.due_date.between(dt.datetime.now(),(dt.datetime.now() + dt.timedelta(days=exp_days)))
            # Task.due_date <= (dt.datetime.now() + dt.timedelta(days=exp_days))
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
