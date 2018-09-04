from gunicorn.app.base import BaseApplication
from flask import Flask, render_template
from flask_cors import CORS
from tensorhive.config import APP_CONFIG
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


def start_server():
    log.info('[•] Starting Vue web app with {} backend'.format(
        APP_CONFIG.SERVER_BACKEND))
    
    if APP_CONFIG.SERVER_BACKEND == 'gunicorn':
        options = {
            'bind': '{addr}:{port}'.format(addr=APP_CONFIG.SERVER_HOST, port=APP_CONFIG.SERVER_PORT),
            'workers': APP_CONFIG.NUM_WORKERS,
            'loglevel': APP_CONFIG.SERVER_LOGLEVEL
        }
        log.info('[✔] Web App avaliable at: http://{} '.format(options['bind']))
        GunicornStandaloneApplication(app, options).run()
    else:
        raise NotImplementedError('Selected backend is not supported yet.')


if __name__ == '__main__':
    start_server()
