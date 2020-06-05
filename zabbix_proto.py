#!/usr/bin/env python3

import json
import socket
import struct
import sys
import zlib

# https://www.zabbix.com/documentation/current/manual/appendix/protocols/header_datalen


def recvall(sock, timeout, bufsize=4096):
    sock.settimeout(timeout)
    merged_data = bytearray()
    while True:
        data = sock.recv(bufsize)
        if data:
            merged_data.extend(data)
        else:
            # No more data
            break

    if len(merged_data) > 13:
        # Skip 13 byte header. TODO: Check header?
        content = merged_data[13:]
    else:
        raise Exception("Error in data received data with length: {}".format(len(merged_data)))

    try:
        # The received data might be compressed
        return zlib.decompress(content).decode("utf-8")
    except zlib.error:
        return content.decode("utf-8")


def send_data(host, port, data, recv_timeout=1.0):
    data = json.dumps(data).encode("utf-8")
    packet = bytearray()
    packet.extend(b"ZBXD")
    packet.extend(b"\1")
    packet.extend(struct.pack('<L', len(data)))
    packet.extend(b"\0\0\0\0")
    packet.extend(data)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(packet)
        response = recvall(s, recv_timeout)
        sys.stdout.write(response)


if __name__ == "__main__":
    hostname = sys.argv[1]
    port = int(sys.argv[2])
    timeout = int(sys.argv[3])
    data = json.loads(sys.stdin.read())
    send_data(hostname, port, data, timeout)
