from setuptools import setup, find_packages
import tensorhive
import os

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


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
    description='A user-friendly GPU management tool for distributed machine learning workloads',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Pawel Rosciszewski, Michal Martyniak, Filip Schodowski',
    author_email='pawel.rosciszewski@pg.edu.pl',
    url='https://github.com/roscisz/TensorHive',
    download_url='https://github.com/roscisz/TensorHive/archive/{}.tar.gz'.format(tensorhive.__version__),
    keywords='gpu reservation calendar monitoring machine learning distributed tensorflow pytorch',
    install_requires=[
        'alembic==1.0.3',
        'bcrypt==3.1.7',
        'certifi==2020.12.5',
        'cffi==1.14.5',
        'chardet==4.0.0',
        'Click==7.0',
        'clickclick==20.10.2',
        'coloredlogs==10.0',
        'connexion==2.3.0',
        'cryptography==3.2.1',
        'Flask==1.1.4',
        'Flask-Cors==3.0.7',
        'Flask-JWT-Extended==3.13.1',
        'gevent==21.1.2',
        'greenlet==1.1.0',
        'gunicorn==19.9.0',
        'humanfriendly==9.1',
        'idna==2.10',
        'inflection==0.5.1',
        'itsdangerous==1.1.0',
        'Jinja2==2.11.3',
        'jsonschema==2.6.0',
        'Mako==1.1.4',
        'MarkupSafe==1.1.1',
        'openapi-spec-validator==0.2.9',
        'paramiko==2.7.2',
        'parallel-ssh==1.9.1',
        'passlib==1.7.1',
        'pycparser==2.20',
        'PyJWT==1.7.1',
        'PyNaCl==1.4.0',
        'python-dateutil==2.8.1',
        'python-editor==1.0.4',
        'python-usernames==0.2.3',
        'PyYAML==5.3.1',
        'requests==2.25.1',
        'Safe==0.4',
        'six==1.16.0',
        'SQLAlchemy==1.3.0',
        'SQLAlchemy-Utils==0.33.8',
        'ssh2-python==0.26.0',
        'stringcase==1.2.0',
        'swagger_ui_bundle==0.0.8',
        'urllib3==1.26.4',
        'Werkzeug==0.16.1',
        'zope.event==4.5.0',
        'zope.interface==5.4.0',
    ],
    zip_safe=False
)
