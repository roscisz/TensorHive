from setuptools import setup, find_packages

setup(
    name = 'tensorhive',
    version = '0.0.1',
    packages = find_packages(),
    description = 'Lightweight resource management tool for distributed TensorFlow in clusters with SSH connectivity',
    author = 'Pawel Rosciszewski',
    author_email = 'pawel.rosciszewski@pg.edu.pl',
    url = 'https://github.com/roscisz/TensorHive',
    download_url = 'https://github.com/roscisz/TensorHive/archive/0.0.1.tar.gz',
    keywords = 'distributed machine learning tensorflow resource management',
    install_requires=['kernelhive']
)
