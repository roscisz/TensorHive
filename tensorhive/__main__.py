import signal
import time
from tensorhive.config import CONFIG
from tensorhive.core_anew.managers.TensorHiveManager import TensorHiveManager
from tensorhive.core_anew.services.MonitoringService import MonitoringService
from tensorhive.core_anew.monitors.GPUMonitor import GPUMonitor

from tensorhive.core_anew.utils.SigShutdownHandler import SigShutdownHandler



def main():
    termination_handler = SigShutdownHandler()

    services_to_inject = [MonitoringService(monitors=[GPUMonitor()
                                                      # Add more monitors here
                                                      ])
                          # Add more services here
                          ]

    manager = TensorHiveManager(services=services_to_inject)
    manager.start()
    while True:
        #time.sleep(CONFIG['TH__SLEEP_IN_S'])

        if termination_handler.should_terminate:
            manager.shutdown()
            break

    manager.join()


if __name__ == "__main__":
    main()
