from setuptools import setup, find_packages
from tensorhive.config import CONFIG
setup(
    name = 'tensorhive',
    version = CONFIG.VERSION,
    packages = find_packages(),
    package_data = {'tensorhive': ['scripts/*', 'static/*']},
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
    install_requires=['parallel-ssh', 'click', 'colorama'],
    include_package_data=True,
    zip_safe=False
)
