from tensorhive.core.utils.decorators import override
from tensorhive.core import ssh
from typing import Generator, Dict, List, Any, Optional
import logging
log = logging.getLogger(__name__)


class UserProcessKillingBehaviour:
    '''
    When violation is triggered by ProtectionHandler, this behaviour tries to kill violating processes by logging into
    the target host via SSH as the process owner and executing the proper kill command.
    '''

    @override
    def trigger_action(self, violation_data: Dict[str, Any]) -> None:

        username = violation_data['INTRUDER_USERNAME']

        for hostname in violation_data['VIOLATION_PIDS']:
            config, pconfig = ssh.build_dedicated_config_for(hostname, username)
            client = ssh.get_client(config, pconfig)

            for pid in violation_data['VIOLATION_PIDS'][hostname]:
                command = 'kill {}'.format(pid)

                log.warning('Killing process {} on host {}, user: {}'.format(pid, hostname, username))
                output = ssh.run_command(client, command)

                if output[hostname].exception:
                    e = output[hostname].exception
                    log.warning('Cannot kill process on host {}, user: {}, reason: {}'.format(hostname, username, e))
