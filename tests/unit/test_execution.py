from tensorhive.controllers.job import business_execute
from tensorhive.models.Task import TaskStatus
from tensorhive.models.Job import JobStatus
from getpass import getuser


def test_executing_job(tables, new_user, new_job, new_task):
    new_user.username = getuser()
    new_user.save()
    new_job.save()
    new_task.save()
    new_job.add_task(new_task)
    business_execute(new_job.id)
    assert new_job.status == JobStatus.running
    assert new_task.status == TaskStatus.running
