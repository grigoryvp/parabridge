#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

import os
import sys
import argparse
import subprocess
import xmlrpclib
import json
import socket
import logging

COMM_PORT = 17963
COMM_ADDR = 'http://localhost:{0}/'.format( COMM_PORT )
HELP_APP = """Paradox to SQLite bridge. This tool monitors specified
  Paradox database and reflects all changes to specified SQLite database
  that can be used by any application that has problems with Paradox."""
HELP_START = """Starts background process that will monitor Paradox
  databse."""
HELP_STOP = """Stops background process that was previously started with
  'start'."""
HELP_STATUS = """Shows current background process status."""
HELP_TASK_ADD = """Adds task with specified name (name can be used later
  to manage tasks), path to source Paradox database directory ('~' will
  be expanded) and path to destination SQLite database file ('~' will
  be expanded)."""
HELP_TASK_DEL = """Deletes task with specified name."""
HELP_TASK_LIST = """Displays list of added tasks."""

class Config( object ) :

  m_mItems = { 'tasks' : [] }
  sPath = os.path.expanduser( "~/.parabridge" )
  if os.path.exists( sPath ) :
    m_mItems.update( json.load( open( sPath ) ) )

  @classmethod
  def set( self, i_sName, i_uVal ) :
    self.m_mItems[ i_sName ] = i_uVal
    sPath = os.path.expanduser( "~/.parabridge" )
    json.dump( self.m_mItems, open( sPath, 'w' ) )
    try :
      oSrv = xmlrpclib.ServerProxy( COMM_ADDR )
      oSrv.cfg_changed()
    except socket.error :
      pass

  @classmethod
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

def status( i_oArgs ) :
  try :
    oSrv = xmlrpclib.ServerProxy( COMM_ADDR )
    print( oSrv.status() )
  except socket.error :
    print( "Daemon is not running." )

def task_add( i_oArgs ) :
  for mTask in Config.get( 'tasks' ) :
    if i_oArgs.task_name == mTask[ 'name' ] :
      logging.warning( "Already has '{0}' task".format( i_oArgs.task_name ) )
      return
  mTask = {
    'name' : i_oArgs.task_name,
    'src' : i_oArgs.task_src,
    'dst' : i_oArgs.task_dst
  }
  Config.set( 'tasks', Config.get( 'tasks' ) + [ mTask ] )

def task_del( i_oArgs ) :
  lTasks = Config.get( 'tasks' )
  for mTask in lTasks :
    if i_oArgs.task_name == mTask[ 'name' ] :
      lTasks.remove( mTask )
      Config.set( 'tasks', lTasks )
      return
  logging.warning( "No task named '{0}'".format( i_oArgs.task_name ) )

def task_list( i_oArgs ) :
  lTasks = Config.get( 'tasks' )
  if 0 == len( lTasks ) :
    print( "Tasks list is empty." )
    return
  for mTask in lTasks :
    print( "{0}\n  Source: {1}\n  Destination: {2}".format(
      mTask[ 'name' ],
      mTask[ 'src' ],
      mTask[ 'dst' ] ) )

oParser = argparse.ArgumentParser( description = HELP_APP )
oSubparsers = oParser.add_subparsers()
oSubparser = oSubparsers.add_parser( 'start', help = HELP_START )
oSubparser.set_defaults( handler = start )
oSubparser = oSubparsers.add_parser( 'stop', help = HELP_STOP )
oSubparser.set_defaults( handler = stop )
oSubparser = oSubparsers.add_parser( 'status', help = HELP_STATUS )
oSubparser.set_defaults( handler = status )
oSubparser = oSubparsers.add_parser( 'task_add', help = HELP_TASK_ADD )
oSubparser.set_defaults( handler = task_add )
oSubparser.add_argument( 'task_name' )
oSubparser.add_argument( 'task_src' )
oSubparser.add_argument( 'task_dst' )
oSubparser = oSubparsers.add_parser( 'task_del', help = HELP_TASK_DEL )
oSubparser.set_defaults( handler = task_del )
oSubparser.add_argument( 'task_name' )
oSubparser = oSubparsers.add_parser( 'task_list', help = HELP_TASK_LIST )
oSubparser.set_defaults( handler = task_list )
oArgs = oParser.parse_args()
oArgs.handler( oArgs )

