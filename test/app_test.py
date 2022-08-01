import pytest
import datetime as dt
import app.task as task

@pytest.fixture
def mock_lst():
    return [{
        'title': "title_{}".format(i), 
        'is_done': False,
        'due_date': (dt.datetime.now() + dt.timedelta(days=i)).isoformat(), 
    } for i in range(1,11)]

@pytest.fixture()
def app(mock_lst):
    app = task.app
    app.config.update({
        "TESTING": True,
    })
#    task.start()

#    task.create_tables()
    # clear and setup testing data in database
    task.Task.delete().execute()
    task.Task.insert_many(task.tasks_schema.load(mock_lst)).execute()

    task.logger.debug(mock_lst)

    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

# POST /task/
def test_post_task(client):
    post_one = {'title':'test_post_task', 'due_date': dt.datetime.now().isoformat()}
    res = client.post('/task', json=post_one)
    assert res.status_code == 201
    
# PUT /task/1
def test_put_task(client):
    updated_title = 'updated_title'
    input_json = {'title': updated_title}
    res = client.put('/task/1', json=input_json)
    assert res.status_code == 204
    
    updated = task.Task.get(task.Task.id == 1)
    assert updated is not None
    assert task.task_schema.dump(updated)['title'] == updated_title

    
# GET /tasks
def test_get_tasks(client):
    res = client.get('/tasks')
    lst = res.json
    assert lst is not None
    assert len(lst) == 10
    
# GET /tasks/2
def test_get_tasks_expiring(client):
    res = client.get('/tasks/expire-in-days/2')    # expiring in 2 days
    lst = res.json
    assert lst is not None
    assert len(lst) == 1

# PUT /task/1/toggle
def test_put_task_toggle(client):
    res = client.put('/task/1/toggle', json={})
    assert res.status_code == 200

    updated = task.Task.get(task.Task.id == 1)

    assert updated is not None
    dic = task.task_schema.dump(updated)
    task.logger.debug(dic)
    assert dic['is_done'] == True
    

