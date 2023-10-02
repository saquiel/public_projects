#! /usr/bin/env python3
# coding = utf-8

# storescu localhost 10400 "/home/zenbook/Documents/gleamer/venv_exporter/glm-export-data/raw_data/data/risf/A10027449663/CR.1.3.12.2.1107.5.3.33.7534.11.202005301443480920" -aec DEVICE -ll info


# store SCU: ask for storing a dicom scanner to SCP
# python -m pynetdicom storescu 127.0.0.1 11112 /home/zenbook/Documents/code/python/dicom/data/CTImageStorage.dcm -v -cx

# storescu -ll info -aec DEVICE localhost 10400 "/home/zenbook/Documents/code/python/dicom/data/cancer_dicom/ID_0000_AGE_0060_CONTRAST_1_CT.dcm"



# python 
# dcmsend -ll info -aec DEVICE localhost 10400 "/home/zenbook/Documents/code/python/dicom/data/cancer_dicom/ID_0000_AGE_0060_CONTRAST_1_CT.dcm"


import os
from pydicom.filewriter import write_file_meta_info
from pynetdicom import AE, debug_logger, evt, AllStoragePresentationContexts, ALL_TRANSFER_SYNTAXES


# activate debug mode on terminal
debug_logger()


# event occurs => call handler function
def handle_store(event, storage_dir):
    """Handle EVT_C_STORE events."""
    # try:
    #     os.makedirs(storage_dir, exist_ok=True)
    # except:
    #     # Unable to create output dir, return failure status
    #     print("PROBLEM !!!")
    #     return 0xC001

    # We rely on the UID from the C-STORE request instead of decoding
    #fname = os.path.join(storage_dir, event.request.AffectedSOPInstanceUID)
    # with open(fname, 'wb') as f:
    #     # write 128 bits preamble header
    #     f.write(b'\x00' * 128)
    #     # write 4 bits DICOM prefix
    #     f.write(b'DICM')
    #     # write meta info about the SCU encoded file
    #     write_file_meta_info(f, event.file_meta)
    #     # write SCU encoded data set
    #     f.write(event.request.DataSet.getvalue())

    storage_dir = "/home/zenbook/Documents/code/python/dicom/output"

    ds = event.dataset
    ds.file_meta = event.file_meta
    file_path = os.path.join(storage_dir, ds.SOPInstanceUID + ".dcm")

    ds.save_as(file_path, write_like_original=False)

    # storage success
    return 0x0000


output_folder = "/home/zenbook/Documents/code/python/dicom/output"
# on event C-Store call handler
handlers = [(evt.EVT_C_STORE, handle_store, [output_folder])]


# Instance the Application Entity object
ae = AE()
# ae.ae_title = b"DEVICE"

# Presentation abstract context initialization
# Presentation context for all for every SOP Class Storage service

# To support both compressed and uncompressed transfer syntaxes we separate out the abstract syntaxes then use add_supported_context() with ALL_TRANSFER_SYNTAXES instead
storage_sop_classes = [cx.abstract_syntax for cx in AllStoragePresentationContexts]
# print(storage_sop_classes)
for uid in storage_sop_classes:
    ae.add_supported_context(uid, ALL_TRANSFER_SYNTAXES)
    # print(uid)
# starts our SCP listening for association requests:
# local host and port 10400
# blocking mode
# bind handler to event

scp = ae.start_server(('', 10400), block=True, evt_handlers=handlers)

# time.sleep(5)


# scp.shutdown()