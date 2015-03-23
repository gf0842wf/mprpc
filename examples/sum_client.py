# -*- coding: utf-8 -*-

"""如果想用gevent, 可以用gevent patch all
"""
from mprpc import RPCClient

client = RPCClient('tcp://127.0.0.1:6000', reconnect_delay=5)
print client.call('sum', 1, 2)