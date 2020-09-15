from http import HTTPStatus
from tensorhive.models.Group import Group
from tensorhive.authorization import admin_required
from tensorhive.config import API
GROUP = API.RESPONSES['group']
G = API.RESPONSES['general']


@admin_required
def create(group):
    try:
        new_group = Group(
            name=group['name']
        )
        new_group.save()
    except AssertionError as e:
        content = {'msg': GROUP['create']['failure']['invalid'].format(reason=e)}
        status = HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        content = {'msg': G['internal_error'] + str(e)}
        status = HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content = {
            'msg': GROUP['create']['success'],
            'group': new_group.as_dict
        }
        status = HTTPStatus.CREATED.value
    finally:
        return content, status
