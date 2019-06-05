from tensorhive.core.services.Service import Service
from tensorhive.core.utils.decorators import override
from tensorhive.models.Task import Task
from sqlalchemy import or_, and_
from tensorhive.controllers.task import business_spawn, business_terminate, TaskId
from typing import List, Dict, Any
from datetime import datetime, timedelta
from tensorhive.database import db_session
import gevent
import logging
log = logging.getLogger(__name__)


class TaskSchedulingService(Service):
    """Responsible for automatic spawn and termination of processes on remote hosts via ssh.

    It runs periodically, checking if database records require taking some action.
    """

    def __init__(self, interval: float, stop_attempts_after: float):
        super().__init__()
        self.interval = interval
        self.stop_attempts_after = timedelta(minutes=stop_attempts_after)

    # FIXME Remove unnecesary boilerplate (it's here only because of consistency with other services)
    @override
    def inject(self, injected_object: Any):
        pass

    def _log_msg(self, now: datetime, action: str, id: TaskId, scheduled: datetime) -> str:
        return 'UTC now: {now} | {action} task {task_id} scheduled for {scheduled}'.format(
            now=now.strftime("%H:%M:%S"), action=action, task_id=id, scheduled=scheduled.strftime("%H:%M:%S"))

    def spawn_scheduled(self, now: datetime):
        """Triggers `spawn` on database records that should be already running.

        Author's note:
        - SQLAlchemy ORM requires explicit None checks (looks uglier though).
        - Controller implementation takes full responsibility for spawning logic.
        """
        is_scheduled = Task.spawn_at.isnot(None)
        before_terminate = or_(Task.terminate_at.is_(None), Task.spawn_at < Task.terminate_at)
        # TODO What if terminate_at is None? It can prevent from spawning
        can_spawn_now = and_(Task.spawn_at < now, now < Task.terminate_at)

        # All requirements must be satisfied (AND operator)
        tasks_to_spawn = Task.query.filter(is_scheduled, before_terminate, can_spawn_now).all()

        log.debug('{} tasks should be running.'.format(len(tasks_to_spawn)))
        for task in tasks_to_spawn:
            content, status = business_spawn(task.id)
            log.info(self._log_msg(now=now, action='Spawning', id=task.id, scheduled=task.spawn_at))

            if status == 200:
                log.debug(content['pid'])
            else:
                log.warning(content['msg'])

    def terminate_scheduled(self, now: datetime):
        """Triggers `terminate` on database records that should not be running.

        It will stop trying after `self.stop_attempts_after` because it means that
        process is unable to kill and probably requires human (owner/admin) intervention.
        Current behavior:
        - Gets only those tasks which were scheduled to terminate within last X seconds/minutes/whatever
        - Ignores tasks which were not able to terminate by that time
        It improves performance, because we don't have to check every single task from the past.

        Author's note:
        - Controller implementation takes full responsibility for termination logic.
        """
        consideration_threshold = now - self.stop_attempts_after
        recently_scheduled = and_(Task.terminate_at.isnot(None), Task.terminate_at > consideration_threshold)
        after_spawn = or_(Task.spawn_at < Task.terminate_at, Task.spawn_at.isnot(None))
        can_terminate_now = Task.terminate_at < now
        # TODO Try replacing with Task.query.filter
        tasks_to_terminate = db_session.query(Task).filter(recently_scheduled, after_spawn, can_terminate_now).all()

        log.debug('{} tasks should be terminated.'.format(len(tasks_to_terminate)))
        for task in tasks_to_terminate:
            content, status = business_terminate(task.id, gracefully=False)
            log.info(self._log_msg(now=now, action='Killing', id=task.id, scheduled=task.terminate_at))

            if status == 201:
                log.debug(content['exit_code'])
            else:
                log.warning(content['msg'])

    @override
    def do_run(self):
        """Service loop."""
        # Sleep is important, because API server must be already running (empirical observations)
        # It prevents SQLAlchemy from sqlite3.ProgrammingError caused by threading problems.
        gevent.sleep(self.interval / 2)
        self.spawn_scheduled(now=datetime.utcnow())

        gevent.sleep(self.interval / 2)
        self.terminate_scheduled(now=datetime.utcnow())
