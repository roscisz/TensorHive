import pytest
from sqlalchemy.exc import OperationalError, IntegrityError
from tensorhive.models.Reservation import Reservation
import datetime


@pytest.mark.usefixtures('faker')
def test_invalid_reservation_time_range(db_session, faker):
    with pytest.raises(AssertionError):
        # End is before start
        Reservation(
            start=faker.future_datetime(end_date='+1d'),
            end=faker.past_datetime(start_date='-1d'),
            title='asd',
            description='',
            resource_id='UUID'
        )
    with pytest.raises(AssertionError):
        # Duration is too short
        test_future_datetime = faker.future_datetime()
        test_duration = datetime.timedelta(minutes=10)
        Reservation(
            start=test_future_datetime,
            end=test_future_datetime + test_duration,
            title='asd',
            description='',
            resource_id='UUID'
        )
