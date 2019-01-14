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

def send_command(command, ip_addr='127.0.0.1', port=61112, fname=''):
    """Establishes a socket client to the server at provided address and port"""
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.settimeout(20)

    soc.connect((ip_addr, port))

    print('Attempting Connection to {} Port: {}'.format(ip_addr, port))
    dynlen = soc.recv(padding)  # length should never be greater than 1e7
    conn_success = soc.recv(int(dynlen.strip() or 0))
    print('Server>> %s ' % conn_success.decode())

    soc.send('{}'.format(len(command)).rjust(padding, '0').encode('utf-8'))
    soc.send(command.encode('utf-8'))

    if command == 'CLOSE':
        dynlen = soc.recv(padding)
        conn_success = soc.recv(int(dynlen.strip() or 0))
        print('Server>> %s ' % conn_success.decode())
    else:
        dynlen = soc.recv(padding)
        conn_msg = soc.recv(int(dynlen.strip() or 0)).decode()
        if conn_msg == 'DATA':
            dynlen = soc.recv(padding)
            conn_drv = soc.recv(int(dynlen.strip() or 0))
            print('SERVER >> ---DATA---')
            print(conn_drv)
            dynlen = soc.recv(padding)
            conn_success = soc.recv(int(dynlen.strip() or 0))
            print('Server>> {} -- Return Code {}'.format(conn_msg.decode(), conn_success.decode()))
        elif conn_msg == 'FILETX':
            print("File Transfer from Server started. Saving to {}".format(fname))
            with open(fname, 'wb') as fin:
                while True:
                    data = soc.recv(1024)
                    if not data:
                        break
                    fin.write(data)

        else:
            pass
            """Not sure what I was doing here. refactor to see if obsolete"""
            # dynlen = soc.recv(padding)
            # databuffer = ""
            # # Open link until full message recieved
            # while True:
            #     if int(dynlen.strip() or 0) > 1023:
            #         rxbuffer = soc.recv(1024).decode()
            #         if not rxbuffer:
            #             break
            #         databuffer += rxbuffer
            #
            #     else:
            #         databuffer += soc.recv(int(dynlen.strip() or 0)).decode()

            print('Server>> Return Code {}'.format(conn_msg))
    soc.close()
    return conn_success

def scheck(ip_addr='127.0.0.1', port=61112):
    """Debug function. Neet to remove/replace into /test"""
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    success = soc.connect_ex((ip_addr, port))

    print('Attempting Connection to {} Port: {}--Success Code:{}'.format(ip_addr, port, success))
    dynlen = soc.recv(padding)  # length should never be greater than 1e7
    conn_success = soc.recv(int(dynlen.strip() or 0))
    print('Server>> %s ' % conn_success.decode())
    command = 'MessageBox("Client Command Received")'
    soc.send('{}'.format(len(command)).rjust(padding, '0').encode('utf-8'))
    soc.send(command.encode('utf-8'))
    dynlen = soc.recv(padding)  # length should never be greater than 1e7
    conn_success = soc.recv(int(dynlen.strip() or 0))
    print('Success Code:{}'.format(conn_success))
    soc.close()
    return conn_success


def filesavecheck():
    """Debug function. Need to remove/replace into /test"""
    command = 'capture_average(r"{}", 10)'.format(r'C:\Users\Public\Documents\Python Scripts\testclienth5.h5')
    print('Trying Command: {}'.format(command))
    conn_success = send_command(command)
    return conn_success

def filetransfercheck():
    """Debug function. Neet to remove/replace into /test"""
    fname_send = r'C:\Users\James Johnson\Google Drive\materialsLabShared\4D_tests_data\180322_pellicle_testing\20180322_01_RefFlat.h5'
    fname_save = r'C:\Users\Public\Documents\Python Scripts\testsavetx1h5.h5'
    command = 'self.send_file(r"{}")'.format(fname_send)
    print('Trying Command: {}'.format(command))
    conn_success = send_command(command, fname=fname_save)
    return conn_success

if __name__ == "__main__":
    #ss=scheck(ip_addr='127.0.0.1',port=61112)
    #filesavecheck()
    fil = filetransfercheck()
    # send_command('np.sum([1,1])')
    # #scheck()
    # send_command('1+1')
