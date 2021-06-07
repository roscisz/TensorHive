from tensorhive.core.services.Service import Service
from tensorhive.core.utils.decorators import override
from tensorhive.models.Job import Job
from tensorhive.models.Task import TaskStatus
from tensorhive.models.User import User
from tensorhive.models.Reservation import Reservation
from sqlalchemy import or_, and_
from tensorhive.controllers.job import business_execute, business_stop, JobId
from tensorhive.config import JOB_SCHEDULING_SERVICE as CONFIG
from tensorhive.core.scheduling import Scheduler
from tensorhive.core.managers.InfrastructureManager import InfrastructureManager
from tensorhive.core.managers.SSHConnectionManager import SSHConnectionManager
from tensorhive.core import task_nursery
from typing import List, Dict, Set
from datetime import datetime, timedelta
from http import HTTPStatus
from tensorhive.database import db_session  # pylint: disable=unused-import
import gevent
import logging
log = logging.getLogger(__name__)


class JobSchedulingService(Service):
    """Responsible for automatic spawn and termination of processes on remote hosts via ssh.

    It runs periodically, checking if database records require taking some action.
    """
    _infrastructure_manager = None  # type: InfrastructureManager
    _connection_manager = None  # type: SSHConnectionManager
    _scheduler = None  # type: Scheduler

    def __init__(self, interval: float, stop_attempts_after: float):
        super().__init__()
        self.interval = interval
        self.stop_attempts_after = timedelta(minutes=stop_attempts_after)
        self.stubborn_job_ids = set()  # type: Set[int]
        self.considered_future_period = timedelta(minutes=CONFIG.SCHEDULE_QUEUED_JOBS_WHEN_FREE_MINS)

    @override
    def inject(self, injected_object):
        if isinstance(injected_object, InfrastructureManager):
            self._infrastructure_manager = injected_object
        if isinstance(injected_object, SSHConnectionManager):
            self._connection_manager = injected_object
        if isinstance(injected_object, Scheduler):
            self._scheduler = injected_object

    def _log_msg(self, now: datetime, action: str, id: JobId, scheduled: datetime = None) -> str:
        scheduled_msg = 'scheduled for ' + scheduled.strftime("%H:%M:%S") if scheduled else 'not scheduled'
        return 'UTC now: {now} | {action} job {job_id} {scheduled}'.format(
            now=now.strftime("%H:%M:%S"), action=action, job_id=id, scheduled=scheduled_msg)

    @staticmethod
    def find_jobs_scheduled_for_date(date: datetime) -> List[Job]:
        is_scheduled = Job._start_at.isnot(None)
        before_terminate = or_(Job._stop_at.is_(None), Job._start_at < Job._stop_at)
        # TODO What if _stop_at is None? It can prevent from executing
        can_execute_now = and_(Job._start_at < date, date < Job._stop_at)

        # All requirements must be satisfied (AND operator)
        return Job.query.filter(is_scheduled, before_terminate, can_execute_now).all()

    def try_execute(self, job):
        """
        return value: True if succeeded
        """
        content, status = business_execute(job.id)

        if status == 200:
            log.debug(content['job']['status'])
            return True
        else:
            log.warning(content['msg'])
            return False

    def check_current_gpu_slots(self,
                                hosts_with_gpu_occupation: Dict[str, Dict[str, bool]]) -> Dict[str, Dict[str, int]]:
        '''For each GPU in the dictionary, return the numbers of minutes until the next reservation of consecutive GPUs.
        Return 0 for GPUs that are currently occupied, regardless of the reservations.
        Return None for GPUs that have no scheduled reservations in the future.
        :param hosts_with_gpu_occupation: {hostname: {GPU_id: True if GPU occupied}}
        :returns: {hostname: {GPU_id: number_of_minutes until next occupation of the GPU}}
        '''
        ret = {}  # type: Dict[str, Dict[str, int]]

        for host in hosts_with_gpu_occupation:
            ret[host] = {}
            for gpu_id in hosts_with_gpu_occupation[host]:
                if hosts_with_gpu_occupation[host][gpu_id]:
                    ret[host][gpu_id] = 0
                else:
                    near_reservations = Reservation.upcoming_events_for_resource(gpu_id, self.considered_future_period)
                    if len(near_reservations):
                        nearest_reservation = near_reservations[0]
                        if nearest_reservation.start > datetime.now():  # type: ignore
                            ret[host][gpu_id] = \
                                (nearest_reservation.start - datetime.now()).total_seconds() / 60  # type: ignore
                        else:
                            ret[host][gpu_id] = 0
                    else:
                        ret[host][gpu_id] = None
        return ret

    @staticmethod
    def check_if_resources_available_for_job(job: Job, current_device_occupation: Dict[str, Dict[str, bool]]) -> bool:
        for task in job.tasks:
            if not task.hostname:
                return False
            if not task.gpu_id:
                return False
            if current_device_occupation[task.hostname][task.gpu_id]:
                return False
        return True

    @staticmethod
    def interferes_with_reservations(job: Job, available_hosts_with_gpu_occupation: Dict[str, Dict],
                                     considered_future_period: timedelta = timedelta(0),
                                     allow_own: bool = True) -> bool:
        for task in job.tasks:
            gpu_id = Scheduler.get_assigned_gpu_uid(task, available_hosts_with_gpu_occupation)
            upcoming_reservations = Reservation.upcoming_events_for_resource(gpu_id, considered_future_period)

            if allow_own:
                for reservation in upcoming_reservations:
                    if reservation.user is not job.user:
                        return True
            elif len(upcoming_reservations):
                return True

        return False

    def execute_scheduled(self, available_hosts_with_gpu_occupation: Dict[str, Dict[str, bool]]) -> bool:
        '''
        returns: True if any job has been executed
        '''
        now = datetime.utcnow()
        user_scheduled_jobs = self.find_jobs_scheduled_for_date(now)

        successfully_executed = False
        for user_scheduled_job in user_scheduled_jobs:
            if not self.check_if_resources_available_for_job(user_scheduled_job, available_hosts_with_gpu_occupation):
                log.info(self._log_msg(now=now, action='Not executing scheduled job because resource occupied',
                                       id=user_scheduled_job.id, scheduled=user_scheduled_job._start_at))
                continue

            if self.interferes_with_reservations(user_scheduled_job, available_hosts_with_gpu_occupation):
                log.info(self._log_msg(now=now, action='Not executing scheduled job because Executing scheduled',
                                       id=user_scheduled_job.id, scheduled=user_scheduled_job._start_at))
                continue

            log.info(self._log_msg(now=now, action='Executing scheduled', id=user_scheduled_job.id,
                                   scheduled=user_scheduled_job._start_at))
            successfully_executed = successfully_executed or self.try_execute(user_scheduled_job)

        return successfully_executed

    # TODO: cache for user?
    def get_hosts_with_gpus_eligible_for_jobs(self, jobs: List[Job]) -> Dict[Job, Dict]:
        '''
        :param jobs: list of jobs
        :return: {job: {hostname: {GPU_id: ...}}}
        '''
        ret = {}

        current_infrastructure = self._infrastructure_manager.infrastructure

        for job in jobs:
            owner = job.user  # type: User
            user_filtered_infrastructure = owner.filter_infrastructure_by_user_restrictions(current_infrastructure)
            user_filtered_hostname_gpus = {}
            for hostname in user_filtered_infrastructure:
                eligible_gpus_for_host = []
                if 'GPU' in user_filtered_infrastructure[hostname]:
                    for gpu in user_filtered_infrastructure[hostname]['GPU']:
                        eligible_gpus_for_host.append(gpu)
                user_filtered_hostname_gpus[hostname] = eligible_gpus_for_host
            ret[job] = user_filtered_hostname_gpus

        return ret

    def execute_queued(self, available_hosts_with_gpu_occupation: Dict[str, Dict[str, bool]]):
        queued_jobs = Job.get_job_queue()

        queued_jobs_to_eligible_gpus = self.get_hosts_with_gpus_eligible_for_jobs(queued_jobs)

        available_slots = self.check_current_gpu_slots(available_hosts_with_gpu_occupation)

        scheduled_jobs = self._scheduler.schedule_jobs(queued_jobs_to_eligible_gpus, available_slots)

        for scheduled_job in scheduled_jobs:
            log.info(self._log_msg(now=datetime.utcnow(), action='Executing queued', id=scheduled_job.id))
            self.try_execute(scheduled_job)

    def stop_with_grace(self, job_id: int):
        if job_id in self.stubborn_job_ids:
            log.info(self._log_msg(now=datetime.utcnow(), action='Killing ungracefully', id=job_id))
            self.stubborn_job_ids.remove(job_id)
            return business_stop(job_id, gracefully=False)
        else:
            log.info(self._log_msg(now=datetime.utcnow(), action='Stopping gracefully', id=job_id))
            _, status = business_stop(job_id, gracefully=True)
            if status != HTTPStatus.OK.value:
                self.stubborn_job_ids.add(job_id)

    def stop_scheduled(self):
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
        now = datetime.utcnow()
        consideration_threshold = now - self.stop_attempts_after
        recently_scheduled = and_(Job._stop_at.isnot(None), Job._stop_at > consideration_threshold)
        after_start = or_(Job._start_at < Job._stop_at, Job._start_at.isnot(None))
        can_stop_now = Job._stop_at < now
        jobs_to_stop = Job.query.filter(recently_scheduled, after_start, can_stop_now).all()

        log.debug('{} jobs should be stopped.'.format(len(jobs_to_stop)))
        for job in jobs_to_stop:
            log.info(self._log_msg(now=now, action='Stopping scheduled', id=job.id, scheduled=job._stop_at))
            content, status = self.stop_with_grace(job.id)

            if status == 200:
                log.debug(content['job']['status'])
            else:
                log.warning(content['msg'])

    def sync_running_from_queue(self, available_hosts_with_gpu_occupation: Dict[str, Dict[str, List]]):
        jobs_running_from_queue = Job.get_jobs_running_from_queue()

        for job in jobs_running_from_queue:
            job_should_be_stopped = False
            for task in job.tasks:
                gpu_uid = Scheduler.get_assigned_gpu_uid(task, available_hosts_with_gpu_occupation)

                if not gpu_uid or task.pid not in task_nursery.running(task.hostname, job.user.username):
                    task.status = TaskStatus.not_running
                    continue

                current_processes_on_gpu = available_hosts_with_gpu_occupation[task.hostname][gpu_uid]
                if current_processes_on_gpu is None:
                    other_process_pids = []
                else:
                    other_process_pids = [process['pid'] for process in current_processes_on_gpu
                                          if process['pid'] is not task.pid]

                considered_future_period = timedelta(minutes=CONFIG.SCHEDULE_QUEUED_JOBS_WHEN_FREE_MINS)
                interferes = self.interferes_with_reservations(job, available_hosts_with_gpu_occupation,
                                                               considered_future_period=considered_future_period,
                                                               # Queued jobs should run only between reservations
                                                               allow_own=False)

                if len(other_process_pids) or interferes:
                    job_should_be_stopped = True

            if job_should_be_stopped:
                log.info(self._log_msg(now=datetime.utcnow(), action='Stopping queued job', id=job.id))
                self.stop_with_grace(job.id)

    @override
    def do_run(self):
        gevent.sleep(self.interval / 2)
        available_hosts_with_gpu_occupation = self._infrastructure_manager.all_nodes_with_gpu_processes()

        # If some jobs scheduled by the user were executed in this run, wait with executing
        # queued jobs until the next round to make sure which devices will be free
        if not self.execute_scheduled(available_hosts_with_gpu_occupation):
            self.execute_queued(available_hosts_with_gpu_occupation)

        gevent.sleep(self.interval / 2)
        self.stop_scheduled()
        self.sync_running_from_queue(available_hosts_with_gpu_occupation)
