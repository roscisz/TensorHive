from tensorhive.core.violation_handlers.ProtectionHandler import ProtectionHandler
from tensorhive.core.utils.decorators import override
from typing import Generator, Dict, List, Any
from inspect import cleandoc
import logging
log = logging.getLogger(__name__)


class MessageSendingBehaviour():
    def get_warning_message(self, data: Dict[str, Any]):
        message_template = cleandoc(
            '''{red_bg}{white_fg}
            You are violating {owner_name}\'s reservation!
            Please, stop all your computations immidiately.{reset}
            {red_fg}{bold}
            Host: {hostname}
            Name: GPU{gpu_id}, {gpu_name}{reset}
            UUID: {gpu_uuid}

            Current reservation ends on {red_fg}{reservation_end}{reset}.

            If this was by a mistake, please do not do this again.
            Before starting any GPU-related computations, see TensorHive reservations calendar.
            Please visit: {green_bg}http://cuda3:5000{reset}

            Regards,
            TensorHive bot
            {reset}
            ''')

        message = message_template.format(
            owner_name=data['RESERVATION_OWNER_USERNAME'],
            hostname=data['HOSTNAME'],
            gpu_id=data['GPU_ID'],
            gpu_name=data['GPU_NAME'],
            gpu_uuid=data['UUID'],
            reservation_end=data['RESERVATION_END'],
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

    def merged_commands(self, recipient: str, ttys: List[str], msg: str) -> str:
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
        tty_sessions = violation_data['TTY_SESSIONS']
        intruder_username = violation_data['INTRUDER_USERNAME']
        connection = violation_data['SSH_CONNECTION']

        if not len(tty_sessions):
            return

        command = self.merged_commands(recipient=intruder_username, ttys=tty_sessions, msg=message)
        connection.run_command(command)  # , stop_on_errors=False)

        for tty in tty_sessions:
            log.warning('Violation warning sent to {username}, {tty_name}'.format(
                username=intruder_username,
                tty_name=tty))
