from setuptools import setup, find_packages
import tensorhive


def copy_configuration_files():
    import shutil
    from pathlib import PosixPath
    target_dir = PosixPath.home() / '.config/TensorHive'
    relative_ssh_config_path = 'tensorhive/ssh_config.ini'
    relative_config_path = 'tensorhive/default_config.ini'
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(relative_ssh_config_path, str(target_dir))
        shutil.copy(relative_config_path, str(target_dir))
        # FIXME Prints are only visible with `pip install foobar --verbose`
        print('Configuration .ini files copied to {}'.format(target_dir))
    except:
        print('Unable to copy configuration files to {}'.format(relative_config_path, target_dir))

# TODO Add platform and license
setup(
    name = 'tensorhive',
    version = tensorhive.__version__,
    license='Apache License 2.0',
    packages = find_packages(),
    include_package_data=True,
    entry_points = {
        'console_scripts': [
            'tensorhive = tensorhive.__main__:main'
        ],
    },
    description = 'Lightweight computing resource management tool for executing distributed TensorFlow programs',
    author = 'Pawel Rosciszewski',
    author_email = 'pawel.rosciszewski@pg.edu.pl',
    url = 'https://github.com/roscisz/TensorHive',
    download_url = 'https://github.com/roscisz/TensorHive/archive/0.1.1.tar.gz',
    keywords = 'distributed machine learning tensorflow resource management',
    install_requires=[
        'parallel-ssh', 
        'passlib', 
        'sqlalchemy', 
        'sqlalchemy-utils', 
        'click', 
        'connexion', 
        'flask_cors', 
        'gunicorn', 
        'coloredlogs'
    ],
    zip_safe=False
)

copy_configuration_files()