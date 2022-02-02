from tensorhive.core.violation_handlers.ProtectionHandler import ProtectionHandler
from tensorhive.core.utils.decorators import override
from typing import Generator, Dict, List, Any
from inspect import cleandoc
import logging
from tensorhive.core import ssh
log = logging.getLogger(__name__)


class MessageSendingBehaviour():
    def get_warning_message(self, data: Dict[str, Any]):
        message_template = cleandoc(
            '''{red_bg}{white_fg}
            You are violating the GPU reservation rules!
            Please stop all your computations immediately.{reset}
            {red_fg}{bold}
            GPUs: {gpus}{reset}

            If this was by a mistake, please do not do this again.
            Before starting any GPU-related computations, check the TensorHive reservations calendar.

            Regards,
            TensorHive bot
            {reset}
            ''')

        message = message_template.format(
            gpus=data['GPUS'],
            white_fg=r'\e[97m',
            red_fg=r'\e[31m',
            light_red_fg=r'\e[101m',
            red_bg=r'\e[41m',
            green_bg=r'\e[42m',
            bold=r'\e[1m',
            reset=r'\e[0m')
        return message

    def _build_single_command(self, recipient: str, tty, msg: str) -> str:
        '''Example: 'echo "Example message" | write example_username pts/1' '''
        command = 'echo -e "{msg}" | tee /dev/{tty}'.format(
            msg=msg,
            tty=tty['TTY'])
        return command

    def merged_commands(self, recipient: str, ttys: List[Dict], msg: str) -> str:
        '''
        Concatenates multiple commands into one,
        It allows using ssh connection only once instead of multiple times (for each tty separately)

        Example: 'echo ... | write A pty/1; echo ... | write A pty/2; echo ... | write A pty/3'
        '''
        assert len(ttys) > 0, 'List cannot be empty!'
        commands = [self._build_single_command(recipient, tty, msg) for tty in ttys]
        return ';'.join(commands)

    @override
    def trigger_action(self, violation_data: Dict[str, Any]) -> None:
        '''Sends a mesage to all user's terminal sessions within node'''
        message = self.get_warning_message(data=violation_data)
        intruder_username = violation_data['INTRUDER_USERNAME']

        for hostname in violation_data['SSH_CONNECTIONS']:
            node_connection = violation_data['SSH_CONNECTIONS'][hostname]

            node_sessions = ssh.node_tty_sessions(node_connection)
            tty_sessions = [sess for sess in node_sessions if sess['USER'] == intruder_username]

            if not len(tty_sessions):
                return

            command = self.merged_commands(recipient=intruder_username, ttys=tty_sessions, msg=message)
            node_connection.run_command(command)

            for tty in tty_sessions:
                log.warning('Violation warning sent to {username}, {tty_name}@{hostname}'.format(
                    username=intruder_username,
                    tty_name=tty,
                    hostname=hostname
                ))
