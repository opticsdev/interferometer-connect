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
import logging
import threading

# setup logging for debug
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

fhandle = logging.FileHandler('socket.log')
fhandle.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fhandle.setFormatter(formatter)

logger.addHandler(fhandle)
logger.debug('Starting connect4d.py')
"""Setup the Interferomter as a Server"""

padding = 8 # max number of digits of message length

class InterferometerServer:
    def __init__(self, host_ip='127.0.0.1', port=50001):
        """ Server Object which creates a listen on a separate thread"""
        self.host_ip = host_ip
        self.port = port
        # self.alive = threading.Event()
        # self.alive.set()
        logger.debug('Starting InterferometerServer')
        print("Starting InterferometerServer")
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.settimeout(200)
        self.soc.bind((self.host_ip, self.port))

    def listening(self):

        self.soc.listen(1)  # only connecting process should be on the line

        self.conn_handle = threading.Thread(target=self.handle_connection, args=())
        self.conn_handle.start()

    def handle_connection(self, remote_network=False):
        """ Print a greeting message and wait for signal"""
        #print('in _handle_connection()')
        while True:
            conn, addr = self.soc.accept()
            logger.info('INCOMING CONNECTION FROM: {}'.format(addr[0]))
            print('INCOMING CONNECTION FROM: {}'.format(addr[0]))
            # print(f"Incoming connection from {addr[0]} port {addr[1]}")

            # Check if external connection and refuse if remote_network is False
            if addr[0][:3] not in ['127','192'] and remote_network is False:
                msg = 'CONNECTION REFUSED'.encode('utf-8')
                conn.send('{}'.format(len(msg)).rjust(padding, '0').encode('utf-8'))
                conn.send(msg)
                conn.close()
                break
            # Send Length of Message then message
            msg='CONNECTION ESTABLISHED TO INTERFEROMETER'.encode('utf-8')
            conn.send('{}'.format(len(msg)).rjust(padding, '0').encode('utf-8'))
            conn.send(msg)

            cmd = conn.recv(padding)  # message length in DEC
            cmd = conn.recv(int(cmd))
            logger.info('RECEIVED COMMAND>> {%s}' % cmd.decode())
            print('RECEIVED COMMAND>> %s' % cmd.decode())
            if cmd.upper().decode() == 'CLOSE':
                msg = 'CONNECTION CLOSED. SUCCESS: 0'.encode('utf-8')
                conn.send('{}'.format(len(msg)).rjust(padding, '0').encode('utf-8'))
                conn.send(msg)
                conn.close()
                break
            elif cmd.decode():
                cmdmsg = cmd.decode()
                # Attempt to Prevent malicious code from executing
                if cmdmsg[0:3] == 'os.' or cmdmsg[0:3] == 'sys.':
                    msg = 'COMMAND ERROR: RESTRICTED ACCESS TO OS and SYS MODULES'.encode('utf-8')
                    conn.send('{}'.format(len(msg)).rjust(padding, '0').encode('utf-8'))
                    conn.send(msg)
                    msg = '1'.encode('utf-8')
                    conn.send('{}'.format(len(msg)).rjust(padding, '0').encode('utf-8'))
                    conn.send(msg)

                    conn.close()
                elif 'exec(' in cmdmsg or 'eval(' in cmdmsg:
                    msg = "COMMAND ERROR: RESTRICTED ACCESS TO EXEC and EVAL FUNCTIONS".encode('utf-8')
                    conn.send('{}'.format(len(msg)).rjust(padding, '0').encode('utf-8'))
                    conn.send(msg)
                    msg = '1'.encode('utf-8')
                    conn.send('{}'.format(len(msg)).rjust(padding, '0').encode('utf-8'))
                    conn.send(msg)
                    conn.close()
                elif '.join(' in cmdmsg:
                    msg = "COMMAND ERROR: RESTRICTED ACCESS TO JOIN FUNCTION".encode('utf-8')
                    conn.send('{}'.format(len(msg)).rjust(padding, '0').encode('utf-8'))
                    conn.send(msg)
                    msg = '1'.encode('utf-8')
                    conn.send('{}'.format(len(msg)).rjust(padding, '0').encode('utf-8'))
                    conn.send(msg)
                    conn.close()
                else:
                    """ Attempt to execute function on remote computer"""
                    try:
                        dataresult = None
                        exec(cmdmsg)
                        if dataresult:
                            # If the statment returns a value, code assumes it's data. Will return the datafile location
                            msg = "DATA".encode('utf-8')
                            conn.send('{}'.format(len(msg)).rjust(padding, '0').encode('utf-8'))
                            conn.send(msg)
                            msg = "{}".format(dataresult).encode('utf-8')
                            conn.send('{}'.format(len(msg)).rjust(padding, '0').encode('utf-8'))
                            conn.send(msg)
                        else:
                            msg = "NO RETURN DATA".encode('utf-8')
                            conn.send('{}'.format(len(msg)).rjust(padding, '0').encode('utf-8'))
                            conn.send(msg)
                        # Send success/fail code (0/1)
                        msg = '0'.encode('utf-8')
                        conn.send('{}'.format(len(msg)).rjust(padding, '0').encode('utf-8'))
                        conn.send(msg)
                    except TypeError:
                        msg = "COMMAND FAILED".encode('utf-8')
                        conn.send('{}'.format(len(msg)).rjust(padding, '0').encode('utf-8'))
                        conn.send(msg)
                        msg = '1'.encode('utf-8')
                        conn.send('{}'.format(len(msg)).rjust(padding, '0').encode('utf-8'))
                        conn.send(msg)
                        conn.close()
                    finally:
                        conn.close()
            else:
                conn.close()
        self.soc.close()
        print('Server Closed')
        # logging.info('Server Closed')
        return

if __name__ == "__main__":
        srv = InterferometerServer()
        srv.listening()
#
# def setup_server(ip_addr='127.0.0.1', port=50001):
#     """Establishes a socket server at the provided address and port"""
#     soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     soc.bind((ip_addr, port))
#     print('Server Socket established at {} Port: {}'.format(ip_addr, port))
#     soc.listen(1)
#     soc.settimeout(120)
#     return soc
#
# if __name__ == '__main__':
#     soc = setup_server()
#
#     while True:
#
#         conn, addr = soc.accept()
#         print(f'Incoming Connection from {addr}')
#         conn.send('Connected to 4D Interferometer'.encode('utf-8'))
#         try:
#             data = conn.recv(1024)
#             if data == b'hbt':
#                 conn.send(''.encode('utf-8'))
#             elif data:
#                 try:
#                     exec(data)
#                     #conn.send(f'Executing {data}'.encode('utf-8'))
#                     print(f'Executing {data}')
#                     conn.send(f'1\n'.encode('utf-8'))
#                 except NameError:
#                     print(f'Cannont execute {data}. Closing Connection')
#                     #conn.send('Operation Failed'.encode('utf-8'))
#                     conn.send('0\n'.encode('utf-8'))
#             else:
#                 break
#         finally:
#             time.sleep(.2)
#             conn.send('Connection Closed'.encode('utf-8'))
#             conn.close()
