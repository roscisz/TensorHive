from tensorhive.core.violation_handlers.ProtectionHandler import ProtectionHandler
from tensorhive.core.utils.decorators.override import override
from typing import Generator, Dict, List, Any
from inspect import cleandoc
import logging
log = logging.getLogger(__name__)


class MessageSendingBehaviour():
    def get_warning_message(self, data: Dict[str, Any]):
        message_template = cleandoc(
            '''
            You are violating {owner_name}\'s reservation!
            Please, stop all your computations on {gpu_name} ({gpu_uuid}).
            ''')

        message = message_template.format(
            owner_name=data['RESERVATION_OWNER_USERNAME'],
            gpu_name=data['GPU_NAME'],
            gpu_uuid=data['UUID'])
        return message

    def _build_single_command(self, recipient: str, tty: str, msg: str) -> str:
        '''Example: 'echo "Example message" | write example_username pts/1' '''
        command = 'echo "{msg}" | write {intruder_name} {tty}'.format(
            msg=msg,
            intruder_name=recipient,
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
