from setuptools import setup, find_packages
import tensorhive


def copy_configuration_files():
    import shutil
    from pathlib import PosixPath
    target_dir = PosixPath.home() / '.config/TensorHive'
    # destination is given explicitely, just in case we'd want to rename file during the installation process
    hosts_config_path = {'src': 'hosts_config.ini', 'dst': str(target_dir / 'hosts_config.ini')}
    config_path = {'src': 'main_config.ini', 'dst': str(target_dir / 'main_config.ini')}
    
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(hosts_config_path['src'], hosts_config_path['dst'])
        shutil.copy(config_path['src'], config_path['dst'])
        # FIXME Prints are only visible with `pip install foobar --verbose`
        print('Configuration .ini files copied to {}'.format(target_dir))
    except:
        print('Unable to copy configuration files to {}'.format(target_dir))

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
    author = 'Pawel Rosciszewski, Michał Martyniak, Filip Schodowski, Tomasz Menet',
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