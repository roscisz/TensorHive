from setuptools import setup, find_packages
import tensorhive


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
    description='A user-friendly GPU management tool for distributed machine learning workloads',
    author='Pawel Rosciszewski, Michal Martyniak, Filip Schodowski',
    author_email='pawel.rosciszewski@pg.edu.pl',
    url='https://github.com/roscisz/TensorHive',
    download_url='https://github.com/roscisz/TensorHive/archive/{}.tar.gz'.format(tensorhive.__version__),
    keywords='reservation monitoring machine learning distributed tensorflow pytorch',
    install_requires=[
        'parallel-ssh==1.9.1',
        'passlib==1.7.1',
        'sqlalchemy==1.3.0',
        'sqlalchemy-utils==0.33.8',
        'click==7.0',
        'werkzeug==0.16.1',
        'connexion==1.5.3',
        'flask_cors==3.0.7',
        'flask_jwt_extended==3.13.1',
        'gunicorn==19.9.0',
        'coloredlogs==10.0',
        'Safe==0.4',
        'python-usernames==0.2.3'
    ],
    zip_safe=False
)
