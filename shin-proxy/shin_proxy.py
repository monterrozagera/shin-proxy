import threading
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