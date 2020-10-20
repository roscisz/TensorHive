from tensorhive.database import db_session
from tensorhive.models.Restriction import Restriction
from fixtures.controllers import API_URI as BASE_URI, HEADERS
from http import HTTPStatus
from sqlalchemy.orm.exc import NoResultFound

import datetime
import json
import pytest

ENDPOINT = BASE_URI + '/restrictions'


# GET /restrictions
def test_get_all_restrictions(tables, client):
    resp = client.get(ENDPOINT, headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert len(resp_json) == 0

    # Create new restriction and save it to the DB
    start_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    end_time = start_time + datetime.timedelta(hours=8)
    restriction = Restriction(name='TestRestriction', starts_at=start_time, ends_at=end_time, is_global=False)
    restriction.save()

    resp = client.get(ENDPOINT, headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert len(resp_json) == 1


# GET /restrictions?user_id={id}
def test_get_user_restrictions(tables, client, new_user, restriction):
    new_user.save()
    restriction.apply_to_user(new_user)

    resp = client.get(ENDPOINT + '?user_id={}'.format(new_user.id), headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert resp_json[0]['id'] == restriction.id


# GET /restrictions?user_id={id}&include_user_groups=True
def test_get_users_group_restrictions(tables, client, new_group_with_member, restriction):
    new_group_with_member.save()
    restriction.apply_to_group(new_group_with_member)

    user = new_group_with_member.users[0]
    resp = client.get(ENDPOINT + '?user_id={}&include_user_groups=True'.format(user.id), headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert resp_json[0]['id'] == restriction.id


# GET /restrictions?group_id={id}
def test_get_group_restrictions(tables, client, new_group, restriction):
    new_group.save()
    restriction.apply_to_group(new_group)

    resp = client.get(ENDPOINT + '?group_id={}'.format(new_group.id), headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert resp_json[0]['id'] == restriction.id


# GET /restrictions?resource_id={id}
def test_get_resource_restrictions(tables, client, resource1, restriction):
    resource1.save()
    restriction.apply_to_resource(resource1)

    resp = client.get(ENDPOINT + '?resource_id={}'.format(resource1.id), headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert resp_json[0]['id'] == restriction.id


# GET /restrictions?schedule_id={id}
def test_get_schedule_restrictions(tables, client, active_schedule, restriction):
    active_schedule.save()
    restriction.add_schedule(active_schedule)

    resp = client.get(ENDPOINT + '?schedule_id={}'.format(active_schedule.id), headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert resp_json[0]['id'] == restriction.id


# POST /restrictions - correct way
def test_create_restriction(tables, client):
    data = {
        'name': 'Test restriction',
        'start': '2100-01-01T10:00:00.000Z',
        'end': '2101-02-01T10:00:00.000Z',
        'isGlobal': False
    }
    resp = client.post(ENDPOINT, headers=HEADERS, data=json.dumps(data))
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.CREATED
    assert Restriction.get(resp_json['restriction']['id']) is not None


# POST /restrictions - missing data
def test_create_restriction_missing_data(tables, client):
    data = {
        'name': 'Test restriction',
        'end': '2101-02-01T10:00:00.000Z',
        'isGlobal': False
    }
    resp = client.post(ENDPOINT, headers=HEADERS, data=json.dumps(data))

    assert resp.status_code == HTTPStatus.BAD_REQUEST


# PUT /restrictions/{id} - update existing restriction - correct
def test_update_restriction(tables, client, restriction):
    restriction.save()
    new_name = 'Modified name'
    data = {
        'name': new_name
    }
    resp = client.put(ENDPOINT + '/' + str(restriction.id), headers=HEADERS, data=json.dumps(data))

    assert resp.status_code == HTTPStatus.OK
    assert restriction.name == new_name


# PUT /restrictions/{id} - update existing restriction - incorrect, verify that parameters did not get updated
def test_update_restriction_incorrect_data(tables, client, restriction):
    old_start_date = restriction.starts_at
    old_end_date = restriction.ends_at
    data = {
        'start': '2200-01-01T10:00:00.000Z',    # start date is after the end date, this request shouldn't be accepted
        'end': '2199-02-01T10:00:00.000Z',
    }
    resp = client.put(ENDPOINT + '/' + str(restriction.id), headers=HEADERS, data=json.dumps(data))

    db_session.remove()  # make sure we'll get the restriction from the DB, and not from memory
    restriction = Restriction.get(restriction.id)
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert restriction.starts_at == old_start_date
    assert restriction.ends_at == old_end_date


# PUT /restrictions/{id} - nonexistent restriction
def test_update_nonexistent_restriction(tables, client):
    nonexistent_id = '777'
    data = {
        'name': 'Something'
    }
    resp = client.put(ENDPOINT + '/' + nonexistent_id, headers=HEADERS, data=json.dumps(data))

    assert resp.status_code == HTTPStatus.NOT_FOUND


# PUT /restrictions/{id}/groups/{group_id} - apply restriction to group - correct
def test_apply_restriction_to_group(tables, client, restriction, new_group):
    new_group.save()

    resp = client.put(ENDPOINT + '/{}/groups/{}'.format(restriction.id, new_group.id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.OK
    assert restriction in new_group.get_restrictions()
    assert new_group in restriction.groups


# PUT /restrictions/{id}/groups/{group_id} - nonexistent group
def test_apply_restriction_to_nonexistent_group(tables, client, restriction):
    restriction.save()
    nonexistent_id = '777'

    resp = client.put(ENDPOINT + '/{}/groups/{}'.format(restriction.id, nonexistent_id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.NOT_FOUND


# PUT /restrictions/{id}/groups/{group_id} - nonexistent restriction
def test_apply_nonexistent_restriction_to_group(tables, client, new_group):
    new_group.save()
    nonexistent_id = '777'

    resp = client.put(ENDPOINT + '/{}/groups/{}'.format(nonexistent_id, new_group.id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.NOT_FOUND


# PUT /restrictions/{id}/resources/{resource_id} - apply restriction to resource - correct
def test_apply_restriction_to_resource(tables, client, restriction, resource1):
    restriction.save()
    resource1.save()

    resp = client.put(ENDPOINT + '/{}/resources/{}'.format(restriction.id, resource1.id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.OK
    assert restriction in resource1.get_restrictions()
    assert resource1 in restriction.resources


# PUT /restrictions/{id}/resources/hostname/{hostname}
def test_apply_restriction_to_resources_by_hostname(tables, client, restriction, resource1, resource2):
    restriction.save()
    resource1.hostname = 'nasa.gov'
    resource2.hostname = 'nasa.gov'
    resource1.save()
    resource2.save()

    resp = client.put(ENDPOINT + '/{}/resources/hostname/nasa.gov'.format(restriction.id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.OK
    assert restriction in resource1.get_restrictions()
    assert restriction in resource2.get_restrictions()
    assert resource1 in restriction.resources
    assert resource2 in restriction.resources


# PUT /restrictions/{id}/resources/hostname/{hostname} - no resources with given hostname
def test_apply_restriction_to_nonexistent_resources_by_hostname(tables, client, restriction, resource1, resource2):
    restriction.save()
    resource1.hostname = 'spacex.com'
    resource2.hostname = 'spacex.com'
    resource1.save()
    resource2.save()

    resp = client.put(ENDPOINT + '/{}/resources/hostname/nasa.gov'.format(restriction.id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.OK
    assert restriction not in resource1.get_restrictions()
    assert restriction not in resource2.get_restrictions()
    assert len(restriction.resources) == 0


# PUT /restrictions/{id}/resources/hostname/{hostname}
def test_apply_nonexistent_restriction_to_resources_by_hostname(tables, client, resource1, resource2):
    resource1.hostname = 'nasa.gov'
    resource2.hostname = 'nasa.gov'
    resource1.save()
    resource2.save()

    resp = client.put(ENDPOINT + '/777/resources/hostname/nasa.gov', headers=HEADERS)

    assert resp.status_code == HTTPStatus.NOT_FOUND
    assert len(resource1.get_restrictions()) == 0
    assert len(resource2.get_restrictions()) == 0


# PUT /restrictions/{id}/resources/{resource_id} - nonexistent resource
def test_apply_restriction_to_nonexistent_resource(tables, client, restriction):
    restriction.save()
    nonexistent_id = '777'

    resp = client.put(ENDPOINT + '/{}/resources/{}'.format(restriction.id, nonexistent_id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.NOT_FOUND


# PUT /restrictions/{id}/resources/{resource_id} - nonexistent restriction
def test_apply_nonexistent_restriction_to_resource(tables, client, resource1):
    resource1.save()
    nonexistent_id = '777'

    resp = client.put(ENDPOINT + '/{}/resources/{}'.format(nonexistent_id, resource1.id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.NOT_FOUND


# PUT /restrictions/{id}/schedules/{schedule_id} - apply restriction to schedule - correct
def test_apply_restriction_to_schedule(tables, client, restriction, active_schedule):
    restriction.save()
    active_schedule.save()

    resp = client.put(ENDPOINT + '/{}/schedules/{}'.format(restriction.id, active_schedule.id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.OK
    assert restriction in active_schedule.restrictions
    assert active_schedule in restriction.schedules


# PUT /restrictions/{id}/schedules/{schedule_id} - nonexistent schedule
def test_apply_restriction_to_nonexistent_schedule(tables, client, restriction):
    restriction.save()
    nonexistent_id = '777'

    resp = client.put(ENDPOINT + '/{}/schedules/{}'.format(restriction.id, nonexistent_id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.NOT_FOUND


# PUT /restrictions/{id}/schedules/{schedule_id} - nonexistent restriction
def test_apply_nonexistent_restriction_to_schedule(tables, client, active_schedule):
    active_schedule.save()
    nonexistent_id = '777'

    resp = client.put(ENDPOINT + '/{}/schedules/{}'.format(nonexistent_id, active_schedule.id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.NOT_FOUND


# PUT /restrictions/{id}/users/{group_id} - apply restriction to group - correct
def test_apply_restriction_to_user(tables, client, restriction, new_user):
    restriction.save()
    new_user.save()

    resp = client.put(ENDPOINT + '/{}/users/{}'.format(restriction.id, new_user.id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.OK
    assert restriction in new_user.get_restrictions()
    assert new_user in restriction.users


# PUT /restrictions/{id}/users/{user_id} - nonexistent user
def test_apply_restriction_to_nonexistent_user(tables, client, restriction):
    restriction.save()
    nonexistent_id = '777'

    resp = client.put(ENDPOINT + '/{}/users/{}'.format(restriction.id, nonexistent_id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.NOT_FOUND


# PUT /restrictions/{id}/users/{user_id} - nonexistent restriction
def test_apply_nonexistent_restriction_to_user(tables, client, new_user):
    new_user.save()
    nonexistent_id = '777'

    resp = client.put(ENDPOINT + '/{}/users/{}'.format(nonexistent_id, new_user.id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.NOT_FOUND


# DELETE /restriction/{id} - delete restriction - correct
def test_delete_restriction(tables, client, restriction, new_user):
    new_user.save()
    restriction.apply_to_user(new_user)

    resp = client.delete(ENDPOINT + '/' + str(restriction.id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.OK
    assert restriction not in new_user.get_restrictions()
    with pytest.raises(NoResultFound):
        Restriction.get(restriction.id)


# DELETE /restriction/{id} - delete nonexistent restriction
def test_delete_nonexistent_restriction(tables, client):
    nonexistent_id = '777'
    resp = client.delete(ENDPOINT + '/' + nonexistent_id, headers=HEADERS)

    assert resp.status_code == HTTPStatus.NOT_FOUND
