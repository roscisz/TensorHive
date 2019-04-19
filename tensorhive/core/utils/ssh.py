from paramiko.rsakey import RSAKey


def generate_cert(path, replace=False):
    path.touch(mode=0o600, exist_ok=replace)
    key = RSAKey.generate(2048)
    key.write_private_key_file(str(path))
    return key
