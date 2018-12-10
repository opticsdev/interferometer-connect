"""

Main function for setting up a 4D interferometer as a remote server.

4D uses Python2 so syntax is similar but different to connectzygo.py

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
    def __init__(self, host_ip='127.0.0.1', port=61112):
        """ Server Object which creates a listen on a separate thread"""
        self.host_ip = host_ip
        self.port = port
        logger.info('Starting InterferometerServer')
        print("Starting InterferometerServer")
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.settimeout(20)
        self.soc.bind((self.host_ip, self.port))
        self.soc.listen(10)

    def handle_connection(self, remote_network=False):
        """ Print a greeting message and wait for signal"""
        while True:
            conn, addr = self.soc.accept()
            conn.setblocking(1)  # Quirk of windows
            logger.info('INCOMING CONNECTION FROM: %s' % addr[0])
            print('INCOMING CONNECTION FROM: %s' % addr[0])
            # print(f"Incoming connection from {addr[0]} port {addr[1]}")

            # Check if external connection and refuse if remote_network is False
            whitelist = ['127','192']
            if addr[0][:3] not in whitelist and remote_network is False:
                msg = 'CONNECTION REFUSED'
                self.send_msg(conn, msg)
                break
            # Send Length of Message then message
            msg='CONNECTION ESTABLISHED TO INTERFEROMETER'
            self.send_msg(conn, msg)

            cmd = conn.recv(padding)  # message length in DEC
            cmd = conn.recv(int(cmd))
            logger.info('RECEIVED COMMAND>> %s' % cmd.decode())
            print('RECEIVED COMMAND>> %s' % cmd.decode())
            if cmd.upper().decode() == 'CLOSE':
                msg = 'CONNECTION CLOSED. SUCCESS: 0'
                self.send_msg(conn, msg)
                break
            elif cmd.decode():
                cmdmsg = cmd.decode()
                # Attempt to Prevent malicious code from executing
                if cmdmsg[0:3] == 'os.' or cmdmsg[0:3] == 'sys.':
                    msg = 'COMMAND ERROR: RESTRICTED ACCESS TO OS and SYS MODULES'
                    self.send_msg(conn, msg)
                    msg = '1'
                    self.send_msg(conn, msg)

                    conn.close()
                elif 'exec(' in cmdmsg or 'eval(' in cmdmsg:
                    msg = "COMMAND ERROR: RESTRICTED ACCESS TO EXEC and EVAL FUNCTIONS"
                    self.send_msg(conn, msg)
                    msg = '1'
                    self.send_msg(conn, msg)
                    conn.close()
                elif '.join(' in cmdmsg:
                    msg = "COMMAND ERROR: RESTRICTED ACCESS TO JOIN FUNCTION"
                    self.send_msg(conn, msg)
                    msg = '1'
                    self.send_msg(conn, msg)
                    conn.close()
                else:
                    try:
                        #  Attempt to execute function on remote computer
                        dataresult = None
                        exec(cmdmsg)
                        if dataresult:
                            # If the statment returns a value, code assumes it's data. Will return the datafile location
                            msg = "DATA"
                            self.send_msg(conn, msg)
                            msg = "%s" % dataresult
                            self.send_msg(conn, msg)
                        else:
                            msg = "NO RETURN DATA"
                            self.send_msg(conn, msg)
                        # Send success/fail code (0/1)
                        msg = '0'
                        self.send_msg(conn, msg)
                    finally:
                        conn.close()
            else:
                conn.close()
        conn.close()

        self.soc.close()
        print('Server Closed')
        # logging.info('Server Closed')

    def send_msg(self, conn, msg):
        mlen = '%s' % len(msg)
        conn.send(mlen.rjust(padding, '0'))
        conn.send(msg)

if __name__ == "__main__":
    srv = InterferometerServer()
    srv.handle_connection()
