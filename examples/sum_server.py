# -*- coding: utf-8 -*-

from gevent.monkey import patch_all; patch_all()
from gevent.server import StreamServer

from mprpc import RPCHandler


class SumHandler(RPCHandler):
    def sum(self, x, y):
        return x + y


server = StreamServer(('0.0.0.0', 6000), SumHandler())
server.serve_forever()
