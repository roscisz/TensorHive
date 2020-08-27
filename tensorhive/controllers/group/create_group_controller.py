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
        status = 422
    except Exception as e:
        content = {'msg': G['internal_error'] + str(e)}
        status = 500
    else:
        content = {
            'msg': GROUP['create']['success'],
            'group': new_group.as_dict
        }
        status = 201
    finally:
        return content, status
