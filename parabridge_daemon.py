#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

import sys
import argparse
from SimpleXMLRPCServer import SimpleXMLRPCServer

g_fShutdown = False

def stop() :
  global g_fShutdown
  g_fShutdown = True

oParser = argparse.ArgumentParser( description = "Parabridge daemon" )
oParser.add_argument( 'port', type = int, help = "Port to listen on" )
oArgs = oParser.parse_args()
oServer = SimpleXMLRPCServer( ( 'localhost', oArgs.port ), allow_none = True )
oServer.register_function( stop )
while not g_fShutdown :
  oServer.handle_request()

