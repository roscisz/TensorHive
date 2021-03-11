import pytest
from fixtures.models import new_reservation, new_reservation_2, past_reservation, active_reservation,\
    future_reservation, new_user, new_user_2, new_admin, new_group, new_group_with_member, resource1, resource2, \
    restriction, permissive_restriction, active_schedule, inactive_schedule, new_job, new_admin_job,\
    new_job_with_task, new_task, new_task_2
from fixtures.database import tables
from fixtures.controllers import client
