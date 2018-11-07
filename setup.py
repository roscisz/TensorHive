from setuptools import setup, find_packages
from pathlib import PosixPath
import tensorhive
import shutil


def copy_configuration_files():
    target_dir = PosixPath.home() / '.config/TensorHive'
    # destination is given explicitly, just in case we'd want to rename file during the installation process
    hosts_config_path = {'src': 'hosts_config.ini', 'dst': str(target_dir / 'hosts_config.ini')}
    config_path = {'src': 'main_config.ini', 'dst': str(target_dir / 'main_config.ini')}

    def safe_copy(src: str, dst: str):
        '''It won't override existing configuration'''
        if PosixPath(dst).exists():
            print('Skipping, file already exists: {}'.format(dst))
        else:
            shutil.copy(src, dst)
            print('Creating file {}'.format(dst))

    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        safe_copy(hosts_config_path['src'], hosts_config_path['dst'])
        safe_copy(config_path['src'], config_path['dst'])
    except Exception:
        # FIXME Prints are only visible with `pip install foobar --verbose`
        print('Unable to copy configuration files to {}'.format(target_dir))


# TODO Add platform and license
setup(
    name='tensorhive',
    version=tensorhive.__version__,
    license='Apache License 2.0',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'tensorhive = tensorhive.__main__:main'
        ],
    },
    description='Lightweight computing resource management tool for executing distributed TensorFlow programs',
    author='Pawel Rosciszewski, Michal Martyniak, Filip Schodowski, Tomasz Menet',
    author_email='pawel.rosciszewski@pg.edu.pl',
    url='https://github.com/roscisz/TensorHive',
    download_url='https://github.com/roscisz/TensorHive/archive/{}.tar.gz'.format(tensorhive.__version__),
    keywords='distributed machine learning tensorflow resource management',
    install_requires=[
        'parallel-ssh',
        'passlib',
        'sqlalchemy',
        'sqlalchemy-utils',
        'click',
        'connexion',
        'flask_cors',
        'flask_jwt_extended',
        'gunicorn',
        'coloredlogs',
        'Safe',
        'python-usernames'
    ],
    zip_safe=False
)

copy_configuration_files()