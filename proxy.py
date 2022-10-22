import argparse
import socket
import sys
import textwrap
import threading

import hexdump


def receive_from(connection):
    buffer = b""
    connection.settimeout(5)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception as e:
        pass
    return buffer


def request_handler(buffer):
    # perform packet modifications
    return buffer


def response_handler(buffer):
    # perform packet modifications
    return buffer


def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))
    remote_buffer = b''

    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump.hexdump(remote_buffer)

    remote_buffer = response_handler(remote_buffer)
    if len(remote_buffer):
        line = "[<==] Sending %d bytes to localhost." % len(remote_buffer)
        print(line)
        client_socket.send(remote_buffer)

    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            line = "[==>] Received %d bytes from localhost." % len(local_buffer)
            print(line)
            hexdump.hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.")

        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            line = "[<==] Received %d bytes from remote." % len(remote_buffer)
            print(line)
            hexdump.hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] Sent to localhost.")

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print('problem on bind: %r' % e)

        print("[!!] Failed to listen on %s:%d" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)

    print("[*] Listening on %s:%d" % (local_host, local_port))
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        # print out the local connection information
        line = "> Received incoming connection from %s:%d" % (addr[0], addr[1])
        print(line)
        # start a thread to talk to the remote host
        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket, remote_host, remote_port, receive_first)
        )
        proxy_thread.start()


def main(local_host, local_port, remote_host, remote_port, receive_first):
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)


def test():
    assert (True is True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='BHP Proxy',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''Example:
        proxy.py 127.0.0.1 9000 10.12.132.1 9000 True
        '''))
    parser.add_argument('-t', '--test', action='store_true', help='test')
    parser.add_argument('local_host', type=ascii, help='local-host')
    parser.add_argument('local_port', type=int, help='local-port')
    parser.add_argument('remote_host', type=ascii, help='remote-host')
    parser.add_argument('remote_port', type=int, help='remote-port')
    parser.add_argument('receive_first', type=bool, help='receive-first')
    args = parser.parse_args()

    if args.test:
        test()

    main(args.local_host, args.local_port, args.remote_host, int(args.remote_port), args.receive_first)
