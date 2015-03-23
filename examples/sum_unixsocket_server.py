# -*- coding: utf-8 -*-

from gevent.monkey import patch_all; patch_all()
from gevent.server import StreamServer
from gevent import socket
from mprpc import RPCHandler
import os


class SumHandler(RPCHandler):
    def sum(self, x, y):
        return x + y


listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock_name = './x.sock'
if os.path.exists(sock_name):
    os.remove(sock_name)
listener.bind(sock_name)
listener.listen(10)

server = StreamServer(listener, SumHandler())
server.serve_forever()
