import os
import importlib
from werkzeug.wrappers import Request, Response
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.serving import make_server
from werkzeug.utils import redirect
from jsonrpc import JSONRPCResponseManager, dispatcher


class HTTPJSONRPCServer:
    def __init__(self, hostname, port, name, landing_page):
        self.landing_page = landing_page

        try:
            module = importlib.import_module(name)
            static_path = os.path.dirname(module.__file__) + '/static'
        except ImportError:
            static_path = os.path.join(os.getcwd(), 'static')

        self.dynamic_path = '/tmp/%s' % name
        if not os.path.exists(self.dynamic_path):
            os.mkdir(self.dynamic_path)

        application = SharedDataMiddleware(self.application, {'/': static_path})
        self.srv = make_server(hostname, port, application)

    @Request.application
    def application(self, request):
        if request.path == '/' and request.method == 'GET':
            return redirect(self.landing_page)

        path = request.path.split('/')
        if len(path) > 2 and path[1] == 'dynamic':
            filename = '/'.join([self.dynamic_path, path[2]])
            if os.path.isfile(filename):
                with open(filename, 'rb') as f:
                    data = f.read()
            else:
                data = None
            response = Response(data, mimetype='application/octet-stream')
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        response = JSONRPCResponseManager.handle(request.data, dispatcher)
        return Response(response.json, mimetype='application/json')

    def add_service(self, method):
        dispatcher.add_method(method)

    def server_forever(self):
        print('Starting the HTTPJSONServer at http://%s:%d' % (self.srv.host, self.srv.port))
        self.srv.serve_forever()

    def shutdown(self):
        print('Shutting down the HTTPJSONSever...')
        self.srv.shutdown()
