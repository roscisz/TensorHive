import signal
import time
from tensorhive.config import CONFIG
from tensorhive.core_anew.managers.TensorHiveManager import TensorHiveManager
from tensorhive.core_anew.services.MonitoringService import MonitoringService
from tensorhive.core_anew.monitors.GPUMonitor import GPUMonitor


class GracefulKiller():
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.shutdown_gracefully)
        signal.signal(signal.SIGTERM, self.shutdown_gracefully)

    def shutdown_gracefully(self, signum, frame):
        self.kill_now = True


def main():
    termination_handler = GracefulKiller()

    services_to_inject = [MonitoringService(monitors=[GPUMonitor()
                                                      # Add more monitors here
                                                      ])
                          # Add more services here
                          ]

    manager = TensorHiveManager(services=services_to_inject)
    manager.start()
    while True:
        time.sleep(CONFIG['TH__SLEEP_IN_S'])

        if termination_handler.kill_now:
            manager.shutdown()
            break

        manager.join()


if __name__ == "__main__":
    main()
