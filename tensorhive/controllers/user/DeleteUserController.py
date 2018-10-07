from tensorhive.models.User import User
from tensorhive.models.Role import Role
from connexion import NoContent
from flask_jwt_extended import get_raw_jwt, get_jwt_identity
from tensorhive.models.RevokedToken import RevokedToken
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound


class DeleteUserController():

    @staticmethod
    def delete(id):
        try:
            if id == get_jwt_identity():
                # User is not allowed to delete his own account
                raise AssertionError('Cannot delete current account')

            current_user = User.get(get_jwt_identity())
            if not current_user.has_role('admin'):
                # Admin priviliges are required
                raise AssertionError('Must have admin rights')

            user = User.get(id)
            user.destroy()
        except AssertionError as error_message:
            content, status = str(error_message), 403
        except NoResultFound:
            content, status = 'Not Found', 404
        except (MultipleResultsFound, SQLAlchemyError):
            content, status = 'Internal Error.', 500
        else:
            content, status = 'Successfully deleted.', 204
        finally:
            return {'msg': content}, status
