from tensorhive.config import DB
from flask import Flask
import flask_sqlalchemy
from sqlalchemy_utils import database_exists
import logging
log = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DB.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app


db = flask_sqlalchemy.SQLAlchemy()
flask_app = create_app()


# TODO Refactor 
from flask_migrate import Migrate
from tensorhive.models.User import User
from tensorhive.models.Reservation import Reservation
from tensorhive.models.RevokedToken import RevokedToken
from tensorhive.models.Role import Role
migrate = Migrate(flask_app, db)

def init_db() -> None:
    '''Creates the database, tables (if they does not exist)'''
    # Import all modules that define models so that
    # they could be registered properly on the metadata.
    from tensorhive.models.User import User
    from tensorhive.models.Reservation import Reservation
    from tensorhive.models.RevokedToken import RevokedToken
    from tensorhive.models.Role import Role
    from tensorhive.cli import prompt_to_create_first_account
    
    with flask_app.app_context():
        if database_exists(DB.SQLALCHEMY_DATABASE_URI):
            log.info('[•] Database found ({path})'.format(path=DB.SQLALCHEMY_DATABASE_URI))
            if db.session.query(User).count() == 0:
                prompt_to_create_first_account()
        else:
            db.create_all()
            log.info('[✔] Database created ({path})'.format(path=DB.SQLALCHEMY_DATABASE_URI))
            prompt_to_create_first_account()
