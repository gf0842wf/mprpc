# -*- coding: utf-8 -*-

import logging
import msgpack
import urlparse
import time
import socket

from exceptions import RPCProtocolError, RPCError
from constants import MSGPACKRPC_REQUEST, MSGPACKRPC_RESPONSE, SOCKET_RECV_SIZE

logger = logging.getLogger(__name__)


class RPCClient(object):
    def __init__(self, address=None, timeout=None, pack_encoding='utf-8', unpack_encoding='utf-8', reconnect_delay=0,
                 tcp_no_delay=False):
        self._timeout = timeout

        self._msg_id = 0
        self._socket = None
        self._tcp_no_delay = tcp_no_delay

        self._packer = msgpack.Packer(encoding=pack_encoding)
        self._unpacker = msgpack.Unpacker(encoding=unpack_encoding, use_list=False)

        self._reconnect_delay = reconnect_delay

        url = urlparse.urlparse(address)
        if url.scheme == 'tcp':
            self.open_tcp(url)
        elif url.scheme == 'ipc':
            self.open_unixsocket(url)

    def open_tcp(self, url):
        """Opens a tcp connection.
        :param url: url ParseResult
        """
        assert self._socket is None, 'The connection has already been established'

        logger.debug('Opening a tcp msgpackrpc connection')
        self._socket = socket.create_connection((url.hostname, url.port))

        # set TCP NODELAY
        if self._tcp_no_delay:
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        if self._timeout:
            self._socket.settimeout(self._timeout)

    def open_unixsocket(self, url):
        """Opens a tcp connection.
        :param url: url ParseResult
        """
        assert self._socket is None, 'The connection has already been established'

        logger.debug('Opening a unix socket msgpackrpc connection')
        self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        hostname = url.hostname or ''
        path = url.path or ''
        filename = hostname + path
        self._socket.connect(filename)

        if self._timeout:
            self._socket.settimeout(self._timeout)

    def close(self):
        """Closes the connection."""
        assert self._socket is not None, 'Attempt to close an unopened socket'

        logger.debug('Closing a msgpackrpc connection')
        try:
            self._socket.close()
        except Exception as e:
            logger.exception('An error has occurred while closing the socket. %s', str(e))

        self._socket = None

    def is_connected(self):
        """Returns whether the connection has already been established.
        :rtype: bool
        """
        if self._socket:
            return True
        else:
            return False

    def _call(self, method, *args):
        """Calls a RPC method.
        :param str method: Method name.
        :param args: Method arguments.
        """
        req = self._create_request(method, args)

        self._socket.sendall(req)

        while True:
            data = self._socket.recv(SOCKET_RECV_SIZE)
            if not data:
                raise IOError('Connection closed')
            self._unpacker.feed(data)
            try:
                response = self._unpacker.next()
                break
            except StopIteration:
                continue

        return self._parse_response(response)

    def call(self, method, *args):
        """Calls a RPC method.
        :param str method: Method name.
        :param args: Method arguments.
        """
        if self._reconnect_delay is 0:
            return self._call(method, *args)

        try:
            return self._call(method, *args)
        except Exception as e:
            logger.debug('Call except %s', str(e))
            self.close()
            while 1:
                try:
                    logger.debug('Try reconnecting...')
                    self.open()
                    logger.debug('Reconnected.')
                    return self._call(method, *args)
                except:
                    time.sleep(self._reconnect_delay)

    def _create_request(self, method, args):
        self._msg_id += 1

        req = (MSGPACKRPC_REQUEST, self._msg_id, method, args)

        return self._packer.pack(req)

    def _parse_response(self, response):
        if len(response) != 4 or response[0] != MSGPACKRPC_RESPONSE:
            raise RPCProtocolError('Invalid protocol')

        (_, msg_id, error, result) = response

        if msg_id != self._msg_id:
            raise RPCError('Invalid Message ID')

        if error:
            raise RPCError(str(error))

        return result