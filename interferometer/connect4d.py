"""

Main function for setting up a 4D interferometer as a remote server.

4D uses Python2 so syntax is similar but different to connectzygo.py

Initially using Sockets. Will look to upgrade to an SSH implementation for true
remote access in the future

Author: James Johnson
License: MIT
"""

import socket
import time
import os
import logging

# setup logging for debug
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fhandle = logging.FileHandler('socket.log')
fhandle.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fhandle.setFormatter(formatter)

logger.addHandler(fhandle)
logger.debug('Starting connect4d.py')
"""Setup the Interferomter as a Server"""

padding = 8 # max number of digits of message length
try:
    #Makes sure system resets if script needs to run multiple times
    srv.soc.close()
except NameError:
    pass

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
        time.sleep(0.2)  #ensures socket binds to ip/port
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
                elif 'exec(' in cmdmsg or 'execfile(' in cmdmsg or 'eval(' in cmdmsg:
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
                        dataresult = None  # Resets in case dataresult exists in namespace
                        # Yes this is bad. Looking for alternatives in the future (maybe rewrite/custom version of ast.literal_eval)
                        exec(cmdmsg)
                        if len(cmdmsg.split('=')) > 1:
                            #Also bad. Working to find better soln
                            #eval returns the variable name which when called
                            #saves the variable value to dataresult. If this is
                            #an object/array/list it is the same list in memory.
                            #If number or string, it is a copy.
                            dataresult = eval(cmdmsg.split('=')[0])
                        if dataresult:
                            # If the statment returns a value, code assumes it's data. If ndarray, converts to binary string. else assumes str() to convert
                            try:
                                msg = dataresult.tostring()
                            except AttributeError:
                                msg = str(dataresult)
                            self.send_msg(conn, msg)
                        else:
                            msg = "NO RETURN DATA"
                            self.send_msg(conn, msg)
                        # Send success/fail code (0/1)
                        msg = '0'
                        self.send_msg(conn, msg)
                    except socket.error:
                        logger.error('Unable to transmit data')
                    finally:
                        conn.close()
            else:
                conn.close()
        conn.close()

        self.soc.close()
        print('Server Closed')
        # logging.info('Server Closed')

    def send_msg(self, conn, msg):
        """
        Convienience function for sending messages. Sends message length and then message to receiving computer
        should refactor to _send_msg to make private in future
        """
        mlen = '%s' % len(msg)
        conn.send(mlen.rjust(padding, '0'))
        conn.send(msg)

if __name__ == "__main__":
    srv = InterferometerServer()
    srv.handle_connection()
