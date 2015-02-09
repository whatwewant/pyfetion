#!/usr/bin/env python
# coding=utf-8

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

MODULE_NAME = 'pyfetion'
VERSION = '1.1.5'
AUTHOR = 'Cole Smith'
AUTHOR_EMAIL = 'uniquecolesmith@gmail.com'
URL = 'https://github.com/whatwewant/pyfetion'

PACKAGES = [
    'pyfetion',
]

REQUIRES = [
    'requests',
]

try:
    with open('README.md', 'r') as fp:
        readme = fp.read()
except:
    readme = ''

try:
    with open('HISTORY.md', 'r') as fp:
        history = fp.read()
except:
    history = ''

setup(
    name = MODULE_NAME,
    version = VERSION, 
    description = 'Simple Fetion Message',
    long_description = readme + '\n' + history,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    url = URL,
    packages = PACKAGES,
    package_dir = {'pyfetion': 'pyfetion'},
    include_package_data = True,
    install_requires = REQUIRES,
    license = 'Apache 2.0',
    zip_safe = False,
    classifiers = (
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ),
)
