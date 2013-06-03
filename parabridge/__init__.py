#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

# parabridge command-line entry point.
# Copyright 2013 Grigory Petrov
# See LICENSE for details.

import os
import argparse
import subprocess
import xmlrpclib
import socket
import logging

import settings
import info


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


def start( _ ) :
  sFile = os.path.join( os.path.dirname( __file__ ), "parabridge_daemon.py" )
  subprocess.Popen( [ 'python', sFile, str( info.COMM_PORT ) ] )


def stop( _ ) :
  try :
    oSrv = xmlrpclib.ServerProxy( info.COMM_ADDR )
    oSrv.stop()
  except socket.error :
    pass


def status( _ ) :
  try :
    oSrv = xmlrpclib.ServerProxy( info.COMM_ADDR )
    print( oSrv.status() )
  except socket.error :
    print( "Daemon is not running." )


def task_add( m_args ) :
  sName = m_args[ 'task_name' ]
  sSrc = m_args[ 'task_src' ]
  sDst = m_args[ 'task_dst' ]
  if not settings.instance.taskAdd( sName, sSrc, sDst ) :
    logging.warning( "Already has '{0}' task".format( sName ) )


def task_del( m_args ) :
  if not settings.instance.taskDelByName( m_args[ 'task_name' ] ) :
    logging.warning( "No task named '{0}'".format( m_args[ 'task_name' ] ) )


def task_list( _ ) :
  lTasks = settings.instance.taskList()
  if 0 == len( lTasks ) :
    print( "Tasks list is empty." )
    return
  for mTask in lTasks :
    print( "{0}\n  Source: {1}\n  Destination: {2}".format(
      mTask[ 'name' ],
      mTask[ 'src' ],
      mTask[ 'dst' ] ) )


def main() :
  settings.instance.init( f_notify = True )
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
  oArgs.handler( vars( oArgs ) )

