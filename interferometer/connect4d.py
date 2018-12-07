"""

Main function for setting up a 4D interferometer as a remote server.

Initially using Sockets. Will look to upgrade to an SSH implementation for true
remote access in the future

Author: James Johnson
License: MIT
"""

import socket
import numpy as np
import time
import os

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

"""Setup the Interferomter as a Server"""


def setup_server(soc, ip_addr='127.0.0.1', port=50001):
    """Establishes a socket server at the provided address and port"""
    soc.bind((ip_addr, port))
    print('Server Socket established at {} Port: {}'.format(ip_addr, port))


if __name__ == '__main__':
    setup_server(soc)
    soc.listen(1)
    soc.settimeout(120)
    while True:

        conn, addr = soc.accept()
        print(f'Incoming Connection from {addr}')
        conn.send('Connected to 4D Interferometer'.encode('utf-8'))
        try:
            data = conn.recv(1024)
            if data == b'hbt':
                conn.send(''.encode('utf-8'))
            elif data:
                try:
                    exec(data)
                    #conn.send(f'Executing {data}'.encode('utf-8'))
                    print(f'Executing {data}')
                    conn.send(f'1\n'.encode('utf-8'))
                except NameError:
                    print(f'Cannont execute {data}. Closing Connection')
                    #conn.send('Operation Failed'.encode('utf-8'))
                    conn.send('0\n'.encode('utf-8'))
            else:
                break
        finally:
            time.sleep(.2)
            conn.send('Connection Closed'.encode('utf-8'))
            conn.close()
