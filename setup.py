#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
import setuptools

setup(
  name="parabridge",
  version='0.1.2',
  description="A simple python daemon that can dynamically sync paradox database with SQLite database.",
  author='Grigory Petrov',
  author_email='grigory.v.p@gmail.com',
  url='http://bitbucket.org/eyeofhell/parabridge',
  scripts = [ 'parabridge.py' ],
  packages = [ 'parabridge_core' ],
  install_requires = [ 'pyparadox>=0.1.0' ],
  classifiers=[
    'Development Status :: 1 - Prototype',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: GPLv3',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Utilities' ])

