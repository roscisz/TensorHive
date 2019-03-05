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
    # FIXME Check for pid being None
    try:
        print(Task.all())
        task = Task.get(id)
        assert task.pid and task.exit_code is None
        exit_code = task_nursery.terminate(task.pid, task.host, task.user.username)

        # Allow to spawn that object again
        task.pid = None
        task.exit_code = exit_code
        task.save()
    except AssertionError:
        content, status = {'msg': T['terminate']['failure']['invalid_state']}, 405    
    else:
        # FIXME Display success only with code==0
        content, status = {'msg': T['terminate']['success'], 'exit_code': exit_code}, 200
    finally:
        return content, status

# GET /tasks/{id}/start
#@jwt_required
def spawn(id):
    # FIXME Check exceptions, etc.
    # FIXME Redesign
    try:
        task = Task.get(id)
        assert task.pid is None
        pid = task_nursery.spawn(task.command, task.host, task.user.username)
        task.pid = pid
        task.exit_code = None
        task.save()
    except AssertionError:
        content, status = {'msg': T['spawn']['failure']['already_spawned']}, 405    
    else:
        content, status = {'msg': T['spawn']['success'], 'pid': pid}, 200
    finally:
        return content, status

