#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

import os
import sys
import argparse
import subprocess
import xmlrpclib
import json
import socket

COMM_PORT = 17963
COMM_ADDR = 'http://localhost:{0}/'.format( COMM_PORT )
HELP_APP = """Paradox to SQLite bridge. This tool monitors specified
  Paradox database and reflects all changes to specified SQLite database
  that can be used by any application that has problems with Paradox."""
HELP_START = """Starts background process that will monitor Paradox
  databse."""
HELP_STOP = """Stops background process that was previously started with
  'start'."""
HELP_TASK_ADD = """Adds task with specified name (name can be used later
  to manage tasks), path to source Paradox database directory and path
  to destination SQLite database file."""

class Config( object ) :

  m_oInstance = None

  def __new__( i_oClass ) :
    if not i_oClass.m_oInstance :
      i_oClass.m_oInstance = super( Config, i_oClass ).__new__( i_oClass )
    return i_oClass.m_oInstance

  def __init__( self ) :
    self.m_mItems = { 'tasks' : [] }
    sPath = os.path.expanduser( "~/.parabridge" )
    if os.path.exists( sPath ) :
      self.m_mItems.update( json.load( open( sPath ) ) )

  def set( self, i_sName, i_uVal ) :
    self.m_mItems[ i_sName ] = i_uVal
    sPath = os.path.expanduser( "~/.parabridge" )
    json.dump( self.m_mItems, open( sPath, 'w' ) )
    try :
      oSrv = xmlrpclib.ServerProxy( COMM_ADDR )
      oSrv.cfg_changed()
    except socket.error :
      pass

  def get( self, i_sName ) :
    return self.m_mItems[ i_sName ]

def start( i_oArgs ) :
  sFile = '{0}/parabridge_daemon.py'.format( sys.path[ 0 ] )
  subprocess.Popen( [ 'python', sFile, str( COMM_PORT ) ] )

def stop( i_oArgs ) :
  try :
    oSrv = xmlrpclib.ServerProxy( COMM_ADDR )
    oSrv.stop()
  except socket.error :
    pass

def task_add( i_oArgs ) :
  mTask = {
    'name' : i_oArgs.task_name,
    'src' : i_oArgs.task_src,
    'dst' : i_oArgs.task_dst
  }
  Config().set( 'tasks', Config().get( 'tasks' ) + [ mTask ] )

oParser = argparse.ArgumentParser( description = HELP_APP )
oSubparsers = oParser.add_subparsers()
oSubparser = oSubparsers.add_parser( 'start', help = HELP_START )
oSubparser.set_defaults( handler = start )
oSubparser = oSubparsers.add_parser( 'stop', help = HELP_STOP )
oSubparser.set_defaults( handler = stop )
oSubparser = oSubparsers.add_parser( 'task_add', help = HELP_TASK_ADD )
oSubparser.set_defaults( handler = task_add )
oSubparser.add_argument( 'task_name' )
oSubparser.add_argument( 'task_src' )
oSubparser.add_argument( 'task_dst' )
oArgs = oParser.parse_args()
oArgs.handler( oArgs )

