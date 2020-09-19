import pytest
import connexion
from flask_cors import CORS
from tensorhive.app.web.AppServer import API_SERVER, API


API_URI = 'http://' + API_SERVER.HOST + ':' + str(API_SERVER.PORT) + '/' + API.URL_PREFIX


@pytest.fixture
def client():
    app = connexion.FlaskApp(__name__)
    app.add_api('../../tensorhive/api/' + API.SPEC_FILE,
                arguments={
                    'title': API.TITLE,
                    'version': API.VERSION,
                    'url_prefix': API.URL_PREFIX,
                    'RESPONSES': API.RESPONSES
                },
                resolver=connexion.RestyResolver(API.IMPL_LOCATION),
                strict_validation=True)
    CORS(app.app)
    return app.app.test_client()
