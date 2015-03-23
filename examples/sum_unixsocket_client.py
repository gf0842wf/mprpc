# -*- coding: utf-8 -*-

"""如果想用gevent, 可以用gevent patch all
"""
from mprpc import RPCClient


def call():
    client = RPCClient('ipc://x.sock', reconnect_delay=5)

    print client.call('sum', 1, 2)


call()
