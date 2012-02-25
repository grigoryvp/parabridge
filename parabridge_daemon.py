#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

import sys
import argparse
from SimpleXMLRPCServer import SimpleXMLRPCServer

class Config( object ) :

  m_oInstance = None

  def __new__( i_oClass ) :
    if not i_oClass.m_oInstance :
      i_oClass.m_oInstance = super( Config, i_oClass ).__new__( i_oClass )
    return i_oClass.m_oInstance

  def __init__( self ) :
    self.m_mItems = { 'tasks' : [] }
    reload()

  def reload( self ) :
    sPath = os.path.expanduser( "~/.parabridge" )
    if os.path.exists( sPath ) :
      self.m_mItems.update( json.load( open( sPath ) ) )

class Server( SimpleXMLRPCServer, object ) :

  def __init__( self, i_nPort ) :
    gAddr = ( 'localhost', i_nPort )
    mArgs = { 'allow_none' : True, 'logRequests' : False }
    super( Server, self ).__init__( gAddr, ** mArgs )
    self.fShutdown = False
    self.register_function( self.stop )

  def serve_forever( self ) :
    while not self.fShutdown :
      self.handle_request()

  def stop( self ) :
    self.fShutdown = True

  def cfg_changed( self ) :
    Config().reload()

oParser = argparse.ArgumentParser( description = "Parabridge daemon" )
oParser.add_argument( 'port', type = int, help = "Port to listen on" )
oArgs = oParser.parse_args()
Server( oArgs.port ).serve_forever()

