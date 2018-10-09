from tensorhive.cli import prompt_to_create_first_account
from click.testing import CliRunner
import click
import pytest

@pytest.mark.parametrize('_, test_input', [
    ('will_pass', ['y', 'some_username', 'some_password', 'y'])
    #('will_fail', ['y', 'some_username', 'asdf', 'y'])
])
def test_prompts(db_session, test_input, _):
    mocked_input = '\n'.join(test_input)

    @click.command()
    def hello():
        result = prompt_to_create_first_account()
        assert result

    result = CliRunner().invoke(hello, input=mocked_input)
    assert result.exception is None, 'Account creator failed'
