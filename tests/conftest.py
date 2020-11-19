import pytest
from fixtures.models import new_reservation, new_reservation_2, new_user, new_user_2, new_admin, new_group, \
    new_group_with_member, resource1, resource2, restriction, active_schedule, inactive_schedule, \
    new_job, new_task, new_task_2
from fixtures.database import tables
from fixtures.controllers import client
