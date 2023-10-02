#! /usr/bin/env python3
# coding = utf-8


# store SCP: ask for storing a dicom scanner to SCP
# python -m pynetdicom storescu 127.0.0.1 11112 /home/zenbook/Documents/code/python/dicom/data/CTImageStorage.dcm -v -cx


from pydicom import dcmread
from pynetdicom import AE, debug_logger, StoragePresentationContexts
from pynetdicom.sop_class import CTImageStorage

debug_logger()

# Initialise the Application Entity
ae_scu = AE()
ae_scu.ae_title = b"DEVICE"
# Add a requested presentation context
ae_scu.requested_contexts = StoragePresentationContexts



# Read in our DICOM CT dataset
ds = dcmread('/home/zenbook/Documents/gleamer/venv_exporter/glm-export-data/raw_data/data/pacs/default_dicom/unknown_vr/DX.1.2.392.200046.100.14.181422110893939961618913563530073464142')



# Associate with peer AE at IP 127.0.0.1 and port 11112

# assoc = ae_scu.associate('127.0.0.1', 11112)
assoc = ae_scu.associate('192.168.1.100', 4242, b"ORTHANC")

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
