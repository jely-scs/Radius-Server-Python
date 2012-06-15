#-*- coding: utf-8 -*-

import sqlite3
import config
import socket

class SQLite_srv:
    c = None
    conn = None

    def __init__(self):
        try:
            self.conn = sqlite3.connect(config.sqlbase_file)
            self.c = self.conn.cursor()
            if config.new_base:
                self.c.executescript("""
                    DROP TABLE IF EXISTS user
                """)

            self.c.executescript("""

                CREATE TABLE IF NOT EXISTS user (
                    id INTEGER PRIMARY KEY,
                    login varchar(255),
                    password varchar(255),
                    ip varchar(255),
                    unique(login,password)
                )
            """)

            if config.add_test_value:
                self.c.executescript("""
                    insert into user values (1,"test1","qw","192.168.0.1");
                    insert into user values (2,"test","qq","192.168.0.2");
                    insert into user values (3,"1111","asd","192.168.0.3");
                """)
        except:
            print "Error in connect to sql base"
            return None


    def check_user(self,user):
        user_b = (user,)
        self.c.execute("select login from user where login =?",user_b)
        return not self.c.fetchone()==None
      
    def get_password(self,user):
        user_b = (user,)
        self.c.execute("select password from user where login =?",user_b)
        try:
            return self.c.fetchone()[0]
        except TypeError:
            print "Not password for user: "+ `user`
            return None

    def get_ip(self,user):
        user_b = (user,)
        self.c.execute("select ip from user where login =?",user_b)
        try:
            return `iptoint(self.c.fetchone()[0])`+ ""

        except TypeError:
            print "Not ip for user: "+ `user`
            return None

def iptoint(ip):
    return int(socket.inet_aton(ip).encode('hex'),16)

def inttoip(ip):
    return socket.inet_ntoa(hex(ip)[2:].zfill(8).decode('hex'))