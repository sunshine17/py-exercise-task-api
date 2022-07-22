import peewee as pw

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
