from setuptools import setup, find_packages
from hyperdock import __version__

setup(
    name='hyperdock',
    version=__version__,
    description='A simple program for distributed hyperparameter optimization in Docker',
    long_description='''A simple program for distributed hyperparameter optimization in Docker''',
    keywords='hyperparameter optimization,docker',
    author='Erik Gärtner',
    author_email='erik@gartner.io',
    url='http://github.com/ErikGartner/hyperdock',
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache 2.0',
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
        'decorator==4.3.0',
        'dill==0.2.7.1',
        'docker-pycreds==0.2.3',
        'docker==3.3.0',
        'future==0.16.0',
        'hyperopt==0.1',
        'idna==2.6',
        'mock==2.0.0',
        'mongomock==3.10.0',
        'networkx==1.11',
        'nose==1.3.7',
        'numpy==1.14.3',
        'pbr==4.0.3',
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
