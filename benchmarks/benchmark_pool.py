# -*- coding: utf-8 -*-
"""before: run examples/*_server.py"""

import sys; sys.modules.pop('threading', None)
from gevent.monkey import patch_all; patch_all()
import time

from pu.gpool import ConnectionPool

NUM_CALLS = 10000


def call():
    from mprpc import RPCClient

    pool = ConnectionPool(10, RPCClient, {'address': 'tcp://127.0.0.1:6000'})

    start = time.time()

    list(pool.map('call', [(('sum', 1, 2), {}), ] * NUM_CALLS))

    print 'call: %d qps' % (NUM_CALLS / (time.time() - start))


if __name__ == '__main__':
    call()
