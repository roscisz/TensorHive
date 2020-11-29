import pytest
from tensorhive.models.Job import Job, JobStatus
from tensorhive.models.Task import TaskStatus
from tensorhive.exceptions.InvalidRequestException import InvalidRequestException


def test_job_creation(tables):
    new_job = Job(name='job_name',
                    description='testDescription').save()
    assert new_job.id is not None


def test_adding_task_to_a_job(tables, new_task, new_job):
    new_job.add_task(new_task)

    assert new_task in new_job.tasks
    assert new_job is new_task.job


def test_removing_task_from_a_job(tables, new_job_with_task):
    task = new_job_with_task.tasks[0]
    new_job_with_task.remove_task(task)

    assert task not in new_job_with_task.tasks
    assert new_job_with_task is not task.job


def test_removing_task_from_a_job_that_he_doesnt_belong_to_fails(tables, new_task, new_job):
    with pytest.raises(InvalidRequestException):
        new_job.remove_task(new_task)


def test_adding_task_to_a_job_that_he_is_already_in_fails(tables, new_job_with_task):
    task = new_job_with_task.tasks[0]

    with pytest.raises(InvalidRequestException):
        new_job_with_task.add_task(task)


def test_synchronizing_job(tables, new_job_with_task, new_task_2):
    new_job_with_task.save()
    new_job_with_task.status = JobStatus.unsynchronized
    new_task = new_job_with_task.tasks[0]
    new_task.status = TaskStatus.unsynchronized
    new_task_2.status = TaskStatus.unsynchronized
    new_job_with_task.add_task(new_task_2)

    new_task.status = TaskStatus.not_running
    new_job_with_task.synchronize_status(new_task.status)
    assert new_job_with_task.status is not JobStatus.not_running

    new_task_2.status = TaskStatus.not_running
    new_job_with_task.synchronize_status(new_task.status)
    assert new_job_with_task.status is JobStatus.not_running
