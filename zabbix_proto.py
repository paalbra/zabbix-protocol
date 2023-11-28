#!/usr/bin/env python3

import json
import socket
import struct
import sys
import zlib

# https://www.zabbix.com/documentation/current/manual/appendix/protocols/header_datalen


def parse_data(data):
    if len(data) < 13:
        raise Exception(f"Too little data received. Length: {len(data)}")

    header = bytes(data[:13])
    content = data[13:]

    if header[0:4] != b"ZBXD":
        raise Exception(f"Invalid header start: {repr(header[0:4])}")

    flag_com_proto = bool(1 & header[4])
    flag_compression = bool(2 & header[4])
    flag_large_packet = bool(4 & header[4])

    data_length = int.from_bytes(header[5:9], "little")

    # So called "reserved" bits are used to represent uncompressed data length.
    reserved_bits = int.from_bytes(header[9:13], "little")

    if not flag_com_proto:
        # What the fuck is this flag? Is it always 1?
        # Can't find any documentation regarding the flag.
        pass

    if not flag_large_packet:
        # What does this really do? Just info that the content is huge?
        # Can't find any documentation regarding the flag.
        pass

    if len(content) != data_length:
        raise Exception(f"Content length and header does not match. {len(content)} != {data_length}")

    if not flag_compression:
        if reserved_bits != 0:
            raise Exception(f"Reserved bits should be 0 when not using compression: {reserved_bits}")

    if flag_compression:
        content = zlib.decompress(content)
        if len(content) != reserved_bits:
            raise Exception(f"Uncompressed content length and header does not match. {len(content)} != {reserved_bits}")

    content = json.loads(content.decode("utf-8"))
    return header, content


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

    _, content = parse_data(merged_data)

    return content


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
        return response


if __name__ == "__main__":
    hostname = sys.argv[1]
    port = int(sys.argv[2])
    timeout = int(sys.argv[3])
    data = json.loads(sys.stdin.read())
    response = send_data(hostname, port, data, timeout)
    print(json.dumps(response))
