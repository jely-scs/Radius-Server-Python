#!/usr/bin/python
#-*- coding: utf-8 -*-

from pyrad import packet, server
import config
#константы для разных типов шифрования
AUTH_PAP = 1

"""Можно сделать интерфейс для типов шифрования и его реализации.
Но только для PAP нет смысла плодить лишние сущности - это будет ущерб производительности
Для 1-2 типов шифрования имеет смысл использовать константы.
Больше типов или используемых возможностей - объектную модель
"""

class AuthServ( server.Server ):
    """Класс аутентификатора"""

    sqlite_srv = None

    def _HandleAuthPacket( self, pkt ):
        """Событийно-ориентированная функция на приход Auth-пакета"""
        server.Server._HandleAuthPacket( self, pkt )

        packet_auth_type = self.get_auth_type( pkt )
        print "conneсt user "+ pkt[1][0]
        if not self.sqlite_srv.check_user(pkt.get(1)[0]):
            print "Not user " + `pkt.get(1)[0]` + "in base"
            return self.reject_auth( pkt, 100 )

        if packet_auth_type == AUTH_PAP:

            reply = self.validate_pap( pkt,self.sqlite_srv.get_password(pkt.get(1)[0])) #self.get_password( pkt.get( 'User-Name' ) [0] ) )
            if not reply:
                #print "Not correct password"
                return self.reject_auth( pkt, 0 )
            else:
                return self.accept_auth( pkt, reply)
        else:
            print "auth type not supported"
            return self.reject_auth( pkt, 101 )

    def reject_auth( self, auth_pkt, reject_reason ):
        reply = self.CreateReplyPacket( auth_pkt )
        reply.code = packet.AccessReject
        self.SendReplyPacket( auth_pkt.fd, reply )
        # по reject_reason можно создать логирование
        # полезно для службы техподдержки

    def accept_auth( self, auth_pkt, reply ):
        reply.code = packet.AccessAccept

        self.SendReplyPacket( auth_pkt.fd, reply )

    def create_accept_reply( self, pkt ):
        """Создание акцепта"""
        reply = self.CreateReplyPacket( pkt )
        reply.code = packet.AccessAccept
        reply.secret = config.secret
        self.add_attributes( reply, pkt )
        self.add_ip(reply,pkt)
        return reply

    def add_attributes( self, pkt, dictionary ):
        """Добавляем атрибуты в пакет из словаря"""
        for attr in dictionary.keys( ):
            pkt.AddAttribute( attr, dictionary[ attr ][ 0 ] )

        return pkt

    def add_ip(self,pkt,dict):
        pkt.AddAttribute(8, self.sqlite_srv.get_ip(dict[1][0]))


    def create_reject_reply( self, pkt ):
        """Создание реджекта"""
        reply = self.CreateReplyPacket( pkt )
        reply.code = packet.AccessReject
        return reply
    
    def get_pap_pass( self, pkt ):
        """Получение открытого пароля"""
        try:
            packet_password = packet.AuthPacket(
                            secret = config.secret,
                            authenticator = pkt.authenticator
                            ).PwDecrypt( pkt.get(2)[0] )
            return packet_password

        except TypeError:
            print "Not passw in input"
            return None

    def get_auth_type( self, pkt ):
            return AUTH_PAP

    def validate_pap( self, pkt, db_password):
        if db_password==None:
            return None
        packet_password = self.get_pap_pass( pkt )
        if packet_password == db_password:
            print "Success authotizate"
            return self.create_accept_reply( pkt )
        print "Not correct password"
        return None
