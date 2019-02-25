import pytest
from datetime import timedelta, datetime


def test_reservation_creation(tables, new_reservation):
    new_reservation.save()


def test_interfering_reservation_cannot_be_saved(tables, new_reservation, new_reservation_2):
    # Create initial record
    new_reservation.save()
    offset = timedelta(minutes=5)

    with pytest.raises(AssertionError):
        # | A    A |
        new_reservation_2.starts_at = new_reservation.starts_at + offset
        new_reservation_2.ends_at = new_reservation.ends_at - offset
        new_reservation_2.save()

    with pytest.raises(AssertionError):
        # A |     A |
        new_reservation_2.starts_at = new_reservation.starts_at - offset
        new_reservation_2.ends_at = new_reservation.ends_at - offset
        new_reservation_2.save()

    with pytest.raises(AssertionError):
        # | A     | A
        new_reservation_2.starts_at = new_reservation.starts_at + offset
        new_reservation_2.ends_at = new_reservation.starts_at + offset
        new_reservation_2.save()

    with pytest.raises(AssertionError):
        # A |      | A
        new_reservation_2.starts_at = new_reservation.starts_at - offset
        new_reservation_2.ends_at = new_reservation.ends_at + offset
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
        new_reservation.starts_at = starts_at
        new_reservation.ends_at = ends_at
        new_reservation.save()

    # Test valid format
    valid_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    starts_at, ends_at = cast_dt_to_str(valid_format)
    new_reservation.starts_at = starts_at
    new_reservation.ends_at = ends_at
    new_reservation.save()


@pytest.mark.usefixtures('faker')
def test_invalid_reservation_time_range(tables, new_reservation, faker):
    with pytest.raises(AssertionError):
        # End before start
        new_reservation.starts_at = faker.future_datetime(end_date='+1d')
        new_reservation.ends_at = faker.past_datetime(start_date='-1d')
        new_reservation.save()

    with pytest.raises(AssertionError):
        # Duration too short (30 min at least required)
        new_reservation.starts_at = faker.future_datetime()
        new_reservation.ends_at = new_reservation.starts_at + timedelta(minutes=29, seconds=59)
        new_reservation.save()

    with pytest.raises(AssertionError):
        # Duration too long (2 days at last)
        new_reservation.starts_at = faker.future_datetime()
        new_reservation.ends_at = new_reservation.starts_at + timedelta(days=2, seconds=1)
        print(new_reservation)
        new_reservation.save()
