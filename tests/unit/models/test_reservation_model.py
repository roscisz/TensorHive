import pytest
from sqlalchemy.exc import OperationalError, IntegrityError
from tensorhive.models.Reservation import Reservation
import datetime


def test_exception_on_reservation_collision(db_session, valid_user):
    now = datetime.datetime.utcnow()
    duration = datetime.timedelta(minutes=30)

    existing_reservation = Reservation.create(
        start=now,
        end=now + duration,
        title='asd',
        description='',
        resource_id='THE SAME UUID',
        user_id=valid_user.id
    ).save(session=db_session)

    with pytest.raises(AssertionError):
        # TODO Refactor, use fixtures
        # Between time
        colliding_reservation = Reservation.create(
            start=now + datetime.timedelta(minutes=5),
            end=now + duration - datetime.timedelta(minutes=5),
            title='asd',
            description='',
            resource_id='THE SAME UUID',
            user_id=valid_user.id
        ).save(session=db_session)

    # IT DOES NOT RAISE ANY ERRORS!
    # with pytest.raises(AssertionError):
    #     # Exact time
    #     colliding_reservation = Reservation.create(
    #         start=now,
    #         end=now + duration,
    #         title='asd',
    #         description='',
    #         resource_id='THE SAME UUID',
    #         user_id=valid_user.id
    #     ).save(session=db_session)


@pytest.mark.usefixtures('faker')
def test_invalid_reservation_time_range(db_session, faker):
    with pytest.raises(AssertionError):
        # End is before start
        Reservation(
            start=faker.future_datetime(end_date='+1d'),
            end=faker.past_datetime(start_date='-1d'),
            title='asd',
            description='',
            resource_id='UUID',
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


@pytest.mark.usefixtures('faker')
def test_valid_string_time_format(db_session, faker, valid_user):
    starts_at = faker.future_datetime(end_date='+1d')
    ends_at = starts_at + datetime.timedelta(minutes=400)

    # Convert datetime to string
    valid_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    starts_at = starts_at.strftime(valid_format)  # type: str
    ends_at = ends_at.strftime(valid_format)  # type: str

    Reservation.create(
        start=starts_at,
        end=ends_at,
        title='asd',
        description='',
        resource_id='UUID',
        user_id=valid_user.id
    ).save(session=db_session)


@pytest.mark.usefixtures('faker')
def test_invalid_start_time_format(db_session, faker, valid_user):
    starts_at = faker.future_datetime()
    ends_at = starts_at + datetime.timedelta(minutes=400)

    # Convert datetime to string
    invalid_format = '%Y_%m_%dT%H:%M:%S.%fZ'
    starts_at = starts_at.strftime(invalid_format)  # type: str
    ends_at = ends_at.strftime(invalid_format)  # type: str

    with pytest.raises(ValueError):
        Reservation(
            start=starts_at,
            end=ends_at,
            title='asd',
            description='',
            resource_id='UUID',
            #user_id=valid_user.id
        )


@pytest.mark.parametrize('duration_in_minutes', [
    30, 31, 40, 120, 9999
])
@pytest.mark.usefixtures('faker')
def test_valid_reservation_creation(db_session, faker, duration_in_minutes, valid_user):
    starts_at = faker.future_datetime()
    duration = datetime.timedelta(minutes=duration_in_minutes)
    reservation = Reservation.create(
        start=starts_at,
        end=starts_at + duration,
        title='asd',
        description='',
        resource_id='UUID',
        user_id=valid_user.id
    ).save(session=db_session)
    assert reservation.duration == duration
