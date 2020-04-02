#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from pathlib import Path

from distutils.core import setup

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
    packages=['squall'],
    version=version['__version__'],
    description='Multi-cloud utils package',
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
        'aws': aws_packages,  # pip install squall[aws]
        'az': azure_packages,  # pip install squall[az]
        'storage': aws_packages + azure_packages + data_packages,  # pip install squall[storage]
    }
)
