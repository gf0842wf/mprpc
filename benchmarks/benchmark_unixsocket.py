# -*- coding: utf-8 -*-
"""before: run examples/*unixsocket_server.py"""

import sys; sys.modules.pop('threading', None)
from gevent.monkey import patch_all; patch_all()
import time

NUM_CALLS = 10000


def run_sum_server():
    from gevent.server import StreamServer
    from mprpc import RPCHandler
    from gevent import socket
    import os

    class SumHandler(RPCHandler):
        def sum(self, x, y):
            return x + y

    listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock_name = 'test.sock'
    if os.path.exists(sock_name):
        os.remove(sock_name)
    listener.bind(sock_name)
    listener.listen(10)

    server = StreamServer(listener, SumHandler())
    server.serve_forever()


def call():
    from mprpc import RPCClient

    client = RPCClient('ipc://test.sock')

    start = time.time()
    [client.call('sum', 1, 2) for _ in xrange(NUM_CALLS)]

    print 'call: %d qps' % (NUM_CALLS / (time.time() - start))


if __name__ == '__main__':
    call()
