from tensorhive.core.services.Service import Service
from tensorhive.core.utils.decorators import override
from tensorhive.models.Task import Task
from sqlalchemy import or_, and_
from tensorhive.controllers.task import spawn, terminate, synchronize
from typing import List, Dict, Any
from datetime import datetime, timedelta
from tensorhive.database import db_session
import gevent
import logging
log = logging.getLogger(__name__)


class TaskSchedulingService(Service):
    def __init__(self, interval=0.0):
        super().__init__()
        self.interval = interval

    @override
    def inject(self, injected_object):
        pass

    def spawn_scheduled(self, now: datetime):
        is_scheduled = Task.spawn_at.isnot(None)
        before_terminate = or_(Task.terminate_at.is_(None), Task.spawn_at < Task.terminate_at)
        can_spawn_now = and_(Task.spawn_at < now, now < Task.terminate_at)
        tasks_to_spawn = Task.query.filter(is_scheduled, before_terminate, can_spawn_now).all()

        log.debug('{} tasks should be running.'.format(len(tasks_to_spawn)))
        for task in tasks_to_spawn:
            log.info('UTC now: {} | Spawning task {} scheduled for {}'.format(
                now.strftime("%H:%M:%S"), task.id, task.spawn_at.strftime("%H:%M:%S")))
            content, status = spawn(task.id)
            if status == 200:
                log.debug(content['pid'])
            else:
                log.debug(content['msg'])

    def terminate_scheduled(self, now: datetime):
        # Get only tasks that were scheduled to terminate within last X minutes
        # We ignore tasks which were not able to terminate by that time
        # It improves performance, because we don't have to check every single task in db
        consideration_threshold = now - timedelta(minutes=1)
        recently_scheduled = and_(Task.terminate_at.isnot(None), Task.terminate_at > consideration_threshold)
        after_spawn = or_(Task.spawn_at < Task.terminate_at, Task.spawn_at.isnot(None))
        can_terminate_now = Task.terminate_at < now
        tasks_to_terminate = db_session.query(Task).filter(recently_scheduled, after_spawn, can_terminate_now).all()

        log.debug('{} tasks should be terminated.'.format(len(tasks_to_terminate)))
        for task in tasks_to_terminate:
            print('UTC now: {} | Killing task {} scheduled for {}'.format(
                now.strftime("%H:%M:%S"), task.id, task.terminate_at.strftime("%H:%M:%S")))
            content, status = terminate(task.id, gracefully=False)
            if status == 201:
                log.debug(content['exit_code'])
            else:
                log.debug(content['msg'])

    @override
    def do_run(self):
        # Sleep here is important, API server must be running first (empirical observations)
        # It prevents SQLAlchemy from sqlite3.ProgrammingError caused by threading problems.
        gevent.sleep(self.interval)
        # print()
        # print('Waking up...')
        now = datetime.utcnow()
        # print('=====================================')
        self.spawn_scheduled(now)
        gevent.sleep(self.interval)
        # print('=====================================')
        self.terminate_scheduled(now)
        # print('=====================================')
        # print('Going to sleep...')
