from tensorhive.core.monitoring import Monitor

timeout_prefix = 'timeout 2 '


class GPUMonitor(Monitor):
    def get_key(self):
        return 'gpu'

    def discover(self, client):
        gpus = {}
        _, stdout, _ = client.exec_command('nvidia-smi -L')
        gpu_descrs = stdout.read().split('\n')[:-1]
        for gpu_descr in gpu_descrs:
            name, model, uuid = gpu_descr.split(': ')
            model = model[:-6]
            uuid = uuid[:-1]
            gpus[uuid] = {}
            gpus[uuid]['name'] = name
            gpus[uuid]['model'] = model
        return gpus

    def check_process_owner(self, client, pid):
        _, stdout, _ = client.exec_command('ps -o user %s' % pid)
        return stdout.read().split('\n')[1]

    def monitor_processes(self, client, uuid):
        processes = []
        _, stdout, _ = client.exec_command('%s nvidia-smi pmon -c 1 -i %s' % (timeout_prefix, uuid))
        outputs = stdout.read().split('\n')[2:-1]
        for output in outputs:
            values = output.split()
            if values[1] is not '-':
                processes.append({'pid': values[1], 'owner': self.check_process_owner(client, values[1])})
        return processes

    def monitor_utilization(self, client, uuid):
        _, stdout, _ = client.exec_command('%s nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader -i %s' % (timeout_prefix, uuid))
        output = stdout.read().split()
        if not len(output):
            return 0
        return output[0]

    def monitor(self, client, gpus):
        for uuid in gpus.keys():
            gpus[uuid]['processes'] = self.monitor_processes(client, uuid)
            gpus[uuid]['utilization'] = self.monitor_utilization(client, uuid)
        return gpus

