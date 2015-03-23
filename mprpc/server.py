# -*- coding: utf-8 -*-

from constants import MSGPACKRPC_REQUEST, MSGPACKRPC_RESPONSE, SOCKET_RECV_SIZE
from exceptions import MethodNotFoundError, RPCProtocolError
import socket
import msgpack


class RPCHandler(object):
    def __init__(self, *args, **kwargs):
        pack_encoding = kwargs.pop('pack_encoding', 'utf-8')
        unpack_encoding = kwargs.pop('unpack_encoding', 'utf-8')
        self._tcp_no_delay = kwargs.pop('tcp_no_delay', False)

        self._packer = msgpack.Packer(encoding=pack_encoding)
        self._unpacker = msgpack.Unpacker(encoding=unpack_encoding, use_list=False)

        self.use_greenlets = False
        try:
            from gevent import socket as gsocket

            if gsocket == socket.socket:
                self.use_greenlets = True
        except:
            pass

        if args and isinstance(args[0], socket.socket):
            self._run(_RPCConnection(args[0]), self.use_greenlets)

    def __call__(self, sock, _):
        if self._tcp_no_delay:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self._run(_RPCConnection(sock, self.use_greenlets))

    def _run(self, conn):
        while True:
            data = conn.recv(SOCKET_RECV_SIZE)
            if not data:
                break

            self._unpacker.feed(data)
            try:
                req = self._unpacker.next()
            except StopIteration:
                continue

            (msg_id, method, args) = self._parse_request(req)

            try:
                ret = method(*args)

            except Exception, e:
                self._send_error(str(e), msg_id, conn)

            else:
                self._send_result(ret, msg_id, conn)

    def _parse_request(self, req):
        if len(req) != 4 or req[0] != MSGPACKRPC_REQUEST:
            raise RPCProtocolError('Invalid protocol')

        (_, msg_id, method_name, args) = req

        if method_name.startswith('_'):
            raise MethodNotFoundError('Method not found: %s', method_name)

        if not hasattr(self, method_name):
            raise MethodNotFoundError('Method not found: %s', method_name)

        method = getattr(self, method_name)
        if not hasattr(method, '__call__'):
            raise MethodNotFoundError('Method is not callable: %s', method_name)

        return msg_id, method, args

    def _send_result(self, result, msg_id, conn):
        msg = (MSGPACKRPC_RESPONSE, msg_id, None, result)
        conn.send(self._packer.pack(msg))

    def _send_error(self, error, msg_id, conn):
        msg = (MSGPACKRPC_RESPONSE, msg_id, error, None)
        conn.send(self._packer.pack(msg))


class _RPCConnection(object):
    def __init__(self, sock, use_greenlets):
        self._sock = sock
        self.use_greenlets = use_greenlets
        if use_greenlets:
            from gevent.lock import Semaphore

            self._send_lock = Semaphore()

    def recv(self, buf_size):
        return self._sock.recv(buf_size)

    def send(self, msg):
        if self.use_greenlets:
            self._send_lock.acquire()
            try:
                self._sock.sendall(msg)
            finally:
                self._send_lock.release()
        else:
            try:
                self._sock.sendall(msg)
            finally:
                pass

    def __del__(self):
        try:
            self._sock.close()
        except:
            pass
