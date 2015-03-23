# -*- coding: utf-8 -*-
""" 使用python标准库的 ThreadingTCPServer
: 如果想用gevent, 可以用gevent patch all
"""
from SocketServer import ThreadingTCPServer, StreamRequestHandler
from mprpc import RPCHandler


class SumHandler(RPCHandler):
    def sum(self, x, y):
        return x + y


class _Handler(StreamRequestHandler):
    def handle(self):
        SumHandler()(self.connection, None)


server = ThreadingTCPServer(('0.0.0.0', 6000), _Handler)
server.serve_forever()