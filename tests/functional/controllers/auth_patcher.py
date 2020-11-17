from unittest.mock import patch
from tensorhive.config import API
from functools import wraps

import tensorhive.controllers.group as group
import tensorhive.controllers.reservation as reservation
import tensorhive.controllers.restriction as restriction
import tensorhive.controllers.schedule as schedule
import tensorhive.controllers.user as user

CONTROLLER_MODULES = [group, reservation, restriction, schedule, user]

G = API.RESPONSES['general']


def get_patches(superuser=False):
    def always_unprivileged(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            return {'msg': G['unprivileged']}, 403

        return wrapper

    if superuser:
        return [patch('tensorhive.authorization.admin_required', lambda x: x),
                patch('flask_jwt_extended.get_jwt_claims', lambda: {'roles': ['admin', 'user']})]
    else:
        return [patch('tensorhive.authorization.admin_required', lambda x: always_unprivileged(x)),
                patch('flask_jwt_extended.get_jwt_claims', lambda: {'roles': ['user']})]
