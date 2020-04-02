#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from pathlib import Path

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

_here = Path(os.path.abspath(os.path.dirname(__file__)))

version = dict()
with (_here / 'caelus' / '__init__.py').open() as f:
    exec(f.readline(), version)

license_info = (_here / 'LICENSE').read_text()

with (_here / 'requirements.txt').open() as req:
    requirements = [i.replace('\n', '') for i in req]

aws_packages = ['boto3==1.9.66',
                'awscli==1.16.314', ]

azure_packages = ['azure==4.0.0',
                  'azure-identity==1.2.0',
                  'msrestazure==0.6.2', ]

data_packages = ['pandas==0.25.3',
                 'xlrd==1.2.0',
                 'pyarrow==0.15.1',
                 'openpyxl==3.0.3']
setup(
    name='caelus',
    packages=['caelus'],
    version=version['__version__'],
    description='Multi-cloud utils package',
    long_description=(_here / 'README.md').read_text(),
    author='dariopascu',
    url='https://github.com/dariopascu/squall',
    download_url='https://github.com/dariopascu/squall/archive/v0.0.1.tar.gz',
    license=license_info,
    install_requires=requirements + aws_packages + azure_packages + data_packages,
    include_package_data=True,
    python_requires='>=3.7',
    keywords=['cloud', 'aws', 'azure', 'gcp'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.7'],
    extras_require={
        'aws': aws_packages,  # pip install caelus[aws]
        'az': azure_packages,  # pip install caelus[az]
        'storage': aws_packages + azure_packages + data_packages,  # pip install caelus[storage]
    }
)
