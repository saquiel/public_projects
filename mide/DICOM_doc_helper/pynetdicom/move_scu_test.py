#! /usr/bin/env python3
# coding = utf-8


import os
from pydicom.dataset import Dataset
from pynetdicom import AE, evt, debug_logger, AllStoragePresentationContexts, ALL_TRANSFER_SYNTAXES
from pydicom.filewriter import write_file_meta_info

# debug_logger()

# event occurs => call handler function
def handle_store(event, storage_dir):
    """Handle EVT_C_STORE events."""

    # We rely on the UID from the C-STORE request instead of decoding
    fname = os.path.join(storage_dir, event.request.AffectedSOPInstanceUID)
    with open(fname, 'wb') as f:
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



# Variable initialization
output_folder = "/Documents/code/python/dicom/output"
aet_name = b'DEVICE'
aet_port = 10400

# Study Root Query/Retrieve Information Model – MOVE
sop_uid = "1.2.840.10008.5.1.4.1.2.1.2"

query_level = "STUDY"
StudyInstanceUID =  "1.1.827.205.609781.689" # <= SIUID to query
pacs_ip = '192.168.1.100'
pacs_port = 4242
pacs_title = b'ORTHANC'


# on event C-Store call handler
handlers = [(evt.EVT_C_STORE, handle_store, [output_folder])]

# Initialise the Application Entity
ae = AE()

# Add a requested presentation context
ae.add_requested_context(sop_uid)

# support both compressed and uncompressed transfer syntaxes:
# separate out the abstract syntaxes then use add_supported_context() with ALL_TRANSFER_SYNTAXES instead
storage_sop_classes = [cx.abstract_syntax for cx in AllStoragePresentationContexts]
for uid in storage_sop_classes:
    ae.add_supported_context(uid, ALL_TRANSFER_SYNTAXES)

# Start our Storage SCP in non-blocking mode, listening on port 11120
ae.ae_title = aet_name
scp = ae.start_server(("", aet_port), block=False, evt_handlers=handlers)

# Create out identifier (query) dataset
ds_query = Dataset()
# Add query retrieve level
ds_query.QueryRetrieveLevel = query_level

# add assession number
# ds_query.AccessionNumber = accession_number
ds_query.StudyInstanceUID =  StudyInstanceUID

ds_query.query_key_type = "StudyInstanceUID"

# Associate with peer AE IP and port
assoc = ae.associate(pacs_ip, pacs_port, ae_title = pacs_title)

if assoc.is_established:
    # Use the C-MOVE service to send the identifier
    responses = assoc.send_c_move(ds_query, aet_name, sop_uid)

    for (status, identifier) in responses:
        if status:
            service_status = status.Status
            print(f'C-MOVE query status: 0x{service_status:04x}')

        else:
            service_status = 0xC002

    # Release the association
    assoc.release()
else:
    # Association rejected, aborted or never connected
    service_status = 0xC003


# Stop our Storage SCP
scp.shutdown()