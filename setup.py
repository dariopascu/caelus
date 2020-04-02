#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from pathlib import Path

from setuptools import setup, find_packages

_here = Path(os.path.abspath(os.path.dirname(__file__)))

version = dict()
with (_here / 'squall' / '__init__.py').open() as f:
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
    name='squall',
    version=version['__version__'],
    description='Multi-cloud utils package',
    url='https://github.com/dariopascu/squall',
    license=license_info,
    packages=find_packages(),
    install_requires=requirements + aws_packages + azure_packages + data_packages,
    include_package_data=True,
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.7'],
    extras_require={
        'aws': aws_packages,  # pip install cloud_utils[aws]
        'az': azure_packages,  # pip install cloud_utils[az]
        'storage': aws_packages + azure_packages + data_packages,  # pip install cloud_utils[storage]
    }
)
