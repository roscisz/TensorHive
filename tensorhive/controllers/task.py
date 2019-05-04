from tensorhive.models.Task import Task
from tensorhive.models.User import User
from tensorhive.core import task_nursery, ssh
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm.exc import NoResultFound
# from tensorhive.database import flask_app
from tensorhive.config import API
from functools import wraps
import logging
log = logging.getLogger(__name__)
T = API.RESPONSES['task']
G = API.RESPONSES['general']

# TODO print -> logging


def synchronize(func):
    """Updates state of Task stored in database.
    It compares current db record with list of active screen session (pids in general)
    on node defined in Task object (task.user.username@task.host)

    Decorated funciton MUST HAVE task id as FIRST ARGUMENT
    """

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        task_id = args[0]
        print('Syncing Task {}...'.format(task_id))
        try:
            task = Task.get(task_id)
            pids = task_nursery.running(
                host=task.host, user=task.user.username)
        except NoResultFound:
            # Let func handle this
            pass
        except Exception as e:
            # task_nursery.running may raise pssh exceptions
            print('Unable to synchronize, reason: ', e)
            task.exit_code = 90  # FIXME Set unsynchronized status
            task.save()
        else:
            if task.pid in pids:
                print('Task {} is alive'.format(task_id))
            else:
                print('Task {} is dead'.format(task_id))
                task.exit_code = 44  # FIXME Set terminated status
                task.pid = None
                task.save()
        finally:
            return func(*args, **kwargs)

#  GET /tasks
def all(user_id):
    # FIXME Handle exceptions etc.
    # TODO Should sync all?
    print('Not synced records!')
    if user_id:
        tasks = Task.query.filter(Task.user_id == user_id).all()
    else:
        tasks = Task.all()
    return [task.as_dict for task in tasks]


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

# GET /tasks/running?user_id=X&hostname=X
# FIXME This endpoint should probably return ORM objects, not pids
def running(user_id, hostname):
    try:
        assert user_id and hostname
        # TODO Maybe ORM objects should be updated here
        user = User.get(user_id)
        pids = task_nursery.running(host=hostname, user=user.username)
    except AssertionError:
        raise NotImplementedError
    except Exception:
        raise NotImplementedError
    else:
        content, status = {'msg': T['running']['success'], 'pids': pids}, 200
    finally:
        return content, status
        

# GET /tasks/{id}/terminate
def terminate(id):
    # FIXME Check for pid being None
    try:
        task = Task.get(id)
        assert task.pid and task.exit_code is None
        exit_code = task_nursery.terminate(task.pid, task.host, task.user.username)

        # Allow to spawn that object again
        task.pid = None
        task.exit_code = exit_code
        task.save()
    except AssertionError:
        content, status = {'msg': T['terminate']['failure']['invalid_state']}, 405
    except AssertionError:
        raise NotImplementedError
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
    except AssertionError:
        raise NotImplementedError
    else:
        content, status = {'msg': T['spawn']['success'], 'pid': pid}, 200
    finally:
        return content, status

