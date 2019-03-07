from setuptools import setup, find_packages
from hyperdock import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="hyperdock",
    version=__version__,
    description="A distributed hyperparameter optimizer for machine learning that lives in Docker",
    long_description=long_description,
    keywords="hyperparameter,optimization,docker",
    author="Erik Gärtner",
    author_email="erik@gartner.io",
    url="http://github.com/ErikGartner/hyperdock",
    license="Apache 2.0",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved",
        "Natural Language :: English",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3.6",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    include_package_data=False,
    install_requires=[
        "certifi==2018.11.29",
        "chardet==3.0.4",
        "click==7.0",
        "contextlib2==0.5.5",
        "docker-pycreds==0.4.0",
        "docker==3.7.0",
        "idna==2.8",
        "numpy==1.16.2",
        "psutil==5.6.0",
        "pymongo==3.7.2",
        "python-pushover==0.4",
        "pyyaml==3.13",
        "requests==2.21.0",
        "schema==0.7.0",
        "scikit-learn==0.20.3",
        "scipy==1.2.1",
        "six==1.12.0",
        "sklearn==0.0",
        "slackclient==1.3.1",
        "urllib3==1.24.1",
        "websocket-client==0.54.0",
    ],
    extras_require={"tests": ["mongomock==3.15.0", "nose==1.3.7"]},
    entry_points={
        "console_scripts": [
            "hyperdock-supervisor = hyperdock.supervisor.main:launch_supervisor",
            "hyperdock-worker = hyperdock.worker.main:launch_worker",
        ]
    },
)
