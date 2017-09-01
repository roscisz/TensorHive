from setuptools import setup, find_packages

setup(
    name = 'tensorhive',
    version = '0.1.1',
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
    install_requires=['kernelhive>=1.2.7', 'pyrrd'],
    include_package_data=True,
    zip_safe=False
)
