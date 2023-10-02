#! /usr/bin/env python3
# coding = utf-8

import os
from pydicom.filewriter import write_file_meta_info
from pydicom import dcmread
from pydicom.dataset import Dataset

from pynetdicom import AE, StoragePresentationContexts, evt, debug_logger,AllStoragePresentationContexts, ALL_TRANSFER_SYNTAXES
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelMove
import json 
import time

debug_logger()




# Implement the evt.EVT_C_MOVE handler
def handle_move_scp(event):
    """Handle a C-MOVE request event."""
    ds_query = event.identifier

    if 'QueryRetrieveLevel' not in ds_query:
        # Failure
        yield 0xC000, None
        return 

    ds_stored = dcmread(stored_dicom)
    
    print("EVENT MOVE DESTINATION:")
    print(event.move_destination)

    print(f"--------------{event.move_destination}-----------------")


    if event.move_destination == aet_name:
        print("-------knowned------------")

        # yield the (address, port) of the destination AE to the SCU
        yield (aet_ip, aet_port)
    else:
        # Unknown destination AE
        yield (None, None)
        return

    if ds_query.QueryRetrieveLevel == query_level and ds_query.AccessionNumber == ds_stored.AccessionNumber:
        print("----------DICOM in PACS----------------")
        status =  0xC000
        # Yield the total number of C-STORE sub-operations required
        yield 1
        yield (0xFF00, ds_stored)
        return

    else:
        print("not in PACS")
        status = 0x0000
        yield (None, None)
        return



def move_scp(stored_dicom, aet_name, aet_port, aec_ip, aec_port, aec_title, sop_uid, query_level, accession_number, output_folder):
    
    print("enter move_scp")

    # Create application entity
    ae = AE()
    ae.ae_title = aec_title
    # Add the requested presentation contexts (Storage SCU)
    ae.requested_contexts = StoragePresentationContexts
    # Add a supported presentation context (QR Move SCP)
    ae.add_supported_context(sop_uid)

    # Start listening for incoming association requests
    handlers = [(evt.EVT_C_MOVE, handle_move_scp)]
    
    scp = ae.start_server((aec_ip, aec_port), block=False, evt_handlers=handlers)
    
    return scp


def handle_store(event, storage_dir):
    """Handle EVT_C_STORE events
    input:  trigger by evt.EVT_C_STORE
            path to the storage directory
    output: write the receive dicom in the storage directory
            return a storage success status      
    """

    # We rely on the UID from the C-STORE request instead of decoding
    file_name = os.path.join(storage_dir, event.request.AffectedSOPInstanceUID)
    with open(file_name, 'wb') as tmp_file:
        # write 128 bits preamble header
        tmp_file.write(b'\x00' * 128)
        # write 4 bits DICOM prefix
        tmp_file.write(b'DICM')
        # write meta info about the SCU encoded file
        write_file_meta_info(tmp_file, event.file_meta)
        # write SCU encoded data set
        tmp_file.write(event.request.DataSet.getvalue())

    # storage success
    return 0x0000


def move_scu_2(aet_name, aet_port, aec_ip, aec_port, aec_title, sop_uid, query_level, accession_number, output_folder):


    handlers = [(evt.EVT_C_STORE, handle_store, [output_folder])]

    # Initialise the Application Entity
    ae = AE()
    ae.ae_title = aet_name
    # Add a requested presentation context
    ae.add_requested_context(sop_uid)

    # support both compressed and uncompressed transfer syntaxes:
    # separate out the abstract syntaxes then use add_supported_context() with ALL_TRANSFER_SYNTAXES instead
    storage_sop_classes = [cx.abstract_syntax for cx in AllStoragePresentationContexts]
    for uid in storage_sop_classes:
        ae.add_supported_context(uid, ALL_TRANSFER_SYNTAXES)

    # Start our Storage SCP in non-blocking mode, listening on port 11120
    
    scp = ae.start_server(("", aet_port), block=False, evt_handlers=handlers)


    # Create out identifier (query) dataset
    ds_query = Dataset()
    ds_query.QueryRetrieveLevel = query_level

    ds_query.AccessionNumber = accession_number

    # Associate with peer AE at IP 127.0.0.1 and port 11112
    assoc = ae.associate(aec_ip, aec_port, ae_title = aec_title)


    if assoc.is_established:
        # Use the C-MOVE service to send the identifier
        responses = assoc.send_c_move(ds_query, aet_name, sop_uid)
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

    scp.shutdown()

    return 0


def initialization(path_to_json, pacs_name):
    """
    Initialise extractor with a json
    input:  json
    output: aet_name, aet_port, aec_title, aec_ip, aec_port, output_folder
    """
    with open(path_to_json, "r") as tmp_file:
        dict_init = json.load(tmp_file)

    # AE name encoded in bytes ascii
    aet_name = dict_init[pacs_name]["aet_name"].encode('ascii')
    aet_ip = dict_init[pacs_name]["aet_ip"]
    aet_port = dict_init[pacs_name]["aet_port"]
    aec_title = dict_init[pacs_name]["aec_title"].encode('ascii')
    aec_ip = dict_init[pacs_name]["aec_ip"]
    aec_port = dict_init[pacs_name]["aec_port"]
    output_folder = dict_init[pacs_name]["output_folder"]

    return aet_name, aet_ip, aet_port, aec_title, aec_ip, aec_port, output_folder


if __name__ == '__main__':

    aet_name, aet_ip, aet_port, aec_title, aec_ip, aec_port, output_folder = initialization("extractor.json", "unit_test")

    stored_dicom = "/home/zenbook/Documents/code/python/dicom/data/cancer_dicom/ID_0000_AGE_0060_CONTRAST_1_CT.dcm"
    
    ds_stored = dcmread(stored_dicom)
    accession_number = ds_stored.AccessionNumber
    sop_uid = "1.2.840.10008.5.1.4.1.2.1.2"
    query_level = "STUDY"

    scp = move_scp(stored_dicom, aet_name, aet_port, aec_ip, aec_port, aec_title, sop_uid, query_level, accession_number, output_folder)

    print("server started")

    time.sleep(0.2)

    move_scu_2(aet_name, aet_port, aec_ip, aec_port, aec_title, sop_uid, query_level, accession_number, output_folder)
