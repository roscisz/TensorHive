# import pytest
# from sqlalchemy.exc import OperationalError, IntegrityError
from tensorhive.models.User import User

def test_user_creation(db_session, new_user, new_admin):
    db_session.add(new_user)
    db_session.commit()
    assert new_user.id

    db_session.add(new_admin)
    db_session.commit()
    assert new_admin.id

    # TODO Move to test_role_model.py
    try:
        roles = db_session.query(User).filter_by(id=new_admin.id).one().role_names
    except:
        roles = []
    finally:
        assert set(roles) == set(['admin', 'user'])







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
