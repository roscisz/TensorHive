import pytest
from tensorhive.models.Job import Job, JobStatus
from tensorhive.models.Task import TaskStatus


def test_synchronizing_job(tables, new_user, new_job, new_task, new_task_2):
    new_user.save()
    new_job.save()
    new_job.status = JobStatus.unsynchronized
    new_task.save()
    new_task.status = TaskStatus.unsynchronized
    new_task_2.save()
    new_task_2.status = TaskStatus.unsynchronized
    new_job.add_task(new_task)
    new_job.add_task(new_task_2)

    new_task.status = TaskStatus.not_running
    new_job.synchronize_status(new_task.status)
    assert new_job.status is not JobStatus.not_running

    new_task_2.status = TaskStatus.not_running
    new_job.synchronize_status(new_task.status)
    assert new_job.status is JobStatus.not_running
