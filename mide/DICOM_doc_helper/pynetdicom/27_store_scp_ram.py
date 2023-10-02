#! /usr/bin/env python3
# coding = utf-8

# storescu localhost 10400 "/home/zenbook/Documents/gleamer/venv_exporter/glm-export-data/raw_data/data/risf/A10027449663/CR.1.3.12.2.1107.5.3.33.7534.11.202005301443480920" -aec DEVICE -ll info


# store SCU: ask for storing a dicom scanner to SCP
# python -m pynetdicom storescu 127.0.0.1 11112 /home/zenbook/Documents/code/python/dicom/data/CTImageStorage.dcm -v -cx

# storescu -ll info -aec DEVICE localhost 10400 "/home/zenbook/Documents/code/python/dicom/data/cancer_dicom/ID_0000_AGE_0060_CONTRAST_1_CT.dcm"


# python 
# dcmsend -ll info -aec DEVICE localhost 10400 "/home/zenbook/Documents/code/python/dicom/data/n109.dcm"


from glob import glob
import os
from pydicom.filewriter import write_file_meta_info
from pynetdicom import AE, debug_logger, evt, AllStoragePresentationContexts, ALL_TRANSFER_SYNTAXES


# activate debug mode on terminal
# debug_logger()


# event occurs => call handler function
def handle_store(event):
    """Handle EVT_C_STORE events."""

    # write the decoded dataset received from the SCU as a pydicom Dataset
    ds = event.dataset
    # set the dataset’s file_meta attribute
    ds.file_meta = event.file_meta

    list_dicom.append(ds)


    # storage success
    return 0x0000



list_dicom = []
# on event C-Store call handler
handlers = [(evt.EVT_C_STORE, handle_store, list_dicom)]


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


ae.start_server(('', 10400), block=False, evt_handlers=handlers)

import time
time.sleep(5)

ae.shutdown()


# time.sleep(5)
# print(list_dicom[0])
ds = list_dicom[0]

output_folder = "/home/zenbook/Documents/code/python/dicom/output/" + ds.SOPInstanceUID + ".dcm"



ds.save_as(output_folder, write_like_original=False)

print("saved")


# scp.shutdown()