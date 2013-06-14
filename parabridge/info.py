#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

# parabridge information.
# Copyright 2013 Grigory Petrov
# See LICENSE for details.

import os
import pkg_resources

NAME_SHORT = "parabridge"
VER_MAJOR = 0
VER_MINOR = 1
try:
  VER_TXT = pkg_resources.require( NAME_SHORT )[ 0 ].version
##  Installing via 'setup.py develop'?
except pkg_resources.DistributionNotFound:
  VER_BUILD = 0
  VER_TXT = ".".join( map( str, [ VER_MAJOR, VER_MINOR, VER_BUILD ] ) )
DIR_THIS = os.path.dirname( os.path.abspath( __file__ ) )
DIR_HOME = os.path.expanduser( '~' )
NAME_FULL = "Paradox to SQLite bridge."
DESCR = """
{s_name_short} v. {s_ver_txt}\\n\\n
A simple python daemon that can dynamically sync paradox database with
SQLite database.
""".replace( '\n', '' ).replace( '\\n', '\n' ).strip().format(
  s_name_short = NAME_SHORT,
  s_ver_txt = VER_TXT )

COMM_PORT = 17963
COMM_ADDR = 'http://localhost:{0}/'.format( COMM_PORT )
FILE_CFG = os.path.join( DIR_HOME, '.{0}'.format( NAME_SHORT ) )

