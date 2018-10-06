from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from tensorhive.models.User import User
from tensorhive.models.Role import Role


class CreateUserController():
    # TODO Add more user parameters

    @staticmethod
    def create(user):
        try:
            new_user = User.create(username=user['username'], password=user['password'])
            Role.create(name='user', user_id=new_user.id)
        except IntegrityError:
            # Duplicated resource
            content, status = 'Duplicated resource', 409
        except SQLAlchemyError:
            content, status = 'Interal error', 500
        else:
            content, status = 'Successfully created', 201
        finally:
            return {'msg': content}, status
