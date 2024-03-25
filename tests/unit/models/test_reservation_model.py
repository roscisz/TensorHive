import pytest
from datetime import timedelta, datetime
from tensorhive.models.Reservation import Reservation


def test_reservation_creation(tables, new_reservation, faker):
    new_reservation.save()

    new_reservation.start = faker.future_datetime()
    new_reservation.end = new_reservation.start + timedelta(days=8, seconds=-1)
    new_reservation.save()


def test_interfering_reservation_cannot_be_saved(tables, new_reservation, new_reservation_2):
    # Create initial record
    new_reservation.save()
    offset = timedelta(minutes=5)

    with pytest.raises(AssertionError):
        # | A    A |
        new_reservation_2.start = new_reservation.start + offset
        new_reservation_2.end = new_reservation.end - offset
        new_reservation_2.save()

    with pytest.raises(AssertionError):
        # A |     A |
        new_reservation_2.start = new_reservation.start - offset
        new_reservation_2.end = new_reservation.end - offset
        new_reservation_2.save()

    with pytest.raises(AssertionError):
        # | A     | A
        new_reservation_2.start = new_reservation.start + offset
        new_reservation_2.end = new_reservation.end + offset
        new_reservation_2.save()

    with pytest.raises(AssertionError):
        # A |      | A
        new_reservation_2.start = new_reservation.start - offset
        new_reservation_2.end = new_reservation.end + offset
        new_reservation_2.save()


def test_cancelled_reservation_does_not_cause_interference_with_others(tables, new_reservation, new_reservation_2):
    # Create initial record
    new_reservation.is_cancelled = True
    new_reservation.save()
    offset = timedelta(minutes=5)

    # | A    A |
    new_reservation_2.start = new_reservation.start + offset
    new_reservation_2.end = new_reservation.end - offset
    new_reservation_2.save()

    # A |     A |
    new_reservation_2.start = new_reservation.start - offset
    new_reservation_2.end = new_reservation.end - offset
    new_reservation_2.save()

    # | A     | A
    new_reservation_2.start = new_reservation.start + offset
    new_reservation_2.end = new_reservation.end + offset
    new_reservation_2.save()

    # A |      | A
    new_reservation_2.start = new_reservation.start - offset
    new_reservation_2.end = new_reservation.end + offset
    new_reservation_2.save()


@pytest.mark.usefixtures('faker')
def test_string_time_format_conversion(tables, new_reservation, faker):
    # Prepare test data
    starts_at_datetime = faker.future_datetime(end_date='+1d')
    ends_at_datetime = starts_at_datetime + timedelta(minutes=400)

    def cast_dt_to_str(format):
        return starts_at_datetime.strftime(format), ends_at_datetime.strftime(format)

    # Test invalid format
    invalid_format = '%Y_%m_%dT%H:%M:%S.%fZ'
    starts_at, ends_at = cast_dt_to_str(invalid_format)
    with pytest.raises(ValueError):
        new_reservation.start = starts_at
        new_reservation.end = ends_at
        new_reservation.save()

    # Test valid format
    valid_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    starts_at, ends_at = cast_dt_to_str(valid_format)
    new_reservation.start = starts_at
    new_reservation.end = ends_at
    new_reservation.save()


@pytest.mark.usefixtures('faker')
def test_invalid_reservation_time_range(tables, new_reservation, faker):
    with pytest.raises(AssertionError):
        # End before start
        new_reservation.start = faker.future_datetime(end_date='+1d')
        new_reservation.end = faker.past_datetime(start_date='-1d')
        new_reservation.save()

    with pytest.raises(AssertionError):
        # Duration too short (30 min at least required)
        new_reservation.start = faker.future_datetime()
        new_reservation.end = new_reservation.start + timedelta(minutes=29, seconds=59)
        new_reservation.save()

    with pytest.raises(AssertionError):
        # Duration too long (2 days at last)
        new_reservation.start = faker.future_datetime()
        new_reservation.end = new_reservation.start + timedelta(days=8, seconds=1)
        new_reservation.save()


def test_current_events_will_only_return_non_cancelled_reservations(tables, new_reservation, new_reservation_2):
    new_reservation.start = datetime.utcnow() - timedelta(minutes=10)
    new_reservation.end = datetime.utcnow() + timedelta(minutes=60)
    new_reservation.save()
    assert new_reservation in Reservation.current_events()

    new_reservation.is_cancelled = True
    new_reservation.save()
    new_reservation_2.save()

    current_events = Reservation.current_events()
    assert new_reservation not in current_events
    assert new_reservation_2 in current_events
