from tensorhive.core.violation_handlers.ProtectionHandler import ProtectionHandler
from tensorhive.core.utils.decorators.override import override
import logging
log = logging.getLogger(__name__)


class MessageSendingBehaviour():

    message = 'You are violating someone else\'s reservation! Please, logout!'
    command_body = 'echo "{msg}" | write {username} {session_name}'

    def _merged_command(self, sessions):
        '''
        Concatenates multiple commands into one, 
        It allows using ssh connection only once instead of multiple times
        '''
        commands = [self._formatted_command(session) for session in sessions]
        merged_command = ';'.join(commands)
        return merged_command

    def _formatted_command(self, session):
        '''Returns a single bash command formatted with given data'''
        return self.command_body.format(
            msg=self.message,
            username=session['username'],
            session_name=session['session'])

    def _send_message_to_unauthorized_sessions(self, connection, unauthorized_sessions):
        '''Sends a mesage to all user's terminal sessions within given connection (node)'''
        command = self._merged_command(unauthorized_sessions)
        output = connection.run_command(command, stop_on_errors=False)
        connection.join(output)
        log.info('Violation warning sent')

    def trigger_action(self, connection, unauthorized_sessions):
        self._send_message_to_unauthorized_sessions(
            connection, unauthorized_sessions)
