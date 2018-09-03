from setuptools import setup, find_packages
import tensorhive

setup(
    name = 'tensorhive',
    version = tensorhive.__version__,
    packages = find_packages(),
    package_data = {'tensorhive': ['scripts/*', 'static/*', 'api/*']},
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
    install_requires=['parallel-ssh', 'passlib', 'sqlalchemy', 'sqlalchemy-utils', 'click', 'connexion', 'flask_cors'],
    include_package_data=True,
    zip_safe=False
)
