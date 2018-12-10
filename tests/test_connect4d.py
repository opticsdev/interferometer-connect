"""
Test File for simulating server/client behavior
"""

import socket
import numpy
import threading
import time
import pytest
import interferometer.connect4d as srv
import interferometer.connect_client as cli

def test_serverexist():
    server = srv.InterferometerServer('127.0.0.1', 50001)

    time.sleep(1)
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip_addr='127.0.0.1'
    port = 50001
    success = soc.connect_ex((ip_addr, port))
    assert(success == 0)
    # data = example_cli.recv(1028)
    #assert(data.decode() == 'CONNECTED TO INTERFEROMETER')
    example_cli.close()


def test_messagelength():
    pass
