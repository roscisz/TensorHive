from tensorhive.core.violation_handlers.ProtectionHandler import ProtectionHandler
from tensorhive.core.utils.decorators.override import override
from typing import Generator, Dict, List
import logging
log = logging.getLogger(__name__)


class MessageSendingBehaviour():

    message = '''
    You are violating {leigitimate_owner_username}\'s reservation!
    Please, stop all your computations on {gpu_uuid}.
    '''
    command_body = 'echo "{msg}" | write {username} {tty_name}'

    def _merged_command(self, sessions: List):
        '''
        Concatenates multiple commands into one,
        It allows using ssh connection only once instead of multiple times (for each tty separately)

        Example: 'echo ... | write A pty/1; echo ... | write A pty/2; echo ... | write A pty/3'
        '''

        def formatted_command(session):
            '''Example: 'echo "Example message" | write example_username pts/1' '''
            formatted_message = self.message.format(
                leigitimate_owner_username=session['LEGITIMATE_USER'],
                gpu_uuid=session['GPU_UUID'])

            return self.command_body.format(
                msg=formatted_message,
                username=session['USER'],
                tty_name=session['TTY'])

        assert len(sessions) > 0, 'List cannot be empty!'
        commands = [formatted_command(session) for session in sessions]
        merged_command = ';'.join(commands)
        return merged_command

    def _send_message_to_ttys(self, connection, sessions):
        '''Sends a mesage to all user's terminal sessions within given connection (node)'''
        command = self._merged_command(sessions)
        _ = connection.run_command(command)#, stop_on_errors=False)

        for session in sessions:
            log.warning('Violation warning sent to {username}, {tty_name}'.format(
                username=session['USER'],
                tty_name=session['TTY']))

    @override
    def trigger_action(self, connection, unauthorized_sessions):
        self._send_message_to_ttys(connection, unauthorized_sessions)
