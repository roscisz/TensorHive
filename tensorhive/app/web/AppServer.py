from gunicorn.app.base import BaseApplication
from flask import Flask, render_template
from flask_cors import CORS
import tensorhive
from tensorhive.config import APP_SERVER, API_SERVER, API
from tensorhive.core.utils.colors import green
import json
from pathlib import PosixPath
import logging
log = logging.getLogger(__name__)

app = Flask(__name__,
            static_folder='./dist/static',
            template_folder='./dist')
CORS(app)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')


class GunicornStandaloneApplication(BaseApplication):
    '''
    Refactored version of http://docs.gunicorn.org/en/stable/custom.html
    It allows to lauch gunicorn server outside the command line
    '''

    def __init__(self, app, options={}):
        self.options = options
        self.application = app
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def _inject_api_endpoint_to_app():
    '''
    Allows for changing API URL that web app is sending requests to.
    Web app expects API URL to be specified in `config.json`.
    The file must not exist, it will be created automatically if needed.
    '''
    try:
        web_app_json_config_path = PosixPath(__file__).parent / 'dist/static/config.json'
        data = {
            'apiPath': 'http://{}:{}/{}'.format(
                API.URL_HOSTNAME,
                API_SERVER.PORT,
                API.URL_PREFIX),
            'version': tensorhive.__version__
        }
        # Overwrite current file content/create file if it does not exist
        with open(str(web_app_json_config_path), 'w') as json_file:
            json.dump(data, json_file)
    except IOError as e:
        log.error('Could inject API endpoint URL, reason: ' + str(e))
    except Exception as e:
        log.critical('Unknown error: ' + str(e))
    else:
        log.debug('API URL injected successfully: {}'.format(data))


def start_server():
    _inject_api_endpoint_to_app()
    log.info('[⚙] Starting Vue web app with {} backend'.format(
        APP_SERVER.BACKEND))

    if APP_SERVER.BACKEND == 'gunicorn':
        options = {
            'bind': '{addr}:{port}'.format(addr=APP_SERVER.HOST, port=APP_SERVER.PORT),
            'workers': APP_SERVER.WORKERS,
            'loglevel': APP_SERVER.LOG_LEVEL
        }
        log.info(green('[✔] Web App available at: http://{}:{}'.format(API.URL_HOSTNAME, APP_SERVER.PORT)))
        GunicornStandaloneApplication(app, options).run()
    else:
        raise NotImplementedError('Selected backend is not supported yet.')


if __name__ == '__main__':
    start_server()
