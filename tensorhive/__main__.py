import signal
import time
# from tensorhive.config import CONFIG
# from tensorhive.core.TensorHiveManager import TensorHiveManager

# stop = False
from tensorhive.core_anew.connections.SSHConnector import SSHConnector

def main():
    '''THIS IS ONLY TEMPORARY SIMLIFICATION'''
    beka = SSHConnector()

    # # TODO: read server hostname, port host list and command from commandline
    # manager = TensorHiveManager(
    #     hostname=CONFIG['THManager']['server']['hostname'],
    #     port=CONFIG['THManager']['server']['port']
    # )
    # manager.start()

    # def shutdown(signum, frame):
    #     manager.shutdown()
    #     global stop
    #     stop = True

    # signal.signal(signal.SIGINT, shutdown)
    # signal.signal(signal.SIGTERM, shutdown)

    # while not stop:
    #     time.sleep(5)

    # manager.join()
    


if __name__ == "__main__":
    main()
