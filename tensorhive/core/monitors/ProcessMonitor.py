from tensorhive.core.monitoring import Monitor


class ProcessMonitor(Monitor):
    def __init__(self):
        self.processes = []

    def get_key(self):
        return 'processes'

    def discover(self, client):
        process_map = dict()
        for process in self.processes:
            _, stdout, _ = client.exec_command('pgrep -f "%s"' % process)
            process_map[process] = stdout.read().split('\n')[:-1]
        return process_map

    def monitor(self, client, output):
        return self.discover(client)

    def add_process(self, process):
        self.processes.append(process)
