import logging
import connexion
from tensorhive.config import API_CONFIG
from tensorhive.database import db_session
from flask_cors import CORS
log = logging.getLogger(__name__)


class APIServer():
    def start(self):
        app = connexion.FlaskApp(__name__)
        
        @app.app.teardown_appcontext
        def shutdown_session(exception=None):
            db_session.remove()

        app.add_api(API_CONFIG.SPECIFICATION_FILE,
                    arguments={
                        'title': API_CONFIG.TITLE, 
                        'version': API_CONFIG.VERSION,
                        'url_prefix': API_CONFIG.URL_PREFIX
                    },
                    resolver=connexion.RestyResolver(API_CONFIG.VERSION_FOLDER),
                    strict_validation=True)
        CORS(app.app)
        log.info('[•] Starting API server with {} backend'.format(API_CONFIG.SERVER_BACKEND))
        log.info('API documentation (Swagger UI) available at: http://{host}:{port}/{url_prefix}/ui/'.format(
            host=API_CONFIG.SERVER_HOST, 
            port=API_CONFIG.SERVER_PORT,
            url_prefix=API_CONFIG.URL_PREFIX))
        app.run(server=API_CONFIG.SERVER_BACKEND,
                host=API_CONFIG.SERVER_HOST,
                port=API_CONFIG.SERVER_PORT,
                debug=API_CONFIG.SERVER_DEBUG)


if __name__ == '__main__':
    APIServer().start()
