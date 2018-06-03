from setuptools import setup, find_packages
from hyperdock import __version__

tests_require = [
    'mock',
    'nose',
    'coverage',
    'yanc',
    'preggy',
    'tox',
    'ipdb',
    'coveralls',
    'sphinx',
]

setup(
    name='hyperdock',
    version=__version__,
    description='A hyperoptimizer living in Docker',
    long_description='''A hyperoptimizer living in Docker''',
    keywords='',
    author='Erik Gärtner',
    author_email='erik@gartner.io',
    url='http://github.com/ErikGartner/hyperdock',
    license='',
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
        # add your dependencies here
        # remember to use 'package-name>=x.y.z,<x.y+1.0' notation (this way you get bugfixes)
    ],
    extras_require={
        'tests': tests_require,
    },
    entry_points={
        'console_scripts': [
            # add cli scripts here in this form:
            # 'hyperdock=hyperdock.cli:main',
            'hyperdock-supervisor=hyperdock.supervisor.cli'
        ],
    },
)
