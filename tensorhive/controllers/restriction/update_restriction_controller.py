from http import HTTPStatus
from tensorhive.authorization import admin_required
from tensorhive.models.Restriction import Restriction
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.config import API
import logging
log = logging.getLogger(__name__)
R = API.RESPONSES['restriction']
G = API.RESPONSES['general']


def to_db_column():
    return {
        'name': 'name',
        'start': 'starts_at',
        'end': 'ends_at',
        'isGlobal': 'is_global'
    }


@admin_required
def update(id, newValues):
    new_values = newValues
    allowed_fields = {'name', 'start', 'end', 'isGlobal'}
    try:
        assert set(new_values.keys()).issubset(allowed_fields), 'invalid field is present'
        restriction = Restriction.get(id)

        for field_name, new_value in new_values.items():
            field_name = to_db_column().get(field_name)
            assert (field_name is not None) and hasattr(restriction, field_name), \
                'restriction has no {} field'.format(field_name)
            setattr(restriction, field_name, new_value)
        restriction.save()
    except NoResultFound:
        content, status = {'msg': R['not_found']}, HTTPStatus.NOT_FOUND.value
    except AssertionError as e:
        content, status = {'msg': R['update']['failure']['assertions'].format(reason=e)}, \
                          HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': R['update']['success'],
                           'restriction': restriction.as_dict(include_groups=True, include_users=True,
                                                              include_resources=True)}, HTTPStatus.OK.value
    finally:
        return content, status
