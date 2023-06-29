#!/usr/bin/python

# Copyright (c) 2020 Tim Burke
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import unicode_literals
import argparse
import errno
import functools
import os
import signal
import socket
import sys

binary_stdout = os.fdopen(sys.stdout.fileno(), 'wb', 0)


def log(msg):
    try:
        sys.stderr.write(msg + '\n')
        sys.stderr.flush()
    except IOError:
        pass


def noop_log(msg):
    pass


def write(msg, end=b'\n'):
    try:
        binary_stdout.write(msg)
        binary_stdout.write(end)
    except IOError:
        pass


def addr(val):
    try:
        socket.inet_pton(socket.AF_INET6, val)
    except OSError:
        try:
            socket.inet_pton(socket.AF_INET, val)
        except OSError:
            raise ValueError('Invalid address')
    return val


def emit_stats(counter, sig, frame, log=log):
    log('[%d] Received %d packets' % (os.getpid(), counter[0]))


def graceful_exit(log, sock, sig, frame):
    signal.signal(sig, signal.SIG_DFL)
    if log:
        log('[%d] Shutting down' % os.getpid())
    sock.close()


def main(argv=sys.argv[1:], write=write, log=log):
    parser = argparse.ArgumentParser(description=(
        'Listen to a UDP port and print the messages received, '
        'one per line.'))
    parser.add_argument(
        '-q', '--quiet', action='store_true',
        help="don't log to stderr")
    parser.add_argument(
        '-z', '--zero', action='store_true',
        help='separate messages with NUL (instead of LF)')
    parser.add_argument(
        '-a', '--addr', default='::', type=addr,
        help='address on which to listen (default: all addresses)')
    parser.add_argument(
        '-p', '--port', default=8125, type=int,
        help='port on which to listen (default: 8125)')
    parser.add_argument(
        '-b', '--buffer', default=1024, type=int, dest='buf',
        help='recv buffer size (default: 1024)')
    args = parser.parse_args(argv)
    if args.quiet:
        log = noop_log
    if args.zero:
        write = functools.partial(write, end=b'\0')

    if ':' in args.addr:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        if args.addr == '::':
            sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.addr, args.port))
    log('[%d] Listening for UDP packets on port %s:%d' % (
        os.getpid(),
        '[%s]' % args.addr if ':' in args.addr else args.addr,
        args.port))
    counter = [0]

    emitter = functools.partial(emit_stats, counter)
    quitter = functools.partial(graceful_exit, log, sock)

    signal.signal(signal.SIGUSR1, emitter)
    signal.signal(signal.SIGPIPE, quitter)
    signal.signal(signal.SIGTERM, quitter)
    signal.signal(signal.SIGINT, quitter)

    try:
        data = bytearray(args.buf)
        view = memoryview(data)
        while True:
            try:
                msg_len, _ = sock.recvfrom_into(data)
            except socket.error as err:
                if err.errno == errno.EBADF:
                    break
                if err.errno == errno.EINTR:
                    continue
                raise
            write(view[:msg_len])
            counter[0] += 1
    finally:
        sock.close()
    emit_stats(counter, None, None, log=log)


if __name__ == '__main__':
    main()
