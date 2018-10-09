import pytest
from tensorhive.database import create_app, db
from tensorhive.models.Reservation import Reservation

from fixtures.models import new_reservation, new_user, new_admin, user_role, admin_role
from fixtures.database import db_session, test_client