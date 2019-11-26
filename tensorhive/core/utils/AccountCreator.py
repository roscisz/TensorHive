import click

from tensorhive.database import init_db
from tensorhive.models.Role import Role
from tensorhive.models.User import User


class AccountCreator:
    '''
    It asks all the necessary questions in order to set up a new account.
    Takes user's input from CLI.
    Exits on Ctrl+C
    '''

    def __init__(self):
        init_db()
        # Prepare empty ORM object
        self.new_user = User()

    def run_prompt(self):
        self._ask_for_username()
        self._ask_for_email()
        self._ask_for_password()
        self._ask_for_role()
        self._create_user()

    def _create_user(self):
        try:
            self.new_user.save()
        except Exception as e:
            click.echo('Account creation failed due to an error: {}.'.format(e))
        else:
            click.echo('Account created successfully.')

    def _ask_for_username(self):
        '''
        Process is repeated until username becomes valid.
        If so, it assignes the vaule to the ORM object.
        '''
        valid_username_provided = False
        while not valid_username_provided:
            try:
                username = click.prompt('[1/4] UNIX username', type=str)
                self.new_user.username = username
            except click.Abort:
                raise
            except Exception as e:
                click.echo('Invalid username: {reason}.'.format(reason=e))
            else:
                valid_username_provided = True

    def _ask_for_email(self):
        valid_email_provided = False
        while not valid_email_provided:
            try:
                email = click.prompt('[2/4] email (for TensorHive warnings only)', type=str)
                self.new_user.email = email
            except click.Abort:
                raise
            except Exception as e:
                click.echo('Invalid email: {reason}.'.format(reason=e))
            else:
                valid_email_provided = True

    def _ask_for_password(self):
        # Useful aliases
        prompt_for_password = lambda message: click.prompt(message, type=str, hide_input=True)
        password_length_requirement = 'at least {} characters'.format(self.new_user.min_password_length)
        first_password_message = '[3/4] password ({})'.format(password_length_requirement)
        repeated_password_message = '[3/4] repeat password'

        valid_password_provided = False
        while not valid_password_provided:
            try:
                password1 = prompt_for_password(message=first_password_message)
                self.new_user.password = password1
                password2 = prompt_for_password(message=repeated_password_message)
                assert password1 == password2, 'Passwords don\'t match, please try again.'
            except click.Abort:
                raise
            except Exception as error_msg:
                click.echo(str(error_msg))
            else:
                valid_password_provided = True

    def _ask_for_role(self):
        try:
            make_admin = click.confirm('[4/4] admin account?', default=False)

            # TODO Refactor roles: admin or not instead of two mutually exclusive 'admin' and 'user
            self.new_user.roles.append(Role(name='user'))
            if make_admin:
                self.new_user.roles.append(Role(name='admin'))
        except click.Abort:
            raise
        except Exception:
            click.echo('Unknown error - could not assign role.')
