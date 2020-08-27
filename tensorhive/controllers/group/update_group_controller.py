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
            assert hasattr(group, field_name), 'group has no {} column'.format(field_name)
            setattr(group, field_name, new_value)
        group.save()
    except NoResultFound:
        content, status = {'msg': GROUP['not_found']}, 404
    except AssertionError as e:
        content, status = {'msg': GROUP['update']['failure']['assertions'].format(reason=e)}, 422
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, 500
    else:
        content, status = {'msg': GROUP['update']['success'], 'group': group.as_dict}, 201
    finally:
        return content, status
