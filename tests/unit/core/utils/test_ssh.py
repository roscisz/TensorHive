import pytest
import os
import stat
import tensorhive.core.utils.ssh as sut
from paramiko.rsakey import RSAKey


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
    assert oct(os.stat(str(key_path))[stat.ST_MODE])[-3:] == '600'


def test_generate_cert_with_replace_generates_different_key(saved_key, key_path):
    new_key = sut.generate_cert(key_path, replace=True)
    assert saved_key != new_key
