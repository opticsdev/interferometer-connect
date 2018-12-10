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
padding = 8 # longest message <10E8

def send_command(command, ip_addr='127.0.0.1', port=50001):
    """Establishes a socket client to the server at provided address and port"""
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.settimeout(10)

    soc.connect((ip_addr, port))

    print('Attempting Connection to {} Port: {}'.format(ip_addr, port))
    dynlen = soc.recv(padding)  # length should never be greater than 1e7
    conn_success = soc.recv(int(dynlen.strip() or 0))
    print(f'Server>> {conn_success.decode()}')

    soc.send('{}'.format(len(command)).rjust(padding, '0').encode('utf-8'))
    soc.send(command.encode('utf-8'))

    if command == 'CLOSE':
        dynlen = soc.recv(padding)
        conn_success = soc.recv(int(dynlen.strip() or 0))
        print(f'Server>> {conn_success.decode()}')
    soc.close()

def scheck(ip_addr='127.0.0.1', port=50001):
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    success = soc.connect_ex((ip_addr, port))
    print('Attempting Connection to {} Port: {}--{}'.format(ip_addr, port, success))
    soc.close()

if __name__ == "__main__":

    send_command('np.sum([1,1])')
    #scheck()
    send_command('1+1')