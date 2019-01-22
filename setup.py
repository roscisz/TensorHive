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
        'parallel-ssh==1.9.1',
        'passlib==1.7.1',
        'sqlalchemy==1.2.14',
        'sqlalchemy-utils==0.33.8',
        'click==7.0',
        'connexion==1.5.3',
        'flask_cors==3.0.7',
        'flask_jwt_extended==3.13.1',
        'gunicorn==19.9.0',
        'coloredlogs==10.0',
        'Safe==0.4',
        'python-usernames==0.2.2'
    ],
    zip_safe=False
)

copy_configuration_files()
