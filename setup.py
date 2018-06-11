from setuptools import setup, find_packages
from hyperdock import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='hyperdock',
    version=__version__,
    description='A simple program for distributed hyperparameter optimization in Docker',
    long_description=long_description,
    keywords='hyperparameter optimization,docker',
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
        'certifi==2018.4.16',
        'chardet==3.0.4',
        'click==6.7',
        'docker-pycreds==0.3.0',
        'docker==3.3.0',
        'idna==2.6',
        'mock==2.0.0',
        'mongomock==3.10.0',
        'numpy==1.14.4',
        'pbr==4.0.4',
        'pymongo==3.6.1',
        'requests==2.18.4',
        'scikit-learn==0.19.1',
        'scipy==1.1.0',
        'sentinels==1.0.0',
        'six==1.11.0',
        'sklearn==0.0',
        'urllib3==1.22',
        'websocket-client==0.48.0',
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
