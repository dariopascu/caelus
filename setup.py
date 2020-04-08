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

with (_here / 'requirements.txt').open() as req:
    requirements = [i.replace('\n', '') for i in req]

with open(_here / 'README.md', encoding='utf-8') as f:
    long_description = f.read()

aws_packages = ['boto3==1.9.66',
                'awscli==1.16.314', ]

azure_packages = ['azure==4.0.0',
                  'azure-identity==1.2.0',
                  'msrestazure==0.6.2', ]

google_packages = ['google-api-python-client==1.8.0',
                   'google-cloud-storage==1.27.0', ]

setup(
    name='caelus',
    packages=['caelus'],
    version=version['__version__'],
    description='Multi-cloud utils package',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='dariopascu',
    url='https://github.com/dariopascu/caelus',
    download_url='https://github.com/dariopascu/caelus/archive/v0.0.1.tar.gz',
    license='MIT License',
    install_requires=requirements,
    include_package_data=True,
    python_requires='>=3.7',
    keywords=['cloud', 'aws', 'azure', 'gcp'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.7'],
    extras_require={
        'aws': requirements + aws_packages,  # pip install caelus[aws]
        'az': requirements + azure_packages,  # pip install caelus[az]
        'gcp': requirements + google_packages,  # pip install caelus[gcp]
        'all': requirements + aws_packages + azure_packages + google_packages
    }
)
