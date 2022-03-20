"""A setuptools based module for PIP installation."""
# Docs/example setup.py: https://github.com/pypa/sampleproject/blob/master/setup.py

import os
from setuptools import setup, find_packages

__VERSION__ = '0.1.1'
base_dir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(base_dir, 'README.md')) as readme:
    readme_contents = readme.read()

with open('requirements.txt') as requirements:
    requirements_list = [l.strip() for l in requirements.readlines()]

setup(
    name='QtPyUltimarc',
    version=__VERSION__,
    long_description=readme_contents,
    url='https://github.com/robabram/QtPyUltimarc',
    # These packages may be imported after the egg is installed.
    packages=find_packages(exclude=['tests']),
    install_requires=requirements_list,
    entry_points={
        'console_scripts': [
            'ultimarc = ultimarc.main',
            'ultimarc_cli = ultimarc.tools.__main__:run',
        ],
    },
)
