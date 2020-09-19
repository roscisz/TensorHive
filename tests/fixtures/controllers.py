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


# @pytest.fixture(scope='function')
# def skip_jwt(monkeypatch):
#     monkeypatch.setattr('flask_jwt_extended.view_decorators.verify_jwt_in_request', lambda: None)
#
#
# @pytest.fixture(scope='function')
# def skip_admin(monkeypatch):
#     def no_verify():
#         pass
#
#     # monkeypatch.setattr('flask_jwt_extended.view_decorators.verify_jwt_in_request', lambda: None)
#     monkeypatch.setattr('tensorhive.authorization.admin_required', no_verify)
#
