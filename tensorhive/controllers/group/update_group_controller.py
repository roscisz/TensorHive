from http import HTTPStatus
from tensorhive.authorization import admin_required
from tensorhive.models.Group import Group
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.config import API
import logging
log = logging.getLogger(__name__)
GROUP = API.RESPONSES['group']
G = API.RESPONSES['general']


@admin_required
def update(id, newValues):
    new_values = newValues
    allowed_fields = {'name'}
    try:
        assert set(new_values.keys()).issubset(allowed_fields), 'invalid field is present'
        group = Group.get(id)

        for field_name, new_value in new_values.items():
            assert hasattr(group, field_name), 'group has no {} field'.format(field_name)
            setattr(group, field_name, new_value)
        group.save()
    except NoResultFound:
        content, status = {'msg': GROUP['not_found']}, HTTPStatus.NOT_FOUND.value
    except AssertionError as e:
        content, status = {'msg': GROUP['update']['failure']['assertions'].format(reason=e)}, \
                          HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': GROUP['update']['success'], 'group': group.as_dict}, HTTPStatus.OK.value
    finally:
        return content, status
