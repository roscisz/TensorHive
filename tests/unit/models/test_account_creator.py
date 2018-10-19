from tensorhive.cli import prompt_to_create_first_account
from click.testing import CliRunner
import click
import pytest


@pytest.mark.parametrize('test_name, test_input', [
    ('will_pass', ['y', 'some_username', 'some_password', 'y'])
])
def test_prompts(tables, test_name, test_input):
    mocked_input = '\n'.join(test_input)

    @click.command()
    def click_wrapper():
        output = prompt_to_create_first_account()
        assert output
        
    result = CliRunner().invoke(click_wrapper, input=mocked_input)
    assert result.exception is None, 'Account creator failed'
