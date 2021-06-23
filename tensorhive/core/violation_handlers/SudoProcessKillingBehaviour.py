from tensorhive.core.utils.decorators import override
from tensorhive.core.managers.SSHConnectionManager import SSHConnectionManager
import tensorhive.core.ssh as ssh
from typing import Dict, Any
import logging
log = logging.getLogger(__name__)


class SudoProcessKillingBehaviour:
    '''
    When violation is triggered by ProtectionHandler, this behaviour tries to kill violating processes by logging into
    the target host via SSH using the TensorHive configured account and executing the proper kill command with sudo.
    '''
    @override
    def trigger_action(self, violation_data: Dict[str, Any]) -> None:
        username = violation_data['INTRUDER_USERNAME']

        for hostname in violation_data['VIOLATION_PIDS']:
            connection = violation_data['SSH_CONNECTIONS'][hostname]

            for pid in violation_data['VIOLATION_PIDS'][hostname]:
                command = 'sudo kill {}'.format(pid)
                connection.run_command(command)

                log.warning('Sudo killing process {} on host {}, user: {}'.format(pid, hostname, username))
                output = ssh.run_command(connection, command)

                if output[hostname].exception:
                    e = output[hostname].exception
                    log.warning('Cannot kill process on host {}, user: {}, reason: {}'.format(hostname, username, e))
