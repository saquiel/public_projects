#! /usr/bin/env python3
# coding = utf-8


import os
from pydicom.dataset import Dataset
from pynetdicom import AE, evt, StoragePresentationContexts, debug_logger, AllStoragePresentationContexts, ALL_TRANSFER_SYNTAXES
from pydicom.filewriter import write_file_meta_info
import pathlib





# TODO: Save in ram
def handle_store(event):
    """Handle EVT_C_STORE events
    input:  trigger by evt.EVT_C_STORE
            path to the storage directory
    output: write the receive dicom in the storage directory
            return a storage success status      
    """

    # We rely on the UID from the C-STORE request instead of decoding
    dicom_name = event.request.AffectedSOPInstanceUID

    path_to_folder = "/home/zenbook/Documents/code/python/dicom/output"
    file_path = pathlib.Path.cwd().joinpath(path_to_folder, dicom_name+".dcm")

    # save the DICOM
    with open(file_path, 'wb') as tmp_file:
        # write 128 bits preamble header
        tmp_file.write(b'\x00' * 128)
        # write 4 bits DICOM prefix
        tmp_file.write(b'DICM')
        # write meta info about the SCU encoded file
        write_file_meta_info(tmp_file, event.file_meta)
        # write SCU encoded data set
        tmp_file.write(event.request.DataSet.getvalue())

    return 0x0000

# TODO search to avoid handler
def move_scu(aet_title, aet_port, aec_ip, aec_port, aec_title, ds_query):
    """
    DICOM MOVE_SCU service
        build and start a STORE_SCP service
        build and request a MOVE_SCU to the AEC
        STORE_SCP wait for the AEC response
        close the STORE_SCP service

    input:  aet_title, aet_port, aec_ip, aec_port, aec_title, ser_log
    output: Service _status:
        0xC001: Connection timed out, was aborted or received invalid response
        0xC002: Association rejected, aborted or never connected
    """

    # on event C-Store call handler
    handlers = [(evt.EVT_C_STORE, handle_store)]

    # Initialise the Application Entity
    ae = AE()
    ae.ae_title = aet_title

    # Study Root Query/Retrieve Information Model – MOVE SOP UID
    sop_uid = "1.2.840.10008.5.1.4.1.2.1.2"
    # Add a requested presentation context
    ae.add_requested_context(sop_uid)

    # support both compressed and uncompressed transfer syntaxes:
    # separate out the abstract syntaxes then use add_supported_context() with ALL_TRANSFER_SYNTAXES instead
    storage_sop_classes = [
        cx.abstract_syntax for cx in AllStoragePresentationContexts]
    for uid in storage_sop_classes:
        ae.add_supported_context(uid, ALL_TRANSFER_SYNTAXES)

    # Start our Storage SCP in non-blocking mode, listening on port 11120
    scp = ae.start_server(("", aet_port), block=False, evt_handlers=handlers)

    # Associate with peer AE IP and port
    assoc = ae.associate(aec_ip, aec_port, ae_title=aec_title)

    if assoc.is_established:
        # Use the C-MOVE service to send the identifier

        responses = assoc.send_c_move(ds_query, aet_title, sop_uid)

        for (status, identifier) in responses:
            if status:
                service_status = status.Status
            else:
                service_status = 0xC002

        # Release the association
        assoc.release()
    else:
        # Association rejected, aborted or never connected
        service_status = 0xC003

    # Stop our Storage SCP
    scp.shutdown()

    return service_status


if __name__ == '__main__':


    output_folder = "/home/zenbook/Documents/code/python/dicom/output"

    aet_title = b'DEVICE'

    aet_port = 10400
    
    # Study Root Query/Retrieve Information Model – MOVE
    # SOP UID: 1.2.840.10008.5.1.4.1.2.2.2
    study_instance_uid = "1.2.840.10008.5.1.4.1.2.1.2"

    query_level = "STUDY"

    accession_number = "2531514838096696"

    aec_ip = '192.168.1.100'

    aec_port = 4242

    aec_title = b'ORTHANC'

    query_key_type = "StudyInstanceUID"

    # Create out identifier (query) dataset
    ds_query = Dataset()
    # Add query retrieve level
    ds_query.QueryRetrieveLevel = query_level
    # set query key to the query attribute
    setattr(ds_query, query_key_type, study_instance_uid)


    service_status = move_scu(aet_title, aet_port, aec_ip, aec_port, aec_title, ds_query)

    print(service_status)


