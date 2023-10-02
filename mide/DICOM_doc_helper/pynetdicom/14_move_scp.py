#! /usr/bin/env python3
# coding = utf-8

import os

from pydicom import dcmread
from pydicom.dataset import Dataset

from pynetdicom import AE, StoragePresentationContexts, evt, debug_logger
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelMove

from multiprocessing import Process
import time

debug_logger()


# Implement the evt.EVT_C_MOVE handler
def handle_move(event):
    """Handle a C-MOVE request event."""
    ds_query = event.identifier

    if 'QueryRetrieveLevel' not in ds_query:
        # Failure
        return 0xC000

    ds_stored = dcmread(stored_dicom)
    
    print("EVENT MOVE DESTINATION:")
    print(event.move_destination)

# The C-MOVE request handler must yield the (address, port) of the destination AE, 
# then yield the number of sub-operations, 
# then yield (status, dataset) pairs.

    if event.move_destination == b'STORE_SCP':
        print("-------knowned------------")
        # addr = "127.0.0.1"
        # port = 11112
# The C-MOVE request handler must yield the (address, port) of the destination AE, 
        yield ("127.0.0.1", 11112)
    else:
        # Unknown destination AE
        yield (None, None)
        return


    if ds_query.QueryRetrieveLevel == 'STUDY' and ds_query.AccessionNumber == ds_stored.AccessionNumber:
        print("----------passed----------------")
        status =  0xC000

    else:
        print("not in PACS")
        status = 0x0000

# then yield the number of sub-operations
    yield 0
    print("----------yield sub op ok---------")

# then yield (status, dataset) pairs.
    yield (0000, 1)
    print("----------yield status dataset ok---------")

    return status



def move_scp(stored_dicom):
    
    print("enter move_scp")

    handlers = [(evt.EVT_C_MOVE, handle_move)]

    # Create application entity
    ae = AE()

    # Add the requested presentation contexts (Storage SCU)
    ae.requested_contexts = StoragePresentationContexts
    # Add a supported presentation context (QR Move SCP)
    ae.add_supported_context("1.2.840.10008.5.1.4.1.2.1.2")

    # Start listening for incoming association requests
    scp = ae.start_server(('', 11112), evt_handlers=handlers)
    print("server started")
    return scp



if __name__ == '__main__':


    stored_dicom = "/home/zenbook/Documents/code/python/dicom/output/1.3.6.1.4.1.14519.5.2.1.7777.9002.108821836759549281694712274169"
    move_scp(stored_dicom)