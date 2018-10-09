# import pytest
# from sqlalchemy.exc import OperationalError, IntegrityError
# from tensorhive.models.User import User


# # TODO May want to use faker fixture everywhere
# @pytest.mark.parametrize('_reason, test_username', [
#     ('too_short', 'a'),
#     ('too_long', 'a' * 21),
#     ('empty', ''),
#     ('sneaky', '         '),
#     ('special', '!@#$%^&*()[]{};<>?/'),
#     ('blacklisted', 'nonurlfriendly!!!'),
#     ('blacklisted', 'jerk'),
# ])
# @pytest.mark.usefixtures('db_session')
# def test_exception_on_creating_user_with_invalid_username(db_session, _reason, test_username):
#     with pytest.raises(AssertionError):
#         new_user = User(username=test_username, password='irrelevent_password')
#         db_session.add(new_user)
#         db_session.commit()


# @pytest.mark.usefixtures('db_session')
# def test_exception_on_creating_user_with_no_password(db_session):
#     with pytest.raises(IntegrityError):
#         new_user = User(username='valid_username')

#         db_session.add(new_user)
#         db_session.commit()


# @pytest.mark.usefixtures('db_session')
# def test_exception_on_creating_user_with_not_unique_username(db_session):
#     with pytest.raises(IntegrityError):
#         duplicated_username = 'valid_username'
#         password = 'irrelevant_password'

#         existing_user = User(username=duplicated_username, password=password)
#         duplicated_user = User(username=duplicated_username, password=password)

#         db_session.add(existing_user)
#         db_session.add(duplicated_user)
#         db_session.commit()
