from tensorhive.authorization import admin_required
from tensorhive.models.User import User


@admin_required
def all():
    return [
        user.as_dict for user in User.all()
    ], 200
