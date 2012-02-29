#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

import os
import json
import xmlrpclib
import socket

class Settings( object ) :

  m_mItems = { 'tasks' : [] }
  sPath = os.path.expanduser( "~/.parabridge" )
  if os.path.exists( sPath ) :
    m_mItems.update( json.load( open( sPath ) ) )

  @classmethod
  def set( self, i_sName, i_uVal, notify = False ) :
    self.m_mItems[ i_sName ] = i_uVal
    sPath = os.path.expanduser( "~/.parabridge" )
    json.dump( self.m_mItems, open( sPath, 'w' ) )
    if notify :
      try :
        oSrv = xmlrpclib.ServerProxy( COMM_ADDR )
        oSrv.cfg_changed()
      except socket.error :
        pass

  @classmethod
  def get( self, i_sName ) :
    return self.m_mItems[ i_sName ]

