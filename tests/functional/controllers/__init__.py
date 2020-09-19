from unittest.mock import patch
from tensorhive.app.web.AppServer import API_SERVER, API

API_URI = 'http://' + API_SERVER.HOST + ':' + str(API_SERVER.PORT) + '/' + API.URL_PREFIX
HEADERS = {'Authorization': 'Bearer XXX', 'Content-Type': 'application/json'}

patch('tensorhive.authorization.admin_required', lambda x: x).start()
patch('flask_jwt_extended.view_decorators.verify_jwt_in_request', lambda: None).start()
