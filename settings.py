#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

import os
import json
import xmlrpclib
import socket
import sqlite3
import uuid
from common import *

SQL_CREATE = """CREATE TABLE IF NOT EXISTS task (
  guid TEXT,
  name TEXT UNIQUE,
  src TEXT,
  dst TEXT,
  index_last INTEGER)"""
SQL_TASK_ADD = """INSERT INTO task (guid, name, src, dst, index_last)
  VALUES (:guid, :name, :src, :dst, :index_last)"""
SQL_TASK_LIST = """SELECT * FROM task"""
SQL_TASK_DEL_BY_NAME = """DELETE FROM task WHERE name = :name"""

class Settings( object ) :

  m_fInit = False
  m_fNotify = False

  @classmethod
  def init( self, notify = False ) :
    self.m_fNotify = notify
    self.m_fInit = True
    with sqlite3.connect( FILE_CFG ) as oConn :
      oConn.execute( SQL_CREATE )

  ##  Notify daemon process so it can read updated settings.
  @classmethod
  def notifyIfNeeded( self ) :
    if not self.m_fNotify : return
    try :
      xmlrpclib.ServerProxy( COMM_ADDR ).cfg_changed()
    except socket.error :
      pass

  @classmethod
  def taskAdd( self, i_sName, i_sSrc, i_sDst ) :
    with sqlite3.connect( FILE_CFG ) as oConn :
      try :
        mValues = {
          'guid' : str( uuid.uuid4() ),
          'name' : i_sName,
          'src' : i_sSrc,
          'dst' : i_sDst,
          'index_last' : 0 }
        oConn.execute( SQL_TASK_ADD, mValues )
      except sqlite3.IntegrityError :
        ##  Name not unique.
        return False
      else :
        return True
      finally :
        self.notifyIfNeeded()

  @classmethod
  def taskDelByName( self, i_sName ) :
    with sqlite3.connect( FILE_CFG ) as oConn :
      oRet = oConn.execute( SQL_TASK_DEL_BY_NAME, { 'name' : i_sName } )
      self.notifyIfNeeded()
      return 1 == oRet.rowcount

  @classmethod
  def taskList( self ) :
    with sqlite3.connect( FILE_CFG ) as oConn :
      try :
        oConn.row_factory = sqlite3.Row
        return oConn.execute( SQL_TASK_LIST ).fetchall()
      finally :
        self.notifyIfNeeded()

