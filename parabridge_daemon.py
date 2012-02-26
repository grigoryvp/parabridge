#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

import sys
import argparse
import threading
import time
import socket
import os
import json
import re
from SimpleXMLRPCServer import SimpleXMLRPCServer

# Allow to import packages from 'vendor' subfolder.
sys.path.append( '{0}/vendor'.format( sys.path[ 0 ] ) )

import pyparadox

class Config( object ) :

  m_oTimeReloadLast = None
  m_mItems = { 'tasks' : [] }

  @classmethod
  def reload( self ) :
    sPath = os.path.expanduser( "~/.parabridge" )
    if os.path.exists( sPath ) :
      self.m_mItems.update( json.load( open( sPath ) ) )
      self.m_oTimeReloadLast = time.localtime()
      Worker.instance().cfgChanged()

  @classmethod
  def get( self ) :
    return self.m_mItems

  @classmethod
  def timeReloadLast( self ) :
    return self.m_oTimeReloadLast

class Worker( threading.Thread ) :

  m_oInstance = None

  def __init__( self ) :
    super( Worker, self ).__init__()
    self.m_fShutdown = False
    self.m_mResults = {}

  def run( self ) :
    mCfg = Config().get()
    while not self.m_fShutdown :
      if self.m_fCfgChanged :
        mCfg = Config().get()
        self.m_fCfgChanged = False
      for mTask in mCfg[ 'tasks' ] :
        self.processTask( mTask[ 'name' ], mTask[ 'src' ], mTask[ 'dst' ] )
      time.sleep( 1 )

  def processTask( self, i_sName, i_sSrc, i_sDst ) :
    def setRes( i_sTxt ) :
      self.m_mResults[ i_sName ] = i_sTxt
    if not os.path.exists( i_sSrc ) :
      return setRes( "Path \"{0}\" not found.".format( i_sSrc ) )
    if not os.path.isdir( i_sSrc ) :
      return setRes( "Path \"{0}\" is not a directory.".format( i_sSrc ) )
    sTime = time.strftime( '%Y.%m.%d %H:%M:%S' )
    setRes( "Processed at {0}.".format( sTime ) )

  def shutdown( self ) :
    self.m_fShutdown = True

  @classmethod
  def instance( self ) :
    if not self.m_oInstance :
      self.m_oInstance = Worker()
    return self.m_oInstance

  def cfgChanged( self ) : self.m_fCfgChanged = True

  def results( self ) : return self.m_mResults

class Server( SimpleXMLRPCServer, object ) :

  def __init__( self, i_nPort ) :
    gAddr = ( 'localhost', i_nPort )
    super( Server, self ).__init__( gAddr, logRequests = False )
    self.fShutdown = False
    self.register_function( self.stop )
    self.register_function( self.status )
    self.register_function( self.cfg_changed )

  def serve_forever( self ) :
    while not self.fShutdown :
      self.handle_request()

  def stop( self ) :
    self.fShutdown = True
    return True

  def status( self ) :
    sMsg = """Daemon is running.
      \tConfiguration reloaded: {0}""".format(
      time.strftime( '%Y.%m.%d %H:%M:%S', Config().timeReloadLast() ) )
    mResults = Worker.instance().results()
    for sKey in sorted( mResults.keys() ) :
      sMsg += "\n{0}:\n\t {1}".format( sKey, mResults[ sKey ] )
    return re.sub( '\t', ' ', re.sub( ' +', ' ', sMsg ) )

  def cfg_changed( self ) :
    Config().reload()
    return True

oParser = argparse.ArgumentParser( description = "Parabridge daemon" )
oParser.add_argument( 'port', type = int, help = "Port to listen on" )
oArgs = oParser.parse_args()

Config.reload()
Worker.instance().start()
try :
  Server( oArgs.port ).serve_forever()
except socket.error :
  ##  Unable to bind to port if already started.
  pass
finally :
  Worker.instance().shutdown()

