"""
Test File for simulating server/client behavior

Currently Broken
"""

import socket
import numpy
import threading
import time
import pytest
import interferometer.connect4d as srv
import interferometer.connect_client as cli
#
# def test_serverexist():
#     try:
#         server = srv.InterferometerServer('127.0.0.1', 50001)
#         server.listening()
#
#         time.sleep(1)
#         soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         ip_addr='127.0.0.1'
#         port = 50001
#         success = soc.connect_ex((ip_addr, port))
#         assert(success == 0)
#         assert(len('CONNECTION ESTABLISHED TO INTERFEROMETER') == int(soc.recv(8)))
#         data = soc.recv(len('CONNECTION ESTABLISHED TO INTERFEROMETER'))
#         assert(data.decode() == 'CONNECTION ESTABLISHED TO INTERFEROMETER')
#         soc.close()
#         server.conn_handle.join()
#         server.soc.close()
#     except NameError:
#         server.conn_handle.join()
#     finally:
#         soc.close()
#         server.soc.close()
#
# @pytest.fixture
# def srvfixture():
#     server = srv.InterferometerServer('127.0.0.1', 50001)
#     server.listening()
#     return server
#
# def test_commandexc(srvfixture):
#     time.sleep(0.2)
#     assert(int(cli.send_command('len("551abc")')) == 6)
