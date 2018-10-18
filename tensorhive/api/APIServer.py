from tensorhive.config import API, API_SERVER, DB
from tensorhive.database import db, init_migrations, connexion_app_instance
from flask_cors import CORS
from tensorhive.authorization import init_jwt
import connexion
import logging
log = logging.getLogger(__name__)


# def connexion_app_instance():
#     app = connexion.FlaskApp(__name__)
#     app.app.config['SQLALCHEMY_DATABASE_URI'] = DB.SQLALCHEMY_DATABASE_URI
#     app.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#     return app


class APIServer():
    def run_forever(self):
        app = connexion_app_instance()
        print(__name__)
        init_jwt(app.app)

        @app.app.teardown_appcontext
        def shutdown_session(exception=None):
            db.session.remove()

        app.add_api(API.SPEC_FILE,
                    arguments={
                        'title': API.TITLE, 
                        'version': API.VERSION,
                        'url_prefix': API.URL_PREFIX,
                        'RESPONSES': API.RESPONSES
                    },
                    resolver=connexion.RestyResolver(API.IMPL_LOCATION),
                    strict_validation=True)
        CORS(app.app)
        log.info('[⚙] Starting API server with {} backend'.format(API_SERVER.BACKEND))
        log.info('[✔] API documentation (Swagger UI) available at: http://{host}:{port}/{url_prefix}/ui/'.format(
            host=API_SERVER.HOST, 
            port=API_SERVER.PORT,
            url_prefix=API.URL_PREFIX))
        app.run(server=API_SERVER.BACKEND,
                host=API_SERVER.HOST,
                port=API_SERVER.PORT,
                debug=API_SERVER.DEBUG)


def start_api_server():
    APIServer().run_forever()


if __name__ == '__main__':
    start_api_server()
