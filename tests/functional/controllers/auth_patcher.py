from unittest.mock import patch
from tensorhive.config import API
from functools import wraps
import tensorhive.controllers.group as group

CONTROLLER_MODULES = [group]

G = API.RESPONSES['general']


def get_patch(superuser=False):
    def always_unprivileged(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            return {'msg': G['unprivileged']}, 403

        return wrapper

    if superuser:
        return patch('tensorhive.authorization.admin_required', lambda x: x)
    else:
        return patch('tensorhive.authorization.admin_required', lambda x: always_unprivileged(x))
