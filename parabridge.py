#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

import os
import sys
import argparse
import subprocess
import xmlrpclib
import json

COMM_PORT = 17963

class Config( object ) :

  m_oInstance = None

  def __new__( i_oClass ) :
    if not i_oClass.m_oInstance :
      i_oClass.m_oInstance = super( Config, i_oClass ).__new__( i_oClass )
    return i_oClass.m_oInstance

  def __init__( self ) :
    self.m_mItems = {
      'tasks' : []
    }
    sPath = os.path.expanduser( "~/.parabridge" )
    if os.path.exists( sPath ) :
      self.m_mItems.update( json.load( open( sPath ) ) )

  def set( self, i_sName, i_uVal ) :
    self.m_mItems[ i_sName ] = i_uVal
    sPath = os.path.expanduser( "~/.parabridge" )
    json.dump( self.m_mItems, open( sPath, 'w' ) )

  def get( self, i_sName ) :
    return self.m_mItems[ i_sName ]

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

