# TCP Proxy based on BHP v2
import threading
import argparse
import socket
import sys

## ASCII printable characters
hex_filter = ''.join([(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])


# prints in readable-packet format
def hexDump(src, length=16, show=True):

    if isinstance(src, bytes):
        src = src.decode()

    results = list()

    for i in range(0, len(src), length):
        word = str(src[i:i+length])

        # substitute string representation of each char to raw str
        printable = word.translate(hex_filter)

        hexa = ' '.join([f'{ord(c):02X}' for c in word])
        hexwidth = length*3
        results.append(f'{i:04x} {hexa:<{hexwidth}} {printable}')

    if show:
        for line in results:
            print(line)

    else:
        return results
    
def receiveFrom(connection):
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

def requestHandler(buffer):
    # perform packet modifications
    return buffer

def responseHandler(buffer):
    # perform packet modifications
    return buffer

def proxyHandler(client_socket, remote_host, remote_port, receive_first):
    # starts socket handler
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    if receive_first:
        remote_buffer = receiveFrom(remote_socket)
        hexDump(remote_buffer)

    remote_buffer = responseHandler(remote_buffer)
    if len(remote_buffer):
        print("[<==] Sending %d bytes to localhost." % len(remote_buffer))
        client_socket.send(remote_buffer)

    while True:
        local_buffer = receiveFrom(client_socket)
        if len(local_buffer):
            line = "[==>] Received %d bytes from localhost." % len(local_buffer)
            print(line)
            hexDump(local_buffer)

            local_buffer = requestHandler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.")

        remote_buffer = receiveFrom(remote_socket)
        if len(remote_buffer):
            print("[<==] Received %d bytes from remote." % len(remote_buffer))
            hexDump(remote_buffer)

            remote_buffer = responseHandler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] Sent to localhost.")

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing.")
            break

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    # starts forwarder socket object
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # binds IP and port
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((local_host, local_port))
    except Exception as e:
        print('[!] Problem binding on %r' % e)

        sys.exit(0)

    print("[*] Listening on %s:%d" % (local_host, local_port))
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        # print out the local connection information
        line = "[>] Received incoming connection from %s:%d" % (addr[0], addr[1])
        print(line)
        # start a thread to talk to the remote host
        proxy_thread = threading.Thread(
            target=proxyHandler,
            args=(client_socket, remote_host,
            remote_port, receive_first)
        )
        proxy_thread.start()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-lh', type=str, help='Local host domain or IP.')
    parser.add_argument('-lp', type=str, help='Local port.')
    parser.add_argument('-rh', type=str, help='Remote host domain or IP.')
    parser.add_argument('-rp', type=str, help='Remote port.')
    parser.add_argument('--receive', type=str, help='Receive first, true or false.')
    args = parser.parse_args()

    if len(sys.argv[1:]) != 5:
        print("\nUsage ./shin_proxy.py -lh [localhost] -lp [localport]", end='')
        print(" -rh [remotehost] -rp [remoteport] --receive [receive_first]")
        print("\nExample: ./shin_proxy.py -lh 127.0.0.1 -lp 9999 -rh 10.12.132.1 -rp 9999 --receive True")
        sys.exit(0)

    local_host = args.lh
    local_port = args.lp

    remote_host = args.rh
    remote_port = args.rp

    receive_first = args.receive

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False
    
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

if __name__ == '__main__':
    main()