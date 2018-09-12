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
        'certifi==2018.8.24',
        'chardet==3.0.4',
        'click==6.7',
        'docker-pycreds==0.3.0',
        'docker==3.5.0',
        'idna==2.7',
        'mock==2.0.0',
        'mongomock==3.11.1',
        'numpy==1.15.1',
        'pbr==4.2.0',
        'pymongo==3.7.1',
        'python-pushover==0.4',
        'requests==2.19.1',
        'schema==0.6.8',
        'scikit-learn==0.19.2',
        'scipy==1.1.0',
        'slackclient==1.2.1',
        'sentinels==1.0.0',
        'six==1.11.0',
        'sklearn==0.0',
        'urllib3==1.23',
        'websocket-client==0.53.0',
    ],
    extras_require={
        'tests': [
            'nose',
        ],
    },
    entry_points={
        'console_scripts': [
            'hyperdock-supervisor = hyperdock.supervisor.main:launch_supervisor',
            'hyperdock-worker = hyperdock.worker.main:launch_worker',
        ],
    },
)
