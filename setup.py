from setuptools import setup, find_packages
from hyperdock import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='hyperdock',
    version=__version__,
    description='A distributed hyperparameter optimizer for machine learning that lives in Docker',
    long_description=long_description,
    keywords='hyperparameter,optimization,docker',
    author='Erik Gärtner',
    author_email='erik@gartner.io',
    url='http://github.com/ErikGartner/hyperdock',
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    include_package_data=False,
    install_requires=[
        'nose==1.3.7',
        'sentinels==1.0.0',
        'six==1.11.0',
        'certifi==2018.10.15',
        'chardet==3.0.4',
        'click==7.0',
        'docker-pycreds==0.3.0',
        'docker==3.5.1',
        'idna==2.7',
        'numpy==1.15.3',
        'pymongo==3.7.2',
        'python-pushover==0.4',
        'requests==2.20.0',
        'schema==0.6.8',
        'scikit-learn==0.20.0',
        'scipy==1.1.0',
        'six==1.11.0',
        'slackclient==1.3.0',
        'urllib3==1.24',
        'websocket-client==0.53.0',
        'psutil==5.4.8',
    ],
    extras_require={
        'tests': [
            'nose',
            'mongomock==3.13.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'hyperdock-supervisor = hyperdock.supervisor.main:launch_supervisor',
            'hyperdock-worker = hyperdock.worker.main:launch_worker',
        ],
    },
)
