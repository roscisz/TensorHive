from tensorhive.core.violation_handlers.ProtectionHandler import ProtectionHandler
from tensorhive.core.utils.decorators.override import override
import logging
log = logging.getLogger(__name__)


class MessageSendingBehaviour():

    def _send_message_to_unauthorized_sessions(self, message, connection, unauthorized_sessions):
        '''Sends a mesage to all user's terminal sessions within given connection (node)'''
        for session in unauthorized_sessions:
            command = 'echo "{msg}" | write {username} {session}'.format(
                msg=message,
                username=session['username'],
                session=session['session'])
            output = connection.run_command(command, stop_on_errors=False)
            connection.join(output)
            log.info('Violation warning sent to {}'.format(session['username']))

    def trigger_action(self, connection, unauthorized_sessions):
        self._send_message_to_unauthorized_sessions(
            'You are violating someone else\'s reservation! Please, logout!', connection, unauthorized_sessions)
