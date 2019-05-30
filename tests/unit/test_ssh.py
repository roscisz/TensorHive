import pytest
from tensorhive.core import ssh

# def test_config_builder_exceptions_with_incorrect_arguments():


def test_config_builder_with_good_arguments():
    config = ssh.build_dedicated_config_for('hostname', 'username')
    assert config == {
        'hostname': {
            'user': 'username',
            'pkey': '~/.ssh/id_rsa'
        }
    }


@pytest.mark.parametrize('host,user', [
    (None, None),
    ('foo', None),
    (None, 'bar'),
])
def test_config_builder_failure_with_invalid_arguments(host, user):
    with pytest.raises(AssertionError):
        ssh.build_dedicated_config_for(host, user)


# def test_stdout_for_inexisting_host():
#     pass