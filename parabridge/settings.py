#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

# parabridge persistent settings module.
# Copyright 2013 Grigory Petrov
# See LICENSE for details.

import xmlrpclib
import socket
import sqlite3
import uuid

import info

SQL_CREATE = """
  CREATE TABLE IF NOT EXISTS task (
    guid TEXT UNIQUE,
    name TEXT UNIQUE,
    src TEXT,
    dst TEXT);
  CREATE TABLE IF NOT EXISTS index_last (
    guid TEXT,
    file TEXT,
    index_last INTEGER);
"""
SQL_TASK_ADD = """INSERT INTO task (guid, name, src, dst)
  VALUES (:guid, :name, :src, :dst)"""
SQL_TASK_LIST = """SELECT * FROM task"""
SQL_TASK_DEL_BY_NAME = """DELETE FROM task WHERE name = :name"""
SQL_TASK_GUID_BY_NAME = """SELECT guid FROM task WHERE name = :name"""
SQL_INDEX_LAST_DEL = """DELETE FROM index_last WHERE guid = :guid"""
SQL_INDEX_LAST_UPDATE = """UPDATE index_last SET index_last = :index_last
  WHERE guid = :guid AND file = :file"""
SQL_INDEX_LAST_ADD = """INSERT INTO index_last (guid, file, index_last)
  VALUES (:guid, :file, :index_last)"""
SQL_INDEX_LAST_GET = """SELECT index_last FROM index_last WHERE
  guid = :guid AND file = :file"""


class Settings( object ) :


  def __init__( self ) :
    self.__fInit = False
    self.__fNotify = False


  def init( self, f_notify = False ) :
    self.__fNotify = f_notify
    self.__fInit = True
    with sqlite3.connect( info.FILE_CFG ) as oConn :
      oConn.executescript( SQL_CREATE )


  ##  Notify daemon process so it can read updated settings.
  def notifyIfNeeded( self ) :
    if not self.__fNotify :
      return
    try :
      xmlrpclib.ServerProxy( info.COMM_ADDR ).cfg_changed()
    except socket.error :
      pass


  def taskAdd( self, s_name, s_src, s_dst ) :
    with sqlite3.connect( info.FILE_CFG ) as oConn :
      try :
        mValues = {
          'guid' : str( uuid.uuid4() ),
          'name' : s_name,
          'src' : s_src,
          'dst' : s_dst }
        oConn.execute( SQL_TASK_ADD, mValues )
      except sqlite3.IntegrityError :
        ##  Name not unique.
        return False
      else :
        return True
      finally :
        self.notifyIfNeeded()


  def indexLastSet( self, s_guid, s_file, n_index ) :
    with sqlite3.connect( info.FILE_CFG ) as oConn :
      mArgs = {
        'guid' : s_guid,
        'file' : s_file,
        'index_last' : n_index }
      oRet = oConn.execute( SQL_INDEX_LAST_UPDATE, mArgs )
      if oRet.rowcount > 0 :
        return
      ##  No record for guid and name pair: add one.
      oConn.execute( SQL_INDEX_LAST_ADD, mArgs )


  def indexLastGet( self, s_guid, s_file ) :
    with sqlite3.connect( info.FILE_CFG ) as oConn :
      oConn.row_factory = sqlite3.Row
      mArgs = { 'guid' : s_guid, 'file' : s_file }
      lRet = oConn.execute( SQL_INDEX_LAST_GET, mArgs ).fetchall()
      if 0 == len( lRet ) :
        return None
      if len( lRet ) > 1 :
        raise Exception( "Consistency error." )
      return lRet[ 0 ][ 'index_last' ]


  def taskDelByName( self, s_name ) :
    with sqlite3.connect( info.FILE_CFG ) as oConn :
      oConn.row_factory = sqlite3.Row
      try :
        mArgs = { 'name' : s_name }
        oRow = oConn.execute( SQL_TASK_GUID_BY_NAME, mArgs ).fetchone()
        if oRow is None :
          return False
        mArgs[ 'guid' ] = oRow[ 'guid' ]
        oRet = oConn.execute( SQL_TASK_DEL_BY_NAME, mArgs )
        if 0 == oRet.rowcount :
          raise Exception( "Consistency error" )
        oConn.execute( SQL_INDEX_LAST_DEL, mArgs )
        return True
      finally :
        self.notifyIfNeeded()


  def taskList( self ) :
    with sqlite3.connect( info.FILE_CFG ) as oConn :
      try :
        oConn.row_factory = sqlite3.Row
        return oConn.execute( SQL_TASK_LIST ).fetchall()
      finally :
        self.notifyIfNeeded()


instance = Settings()

