#! /usr/bin/env python3
# coding = utf-8


# In a new terminal, start echoscp listening for connection requests on port 11112
# python -m pynetdicom echoscp 11112 -v

from pynetdicom import AE
from pynetdicom import debug_logger

# activate debug mode on terminal
debug_logger()

# Instance the Application Entity object
ae = AE(ae_title=b'DEVICE') # set AE title

# Presentation abstract context initialization
# 1.2.840.10008.1.1: proposes the use of the verification SOP class service
ae.add_requested_context('1.2.840.10008.1.1')

# Establish connection to SCP
# target IP, target port
# connection to local host
# assoc = ae.associate('127.0.0.1', 11112)

# connection to ORTHANC on 192.168.1.3 port 4242
assoc = ae.associate('192.168.1.100', 4242, ae_title=b'ORTHANC')

# associate()

# return an Association instance: subclass of threading.thread (connextion on subprocess)


# if the association has been established
if assoc.is_established:
    print('Association established with Echo SCP!')

    # send the C-ECHO request
    status = assoc.send_c_echo()


    # send an association release request
    assoc.release()
    # If you don’t release the association yourself then it’ll remain established until the connection is closed, usually when a timeouts expires on either the requestor or acceptor AE.
else:
    # Association rejected, aborted or never connected
    print('Failed to associate')
