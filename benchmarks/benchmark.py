# -*- coding: utf-8 -*-
"""before: run examples/*_server.py"""

import sys; sys.modules.pop('threading', None)
from gevent.monkey import patch_all; patch_all()
import time

NUM_CALLS = 10000


def run_sum_server():
    from gevent.server import StreamServer
    from mprpc import RPCHandler

    class SumHandler(RPCHandler):
        def sum(self, x, y):
            return x + y

    server = StreamServer(('0.0.0.0', 6000), SumHandler())
    server.serve_forever()


def call():
    from mprpc import RPCClient

    client = RPCClient('tcp://127.0.0.1:6000')

    start = time.time()
    [client.call('sum', 1, 2) for _ in xrange(NUM_CALLS)]

    print 'call: %d qps' % (NUM_CALLS / (time.time() - start))


if __name__ == '__main__':
    call()
