from tensorhive.config import API, API_SERVER, DB
from tensorhive.database import db_session
from flask_cors import CORS
from tensorhive.authorization import init_jwt
import connexion
import logging
from tensorhive.core.utils.colors import green

log = logging.getLogger(__name__)


class APILogger:
    write = lambda message: log.debug(message)


class APIServer():
    def run_forever(self):
        app = connexion.FlaskApp(__name__)
        init_jwt(app.app)

        @app.app.teardown_appcontext
        def shutdown_session(exception=None):
            db_session.remove()

        app.add_api(API.SPEC_FILE,
                    arguments={
                        'title': API.TITLE,
                        'url_prefix': API.URL_PREFIX,
                        'RESPONSES': API.RESPONSES
                    },
                    resolver=connexion.RestyResolver(API.IMPL_LOCATION),
                    strict_validation=True)
        CORS(app.app)
        log.info('[⚙] Starting API server with {} backend'.format(API_SERVER.BACKEND))
        URL = 'http://{host}:{port}/{url_prefix}/ui/'.format(
            host=API.URL_HOSTNAME,
            port=API_SERVER.PORT,
            url_prefix=API.URL_PREFIX)
        log.info(green('[✔] API documentation (Swagger UI) available at: {}'.format(URL)))
        app.run(server=API_SERVER.BACKEND,
                host=API_SERVER.HOST,
                port=API_SERVER.PORT,
                debug=API_SERVER.DEBUG,
                log=APILogger)


def start_api_server():
    APIServer().run_forever()


if __name__ == '__main__':
    start_api_server()
