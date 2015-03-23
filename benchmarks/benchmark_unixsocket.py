# -*- coding: utf-8 -*-
"""before: run examples/*unixsocket_server.py"""

import sys; sys.modules.pop('threading', None)
from gevent.monkey import patch_all; patch_all()
import time

NUM_CALLS = 10000


def call():
    from mprpc import RPCClient

    client = RPCClient('ipc://test.sock')

    start = time.time()
    [client.call('sum', 1, 2) for _ in xrange(NUM_CALLS)]

    print 'call: %d qps' % (NUM_CALLS / (time.time() - start))


if __name__ == '__main__':
    call()
