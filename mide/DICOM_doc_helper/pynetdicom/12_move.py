#! /usr/bin/env python3
# coding = utf-8


import os
from pydicom.dataset import Dataset

from pynetdicom import AE, evt, StoragePresentationContexts, debug_logger, AllStoragePresentationContexts, ALL_TRANSFER_SYNTAXES
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelMove
from pydicom.filewriter import write_file_meta_info


debug_logger()

# event occurs => call handler function
def handle_store(event, storage_dir):
    """Handle EVT_C_STORE events."""

    try:
        os.makedirs(storage_dir, exist_ok=True)
    except:
        return 0xC001

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

output_folder = "/home/zenbook/Documents/code/python/dicom/output"
# on event C-Store call handler
handlers = [(evt.EVT_C_STORE, handle_store, [output_folder])]

# Initialise the Application Entity
ae = AE()

# support both compressed and uncompressed transfer syntaxes:
# separate out the abstract syntaxes then use add_supported_context() with ALL_TRANSFER_SYNTAXES instead
storage_sop_classes = [cx.abstract_syntax for cx in AllStoragePresentationContexts]
for uid in storage_sop_classes:
    ae.add_supported_context(uid, ALL_TRANSFER_SYNTAXES)


# Study Root Query/Retrieve Information Model – MOVE
# ae.add_requested_context('1.2.840.10008.5.1.4.1.2.2.2')
# Add a requested presentation context
ae.add_requested_context(PatientRootQueryRetrieveInformationModelMove)

# Add the Storage SCP's supported presentation contexts
ae.supported_contexts = StoragePresentationContexts

# Start our Storage SCP in non-blocking mode, listening on port 11120
ae.ae_title = b'DEVICE'
scp = ae.start_server(("", 10400), block=False, evt_handlers=handlers)

# Create out identifier (query) dataset
ds = Dataset()
# Add query retrieve level
ds.QueryRetrieveLevel = 'STUDY'
# add assession number
ds.AccessionNumber="2531514838096696"

# Associate with peer AE at IP 192.168.1.100 and port 4242
assoc = ae.associate('192.168.1.100', 4242, ae_title=b'ORTHANC')

if assoc.is_established:
    # Use the C-MOVE service to send the identifier
    responses = assoc.send_c_move(ds, b'DEVICE', PatientRootQueryRetrieveInformationModelMove)

    for (status, identifier) in responses:
        if status:
            print('C-MOVE query status: 0x{0:04x}'.format(status.Status))
        else:
            print('Connection timed out, was aborted or received invalid response')

    # Release the association
    assoc.release()
else:
    print('Association rejected, aborted or never connected')

# Stop our Storage SCP
scp.shutdown()

