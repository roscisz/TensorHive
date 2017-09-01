import signal
import time

from tensorhive.TensorHiveManager import TensorHiveManager

stop = False

def main():
    # TODO: read server hostname, port host list and command from commandline
    manager = TensorHiveManager('localhost', 31333)
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
