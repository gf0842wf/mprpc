# -*- coding: utf-8 -*-
""" 使用python标准库的 ThreadingTCPServer
: 如果想用gevent, 可以用gevent patch all
"""
from SocketServer import ThreadingUnixStreamServer, StreamRequestHandler
from mprpc import RPCHandler


class SumHandler(RPCHandler):
    def sum(self, x, y):
        return x + y


class _Handler(StreamRequestHandler):
    def handle(self):
        SumHandler()(self.connection, None)


server = ThreadingUnixStreamServer('./x.sock', _Handler)
server.serve_forever()