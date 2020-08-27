from tensorhive.authorization import admin_required
from tensorhive.models.Group import Group
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.config import API
GROUP = API.RESPONSES['group']
G = API.RESPONSES['general']


@admin_required
def delete(id):
    try:
        group_to_destroy = Group.get(id)
        group_to_destroy.destroy()
    except AssertionError as error_message:
        content, status = {'msg': str(error_message)}, 403
    except NoResultFound:
        content, status = {'msg': GROUP['not_found']}, 404
    except Exception as e:
        content, status = {'msg': G['internal_error'] + str(e)}, 500
    else:
        content, status = {'msg': GROUP['delete']['success']}, 200
    finally:
        return content, status
