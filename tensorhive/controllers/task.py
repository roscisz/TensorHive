from tensorhive.models.Task import Task
from tensorhive.models.User import User
from tensorhive.core import task_nursery, ssh
from flask_jwt_extended import jwt_required, get_jwt_identity
# from tensorhive.database import flask_app
from tensorhive.config import API
T = API.RESPONSES['task']
G = API.RESPONSES['general']


#  GET /tasks
def all():
    raise NotImplementedError

# POST /tasks
def create(task):
    try:
        new_task = Task(
            user_id=task['userId'],
            host=task['hostname'],
            command=task['command']
        )
        new_task.save()
    except AssertionError as e:
        content = {'msg': T['create']['failure']['invalid'].format(reason=e)}
        status = 422
    except Exception:
        content = {'msg': G['internal_error']}
        status = 500
    else:
        content = {
            'msg': T['create']['success'],
            'task': new_task.as_dict
        }
        status = 201
    finally:
        return content, status

# GET /tasks/{id}
def get(id):
    raise NotImplementedError

# PUT /tasks/{id}:
def update(id):
    raise NotImplementedError

# DELETE /tasks/{id}
def destroy():
    raise NotImplementedError

# GET /tasks/running
def running():
    raise NotImplementedError

# GET /tasks/{id}/terminate
def terminate(id):
    raise NotImplementedError

# GET /tasks/{id}/start
#@jwt_required
def spawn(id):
    # FIXME Check exceptions, etc.
    # FIXME Redesign
    task = Task.get(id)
    
    config = {
        # FIXME Move
        task.host: {
            'user': task.user.username,
            'pkey': '~/.ssh/id_rsa'
        }
    }
    print(config)
    client = ssh.get_client(config)
    task = task_nursery.Task(task.host, task.command)
    pid = task.spawn(client)
    content, status = {'msg': 'Task spawned', 'pid': pid}, 200
    return content, status

