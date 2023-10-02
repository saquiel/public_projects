#! /usr/bin/env python3
# coding = utf-8


import os
from pydicom.filewriter import write_file_meta_info
from pynetdicom import AE, debug_logger, evt, AllStoragePresentationContexts, ALL_TRANSFER_SYNTAXES
from pydicom import dcmread
from pynetdicom.sop_class import CTImageStorage

import time

# activate debug mode on terminal
debug_logger()

def handle_store(event, storage_dir):
    """Handle EVT_C_STORE events."""
    try:
        os.makedirs(storage_dir, exist_ok=True)
    except:
        # Unable to create output dir, return failure status
        print("PROBLEM !!!")
        return 0xC001

    # We rely on the UID from the C-STORE request instead of decoding
    file_name = os.path.join(storage_dir, event.request.AffectedSOPInstanceUID)
    with open(file_name, 'wb') as f:
        # write 128 bits preamble header
        f.write(b'\x00' * 128)
        # write 4 bits DICOM prefix
        f.write(b'DICM')
        # write meta info about the SCU encoded file
        write_file_meta_info(f, event.file_meta)
        # write SCU encoded data set
        f.write(event.request.DataSet.getvalue())

    # storage success
    return 0x0000



def store_scp():

    output_folder = "/home/zenbook/Documents/code/python/dicom/output"
    # on event C-Store call handler
    handlers = [(evt.EVT_C_STORE, handle_store, [output_folder])]

    # Instance the Application Entity object
    ae = AE()

    # Presentation abstract context initialization
    # Presentation context for all for every SOP Class Storage service

    # To support both compressed and uncompressed transfer syntaxes we separate out the abstract syntaxes then use add_supported_context() with ALL_TRANSFER_SYNTAXES instead
    storage_sop_classes = [cx.abstract_syntax for cx in AllStoragePresentationContexts]

    for uid in storage_sop_classes:
        ae.add_supported_context(uid, ALL_TRANSFER_SYNTAXES)

    # starts our SCP listening for association requests:
    # local host and port 11112
    # blocking mode
    # bind handler to event
    scp = ae.start_server(('', 11112), block=False, evt_handlers=handlers)

    return scp

def store_scu():
    # Initialise the Application Entity
    ae = AE()

    # Add a requested presentation context
    ae.add_requested_context(CTImageStorage)

    # Read in our DICOM CT dataset
    ds = dcmread('/home/zenbook/Documents/code/python/dicom/data/cancer_dicom/ID_0000_AGE_0060_CONTRAST_1_CT.dcm')

    # Associate with peer AE at IP 127.0.0.1 and port 11112
    assoc = ae.associate('127.0.0.1', 11112)
    if assoc.is_established:
        # Use the C-STORE service to send the dataset
        # returns the response status as a pydicom Dataset
        status = assoc.send_c_store(ds)

        # Check the status of the storage request
        if status:
            # If the storage request succeeded this will be 0x0000
            print('C-STORE request status: 0x{0:04x}'.format(status.Status))
        else:
            print('Connection timed out, was aborted or received invalid response')

        # Release the association
        assoc.release()
    else:
        print('Association rejected, aborted or never connected')
    return


if __name__ == '__main__':
    

    scp = store_scp()


    time.sleep(0.2)

    store_scu()

    scp.shutdown()




