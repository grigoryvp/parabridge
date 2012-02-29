#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

import os
import json
import xmlrpclib
import socket
from common import *

class Settings( object ) :

  m_mItems = { 'tasks' : [] }
  sPath = os.path.expanduser( "~/.parabridge" )
  if os.path.exists( sPath ) :
    m_mItems.update( json.load( open( sPath ) ) )
  m_fInit = False
  m_fNotify = False

  @classmethod
  def init( self, notify = False ) :
    self.m_fNotify = notify
    self.m_fInit = True

  @classmethod
  def set( self, i_sName, i_uVal ) :
    if not m_fInit : raise Exception( "Init not called." )
    self.m_mItems[ i_sName ] = i_uVal
    sPath = os.path.expanduser( "~/.parabridge" )
    json.dump( self.m_mItems, open( sPath, 'w' ) )
    ##  Notify daemon process so it can read updated settings.
    if m_fNotify :
      try :
        oSrv = xmlrpclib.ServerProxy( COMM_ADDR )
        oSrv.cfg_changed()
      except socket.error :
        pass

  @classmethod
  def get( self, i_sName ) :
    if not m_fInit : raise Exception( "Init not called." )
    return self.m_mItems[ i_sName ]

