# interferometer-connect
Creates an IP connection to an interferometer to allow an external Python program to command and control the system.

interferometer-connect has only been tested with 4D interferometers using **4Sight 2.10 or greater** at this time. Data and commands are not encrypted and is not currently available. Consider any transmission to be open.


The software that ships with 4D (and Zygo) computers includes a compiled version of Python internal to the software. Because the Python environment (**4Sight** uses Python2.6, **Mx** uses Python3.4 as of 2019-01-01) is internal, it cannot add new modules via pip/conda nor can it access modules via *import* located on the users primary python installation. The *import* modules which control the interferometer are compiled into the executable and only accessible within the internal environment.


The module uses two separate files running on different environments (or computers).

The *connect4d.py* script is run from inside the **4Sight** python environment to create a Server. It must be run either as a Python Script from the GUI or from the internal Console ***(4Sight Menu: Tools >> Debug >> Open 4Sight Scripting Console)***. *connect4d.py* is preconfigured to only listen for connections on *localhost* and localnetwork (172.XXX.XXX.XXX and 192.XXX.XXX.XXX) and will need to be altered to point the Server to listen for external connections. 

The *connect_client.py* script is run outside of the **4Sight** environment and connects to the Server as a Client. It can pass commands as strings to the interferometer Server and retrieve *.h5* files.

## Basic Client-Side Commands

The Client script can pass the following commands to the Interferometer Server.

*connect4d.py* allows for an import of a user script that includes the **4Sight** python module imports to assist in automating data collection.
