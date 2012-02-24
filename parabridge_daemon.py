#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

import sys
import argparse
from SimpleXMLRPCServer import SimpleXMLRPCServer

class Server( SimpleXMLRPCServer, object ) :

  def __init__( self, i_nPort ) :
    gAddr = ( 'localhost', i_nPort )
    super( Server, self ).__init__( gAddr, allow_none = True )
    self.fShutdown = False
    self.register_function( self.stop )

  def serve_forever( self ) :
    while not self.fShutdown :
      self.handle_request()

  def stop( self ) :
    self.fShutdown = True

oParser = argparse.ArgumentParser( description = "Parabridge daemon" )
oParser.add_argument( 'port', type = int, help = "Port to listen on" )
oArgs = oParser.parse_args()
Server( oArgs.port ).serve_forever()

