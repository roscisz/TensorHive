import logging
import connexion
from tensorhive.config import API_CONFIG
from tensorhive.database import db_session
from flask_cors import CORS


class APIServer():
    def start(self):
        # TODO Enable debug mode
        # TODO Read settings from config
        logging.basicConfig(level=logging.INFO)
        app = connexion.FlaskApp(__name__)

        @app.app.teardown_appcontext
        def shutdown_session(exception=None):
            db_session.remove()

        app.add_api(API_CONFIG.API_SPECIFICATION_FILE,
                    arguments={'title': API_CONFIG.API_TITLE},
                    resolver=connexion.RestyResolver('tensorhive.api.api'),
                    strict_validation=True)
        CORS(app.app)
        app.run(port=API_CONFIG.API_SERVER_PORT)


if __name__ == '__main__':
    #Default Swagger UI URL: http://0.0.0.0:9876/v1.0/ui/#/default
    APIServer().start()



