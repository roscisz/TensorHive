import time
from utils import StoppableThread


class MonitoringHandler:
    def handle_monitoring(self, infrastructure):
        raise NotImplementedError()


class Monitor:
    def get_key(self):
        raise NotImplementedError()

    def discover(self, client):
        raise NotImplementedError()

    def monitor(self, client, output):
        raise NotImplementedError()


class MonitoringWorker(StoppableThread):
    def __init__(self, client, node_data, monitors):
        StoppableThread.__init__(self)
        self.client = client
        self.node_data = node_data
        self.monitors = monitors

    def monitor(self, client, node_data):
        for monitor in self.monitors:
            node_data[monitor.get_key()] = monitor.monitor(client, node_data[monitor.get_key()])

    def do_run(self):
        self.monitor(self.client, self.node_data)
        # TODO: sleep period as arg
        time.sleep(1)

    def finalize(self):
        self.client.close()


class MonitoringService(StoppableThread):
    def __init__(self, monitors, handlers, connection_manager):
        StoppableThread.__init__(self)
        print('Starting the monitoring service...')
        self.monitors = monitors
        self.handlers = handlers
        self.connection_manager = connection_manager

        self.infrastructure = dict()
        self.workers = []

    def discover_node(self, client, monitors):
        return {monitor.get_key(): monitor.discover(client) for monitor in monitors}

    def add_node(self, node):
        if node not in self.infrastructure.keys():
            connection = self.connection_manager.ensure_connection(node)
            self.infrastructure[node] = self.discover_node(connection, self.monitors)
            worker = MonitoringWorker(connection, self.infrastructure[node], self.monitors)
            self.workers.append(worker)
            worker.start()

    def add_handler(self, handler):
        self.handlers.append(handler)

    def do_run(self):
        for handler in self.handlers:
            handler.handle_monitoring(self.infrastructure)
        # TODO: sleep period as arg
        time.sleep(5)

    def finalize(self):
        for worker in self.workers:
            worker.join()

    def shutdown(self):
        print('Shutting down monitoring workers...')
        for worker in self.workers:
            worker.shutdown()
        StoppableThread.shutdown(self)
