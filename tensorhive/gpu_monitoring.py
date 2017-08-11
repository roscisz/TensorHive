import signal
import time

from kernelhive.management import Manager
from kernelhive.monitors.GPUMonitor import GPUMonitor
from kernelhive.monitoring_handlers.PrintingHandler import PrintingHandler

stop = False


def main():
    # TODO: read server hostname, port host list and command from commandline
    manager = Manager('localhost', 31333, [GPUMonitor()], [PrintingHandler()])
    manager.start()

    def shutdown(signum, frame):
        manager.shutdown()
        global stop
        stop = True

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    while not stop:
        time.sleep(5)

    manager.join()

if __name__ == "__main__":
    main()
