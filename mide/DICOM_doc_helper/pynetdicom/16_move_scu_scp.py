#! /usr/bin/env python3
# coding = utf-8

import os

from pydicom import dcmread
from pydicom.dataset import Dataset
from pynetdicom import AE, StoragePresentationContexts, evt, debug_logger
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

    if event.move_destination == b'STORE_SCP':
        print("-------knowned------------")

        # yield the (address, port) of the destination AE to the SCU
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

    # Yield the number of sub-operations to the SCU
    yield 0
    print("----------yield sub op ok---------")

    # Yield (status, dataset) pairs to the SCU
    yield (0000, 1)
    print("----------yield status dataset ok---------")

    return status


def move_scp(stored_dicom):
    
    print("enter move_scp")

    # Create application entity
    ae = AE()

    # Add the requested presentation contexts (Storage SCU)
    ae.requested_contexts = StoragePresentationContexts
    # Add a supported presentation context (QR Move SCP)
    ae.add_supported_context("1.2.840.10008.5.1.4.1.2.1.2")

    # Start listening for incoming association requests
    handlers = [(evt.EVT_C_MOVE, handle_move)]
    scp = ae.start_server(('', 11112), block=False, evt_handlers=handlers)
    
    return scp

def move_scu(accession_number):

    # Initialise the Application Entity
    ae = AE()

    # Add a requested presentation context
    ae.add_requested_context("1.2.840.10008.5.1.4.1.2.1.2")

    # Create out identifier (query) dataset
    ds = Dataset()
    ds.QueryRetrieveLevel = 'STUDY'

    ds.AccessionNumber = accession_number


    # Associate with peer AE at IP 127.0.0.1 and port 11112
    assoc = ae.associate('127.0.0.1', 11112)

    if assoc.is_established:
        # Use the C-MOVE service to send the identifier
        responses = assoc.send_c_move(ds, b'STORE_SCP', "1.2.840.10008.5.1.4.1.2.1.2")
        for (status, identifier) in responses:
            if status:
                service_status = status.Status
                print(f'C-MOVE query status: 0x{service_status:04x}')
            else:
                print('Connection timed out, was aborted or received invalid response')

        # Release the association
        assoc.release()
    else:
        print('Association rejected, aborted or never connected')

    return 0

if __name__ == '__main__':

    stored_dicom = "/home/zenbook/Documents/code/python/dicom/data/CTImageStorage.dcm"
    ds_stored = dcmread(stored_dicom)
    accession_number = ds_stored.AccessionNumber

    scp = move_scp(stored_dicom)

    print("server started")

    time.sleep(0.2)

    status = move_scu(accession_number)

    scp.shutdown()