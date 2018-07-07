import logging
import connexion
from tensorhive.config import API_CONFIG


class APIServer():
    def start(self):
        # TODO Enable debug mode
        # TODO Read settings from config
        logging.basicConfig(level=logging.INFO)
        app = connexion.FlaskApp(__name__)
        app.add_api(API_CONFIG.API_SPECIFICATION_FILE,
                    arguments={'title': API_CONFIG.API_TITLE},
                    resolver=connexion.RestyResolver('tensorhive.api.api'))
        app.run(port=API_CONFIG.API_SERVER_PORT)


if __name__ == '__main__':
    APIServer().start()

# SWagger UI http://0.0.0.0:9090/v1.0/ui/#/default
# import logging

# import connexion
# from connexion.resolver import RestyResolver

# logging.basicConfig(level=logging.INFO)

# if __name__ == '__main__':
#     app = connexion.FlaskApp(__name__)
#     app.add_api('api_specification.yml',
#                 arguments={'title': 'RestyResolver Example'},
#                 resolver=RestyResolver('api'),
#                 specification_dir='swagger/')
#     app.run(port=9090)