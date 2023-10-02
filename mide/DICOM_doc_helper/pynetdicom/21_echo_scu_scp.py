#! /usr/bin/env python3
# coding = utf-8

from pynetdicom import AE, evt, debug_logger
from pynetdicom.sop_class import VerificationSOPClass
import time

# activate debug mode on terminal
debug_logger()


# Implement a handler for evt.EVT_C_ECHO
def handle_echo(event):
    """Handle a C-ECHO request event."""
    return 0x0000


def echo_scp():
    # on event C-Store call handler
    handlers = [(evt.EVT_C_ECHO, handle_echo)]

    ae = AE()
    ae.ae_title = b"DEVICE"
    ae.add_supported_context(VerificationSOPClass)
    scp = ae.start_server(('', 11112), block=False, evt_handlers=handlers)
    return scp

def echo_scu():
    # Instance the Application Entity object
    ae = AE(ae_title=b'DEVICE') # set AE title

    # Presentation abstract context initialization
    # 1.2.840.10008.1.1: proposes the use of the verification SOP class service
    ae.add_requested_context('1.2.840.10008.1.1')

    # connection to ORTHANC on 192.168.1.3 port 4242
    assoc = ae.associate('127.0.0.1', 11112, ae_title=b'DEVICE')
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
    return status


if __name__ == '__main__':
    
    scp = echo_scp()

    time.sleep(0.2)

    status = echo_scu()
    print(f"Echo status: {status.Status}")

    scp.shutdown()