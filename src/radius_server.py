#!/usr/bin/python
#-*- coding: utf-8 -*-

import config
from pyrad import dictionary
from pyrad import server
import sqlite_server
from auth_server import AuthServ

__author__ = "jely_scs"
__version__ = 1.0
# main

print "Check SQLite"

sqlite = sqlite_server.SQLite_srv()

print "Start radius server"
srv = AuthServ(
                             dict=dictionary.Dictionary("conf/dictionary.bak"),
                             authport=config.radius_auth_port,
                             )

srv.sqlite_srv = sqlite
srv.hosts["127.0.0.1"] = server.RemoteHost(
                                           "127.0.0.1",
                                           config.secret,
                                           "localhost")
srv.BindToAddress(config.radius_bind_to_address)
srv.Run()

print "Stop server"