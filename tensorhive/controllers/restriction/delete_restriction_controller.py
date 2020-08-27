from sqlalchemy.orm.exc import NoResultFound
from tensorhive.authorization import admin_required
from tensorhive.models.Restriction import Restriction
from tensorhive.config import API
R = API.RESPONSES['restriction']
G = API.RESPONSES['general']


@admin_required
def delete(id):
    try:
        restriction_to_destroy = Restriction.get(id)
        restriction_to_destroy.destroy()
    except AssertionError as error_message:
        content, status = {'msg': str(error_message)}, 403
    except NoResultFound:
        content, status = {'msg': R['not_found']}, 404
    except Exception as e:
        content, status = {'msg': G['internal_error'] + str(e)}, 500
    else:
        content, status = {'msg': R['delete']['success']}, 200
    finally:
        return content, status
