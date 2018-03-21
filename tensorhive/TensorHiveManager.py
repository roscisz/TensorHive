from management import Manager
from monitors.GPUMonitor import GPUMonitor
from monitoring_handlers.PrintingHandler import PrintingHandler
from monitoring_handlers.RRDHandler import RRDHandler
import logging


class TensorHiveManager(Manager):
    def __init__(self, hostname, port):
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        Manager.__init__(self, hostname, port, [], [], landing_page='dashboard.html')

    def configure_services(self):
        Manager.configure_services(self)
        # TODO: register TensorHiveManager JSON-RPC API
        # self.add_service(method...)

    def configure_monitors(self):
        self.monitors.append(GPUMonitor())

    def configure_handlers(self):
        self.handlers.append(PrintingHandler())
        self.handlers.append(RRDHandler('/tmp/tensorhive'))

    def get_module_name(self):
        return 'tensorhive'