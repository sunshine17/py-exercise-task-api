import datetime as dt
from marshmallow import (
    Schema,
    fields,
    validates,
)
from .models import (
    Task,
)

import logging
logger = logging.getLogger('__schemas__')
logger.setLevel(logging.DEBUG)
DUE_DATE_FMT = "%d/%m/%Y"

class TaskSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
#    due_date = fields.DateTime(required=True)
    due_date = fields.Str(required=True)
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
