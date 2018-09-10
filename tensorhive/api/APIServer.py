import logging
import connexion
from tensorhive.config import API, API_SERVER
from tensorhive.database import db_session
from flask_cors import CORS
log = logging.getLogger(__name__)


class APIServer():
    def start(self):
        app = connexion.FlaskApp(__name__)
        
        @app.app.teardown_appcontext
        def shutdown_session(exception=None):
            db_session.remove()

        app.add_api(API.SPEC_FILE,
                    arguments={
                        'title': API.TITLE, 
                        'version': API.VERSION,
                        'url_prefix': API.URL_PREFIX
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
    APIServer().start()

if __name__ == '__main__':
    start_api_server()
