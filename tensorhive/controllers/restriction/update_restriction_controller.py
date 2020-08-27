from tensorhive.authorization import admin_required
from tensorhive.models.Restriction import Restriction
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.config import API
import logging
log = logging.getLogger(__name__)
R = API.RESPONSES['restriction']
G = API.RESPONSES['general']


@admin_required
def update(id, newValues):
    new_values = newValues
    allowed_fields = {'name', 'start', 'end', 'isGlobal'}
    try:
        assert set(new_values.keys()).issubset(allowed_fields), 'invalid field is present'
        restriction = Restriction.get(id)

        for field_name, new_value in new_values.items():
            # Mapping API field name to column used by Restriction model
            if field_name in ['start', 'end']:
                # start -> starts_at, end -> ends_at
                field_name += 's_at'
            if field_name == 'isGlobal':
                field_name = 'is_global'
            assert hasattr(restriction, field_name), 'restriction has no {} column'.format(field_name)
            setattr(restriction, field_name, new_value)
        restriction.save()
    except NoResultFound:
        content, status = {'msg': R['not_found']}, 404
    except AssertionError as e:
        content, status = {'msg': R['update']['failure']['assertions'].format(reason=e)}, 422
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, 500
    else:
        content, status = {'msg': R['update']['success'],
                           'restriction': restriction.as_dict(include_groups=True, include_users=True,
                                                              include_resources=True)}, 201
    finally:
        return content, status
