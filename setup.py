#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='mprpc',
    version='0.1.0',
    description='msgpack rpc',
    packages=['mprpc', ],
    package_data={'': ['README.md']},
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)