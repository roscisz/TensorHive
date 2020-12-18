import click

from tensorhive.database import ensure_db_with_current_schema
from tensorhive.core.utils.colors import orange, green, red
from tensorhive.models.Group import Group
from tensorhive.models.Role import Role
from tensorhive.models.User import User
from tensorhive.models.Restriction import Restriction
from datetime import datetime


class AccountCreator:
    '''
    It asks all the necessary questions in order to set up a new account.
    Takes user's input from CLI.
    Exits on Ctrl+C
    '''

    def __init__(self):
        ensure_db_with_current_schema()
        self._check_restrictions()
        # Prepare empty ORM object
        self.new_user = User()

    def run_prompt(self):
        self._ask_for_username()
        self._ask_for_email()
        self._ask_for_password()
        self._ask_for_role()
        if self._create_user():
            self._add_to_default_groups()

    def _create_user(self) -> bool:
        try:
            self.new_user.save()
        except Exception as e:
            click.echo(red('Account creation failed due to an error: {}.'.format(e)))
            return False
        else:
            click.echo(green('Account created successfully.'))
            return True

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
                click.echo(red('Invalid username: {reason}.'.format(reason=e)))
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
                click.echo(red('Invalid email: {reason}.'.format(reason=e)))
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
                assert password1 == password2, orange('Passwords don\'t match, please try again.')
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
            click.echo(red('Unknown error - could not assign role.'))

    def _add_to_default_groups(self):
        groups = Group.get_default_groups()
        for group in groups:
            group.add_user(self.new_user)

        if len(groups) > 0:
            click.echo(green('Account added to the existing default groups'))

    @classmethod
    def _check_restrictions(cls):
        # If there are already users in the DB, don't bother
        if User.query.count() > 0:
            return

        if Restriction.query.count() == 0:
            if click.confirm(orange('There are no permissions specified') + ' - that means, that by default '
                             'users will not have access to any resources. Would you like to create '
                             'a default permission together with a default group now? (All users '
                             'would have access to every resource)', default=True):
                default_group = Group(name='users')
                default_group._is_default = True
                default_group.save()

                default_restriction = Restriction(name='can always use everything', starts_at=datetime.utcnow(),
                                                  is_global=True)
                default_restriction.apply_to_group(default_group)

                click.echo(green('Created a default group: {} and a permission "{}" '
                           .format(default_group.name, default_restriction.name) + 'allowing access to every resource '
                                                                                   'at any time.'))
            else:
                click.echo(orange('[•] OK - not creating any permissions. Remember that you need to define permissions'
                           ' in order for users to be able to access the resources.'))
