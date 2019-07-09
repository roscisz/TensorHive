import pytest
import os
import stat
import tensorhive.core.ssh as sut
from tensorhive.config import SSH
from paramiko.rsakey import RSAKey


def test_config_builder_with_good_arguments():
    config, _ = sut.build_dedicated_config_for('hostname', 'username')
    assert config == {
        'hostname': {
            'user': 'username',
            'pkey': SSH.KEY_FILE
        }
    }


@pytest.mark.parametrize('host,user', [
    (None, None),
    ('foo', None),
    (None, 'bar'),
])
def test_config_builder_failure_with_invalid_arguments(host, user):
    with pytest.raises(AssertionError):
        sut.build_dedicated_config_for(host, user)


@pytest.fixture
def key_path(tmp_path):
    return tmp_path / 'key'


@pytest.fixture
def saved_key(key_path):
    return sut.generate_cert(key_path)


def test_generate_cert_generated_cert_is_loadable(saved_key, key_path):
    RSAKey.from_private_key_file(str(key_path))


def test_generate_cert_generating_twice_throws_exception(saved_key, key_path):
    with pytest.raises(FileExistsError):
        sut.generate_cert(key_path)


def test_generate_cert_generated_cert_has_proper_permissions(saved_key, key_path):
    mode = os.stat(str(key_path)).st_mode
    assert stat.S_IMODE(mode) == 0o600


def test_generate_cert_with_replace_generates_different_key(saved_key, key_path):
    new_key = sut.generate_cert(key_path, replace=True)
    assert saved_key != new_key
