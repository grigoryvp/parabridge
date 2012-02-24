#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

import os
import sys
import argparse
import subprocess
import xmlrpclib

COMM_PORT = 17963

def start() :
  sFile = '{0}/parabridge_daemon.py'.format( sys.path[ 0 ] )
  subprocess.Popen( [ 'python', sFile, str( COMM_PORT ) ] )

def stop() :
  oSrv = xmlrpclib.ServerProxy( 'http://localhost:{0}/'.format( COMM_PORT ) )
  oSrv.stop()

oParser = argparse.ArgumentParser( description = "Paradox to MySQL bridge." )
oSubparsers = oParser.add_subparsers()
oSubparsers.add_parser( 'start' ).set_defaults( handler = start )
oSubparsers.add_parser( 'stop' ).set_defaults( handler = stop )
oParser.parse_args().handler()

