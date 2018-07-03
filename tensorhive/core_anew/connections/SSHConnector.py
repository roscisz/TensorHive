import spur
import json
from tensorhive.core_anew.monitors.GPUMonitor import GPUMonitor

class SSHConnector():
    '''THIS IS ONLY TEMPORARY SIMPLIFICATION'''
    def __init__(self):
        shell_sessions = []

        # TODO replace hardcoded parameters
        foo_shell = spur.SshShell(hostname='localhost', username='miczi')

        #mocks
        shell_sessions.append(foo_shell)
        gpu_monitor = GPUMonitor()

        for session in shell_sessions:
            gpu_monitor.refresh(session)
            #TODO this should be done by some handler (e.g. printing handler)
            print(json.dumps(gpu_monitor.gathered_data, indent=1))
            
