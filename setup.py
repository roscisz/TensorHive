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
        'parallel-ssh==1.9.1',
        'passlib==1.7.1',
        'sqlalchemy==1.3.0',
        'sqlalchemy-utils==0.33.8',
        'click==7.0',
        'werkzeug==0.16.1',
        'connexion==2.3.0',
        'swagger_ui_bundle==0.0.8',
        'flask_cors==3.0.7',
        'flask_jwt_extended==3.13.1',
        'gunicorn==19.9.0',
        'coloredlogs==10.0',
        'Safe==0.4',
        'python-usernames==0.2.3',
        'stringcase==1.2.0',
        'alembic==1.0.3'
    ],
    zip_safe=False
)
