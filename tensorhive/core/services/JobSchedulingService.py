from tensorhive.core.services.Service import Service
from tensorhive.core.utils.decorators import override
from tensorhive.models.Job import Job
from sqlalchemy import or_, and_
from tensorhive.controllers.job import business_execute, business_stop, JobId
from typing import List, Dict, Any
from datetime import datetime, timedelta
from tensorhive.database import db_session
import gevent
import logging
log = logging.getLogger(__name__)


class JobSchedulingService(Service):
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

    def _log_msg(self, now: datetime, action: str, id: JobId, scheduled: datetime) -> str:
        return 'UTC now: {now} | {action} job {job_id} scheduled for {scheduled}'.format(
            now=now.strftime("%H:%M:%S"), action=action, job_id=id, scheduled=scheduled.strftime("%H:%M:%S"))

    def execute_scheduled(self, now: datetime):
        """Triggers `execute` on database records that should be already running.

        Author's note:
        - SQLAlchemy ORM requires explicit None checks (looks uglier though).
        - Controller implementation takes full responsibility for job executing logic.
        """
        is_scheduled = Job._start_at.isnot(None)
        before_terminate = or_(Job._stop_at.is_(None), Job._start_at < Job._stop_at)
        # TODO What if _stop_at is None? It can prevent from executing
        can_execute_now = and_(Job._start_at < now, now < Job._stop_at)

        # All requirements must be satisfied (AND operator)
        jobs_to_run = Job.query.filter(is_scheduled, before_terminate, can_execute_now).all()

        log.debug('{} jobs should be running.'.format(len(jobs_to_run)))
        for job in jobs_to_run:
            content, status = business_execute(job.id)
            log.info(self._log_msg(now=now, action='Executing', id=job.id, scheduled=job._start_at))

            if status == 200:
                log.debug(content['job']['status'])
            else:
                log.warning(content['msg'])

    def stop_scheduled(self, now: datetime):
        """Triggers `stop` on database records that should not be running.
        After that `terminate` is trigerred on all of task database records in
        relationship with the job.

        It will stop trying after `self.stop_attempts_after` because it means that one or more
        processes is unable to kill and probably requires human (owner/admin) intervention.
        Current behavior:
        - Gets only those jobs which were scheduled to terminate within last X seconds/minutes/whatever
        - Ignores jobs which were not able to terminate by that time
        It improves performance, because we don't have to check every single job from the past.

        Author's note:
        - Controller implementation takes full responsibility for stopping job logic.
        """
        consideration_threshold = now - self.stop_attempts_after
        recently_scheduled = and_(Job._stop_at.isnot(None), Job._stop_at > consideration_threshold)
        after_start = or_(Job._start_at < Job._stop_at, Job._start_at.isnot(None))
        can_stop_now = Job._stop_at < now
        jobs_to_stop = Job.query.filter(recently_scheduled, after_start, can_stop_now).all()

        log.debug('{} jobs should be stopped.'.format(len(jobs_to_stop)))
        for job in jobs_to_stop:
            content, status = business_stop(job.id, gracefully=False)
            log.info(self._log_msg(now=now, action='Stopping', id=job.id, scheduled=job._stop_at))

            if status == 200:
                log.debug(content['job']['status'])
            else:
                log.warning(content['msg'])

    @override
    def do_run(self):
        """Service loop."""
        # Sleep is important, because API server must be already running (empirical observations)
        # It prevents SQLAlchemy from sqlite3.ProgrammingError caused by threading problems.
        gevent.sleep(self.interval / 2)
        self.execute_scheduled(now=datetime.utcnow())

        gevent.sleep(self.interval / 2)
        self.stop_scheduled(now=datetime.utcnow())
