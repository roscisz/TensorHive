import pytest
import connexion
from flask_cors import CORS
from unittest.mock import patch
from tensorhive.app.web.AppServer import API_SERVER, API

API_URI = 'http://' + API_SERVER.HOST + ':' + str(API_SERVER.PORT) + '/' + API.URL_PREFIX
HEADERS = {'Authorization': 'Bearer XXX', 'Content-Type': 'application/json'}

patch('flask_jwt_extended.get_jwt_identity', lambda: 1).start()
patch('flask_jwt_extended.get_jwt_claims', lambda: {'roles': ['user']}).start()
patch('flask_jwt_extended.view_decorators.verify_jwt_in_request', lambda: None).start()


@pytest.fixture(scope='module')
def client():
    app = connexion.FlaskApp(__name__)
    app.add_api('../../tensorhive/api/' + API.SPEC_FILE,
                arguments={
                    'title': API.TITLE,
                    'url_prefix': API.URL_PREFIX,
                    'RESPONSES': API.RESPONSES
                },
                resolver=connexion.RestyResolver(API.IMPL_LOCATION),
                strict_validation=True)
    CORS(app.app)
    return app.app.test_client()
