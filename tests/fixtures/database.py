import pytest
from tensorhive.database import db, create_boilerplate_app


@pytest.fixture(scope='module')
def test_client():
    flask_app = create_boilerplate_app(db)

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app.test_client()

    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()


@pytest.fixture(scope='function')
def db_session(test_client, new_reservation):
    print('[DB SESSION START]')
    # Create the database and the database table
    db.create_all()

    # Insert user data
    db.session.add(new_reservation)

    # Commit the changes for the users
    db.session.commit()
    yield db.session  # this is where the testing happens!

    db.drop_all()
    print('[DB SESSION END]')
