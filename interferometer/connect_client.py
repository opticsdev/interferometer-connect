"""

Main function for accessing a 4D interferometer to collect data from an external script.

Initially using Sockets. Will look to upgrade to an SSH implementation for true
remote access in the future

Author: James Johnson
License: MIT
"""

import os
import numpy as np
import socket

# soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def send_command(command, ip_addr='127.0.0.1', port=50001):
    """Establishes a socket client to the server at provided address and port"""
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect((ip_addr, port))
    print('Attempting Connection to {} Port: {}'.format(ip_addr, port))
    conn_success = soc.recv(1024)
    print(f'Server>> {conn_success.decode()}')

    soc.send(command.encode('utf-8'))
    conf = soc.recv(1)
    complete = soc.recv(1024)

    print(f'Input: {command} -- Completed with success (1/0): {conf.decode()}')
    print(f'{complete.decode()}')
    soc.close()

if __name__ == "__main__":
    send_command('np.sum([1,1])')
