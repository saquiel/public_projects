#! /usr/bin/env python3
# coding = utf-8


# store SCP: ask for storing a dicom scanner to SCP
# python -m pynetdicom storescu 127.0.0.1 11112 /home/zenbook/Documents/code/python/dicom/data/CTImageStorage.dcm -v -cx


from pydicom import dcmread
from pynetdicom import AE, debug_logger, StoragePresentationContexts
from pynetdicom.sop_class import CTImageStorage
import os

debug_logger()



def path_to_dicom(path_to_folder):
    '''Find all dicom file and return their path
        input:  folder to search
        output: list of dicom file path'''
    list_path = []
    for dirpath, dirs, files in os.walk(path_to_folder):  
                for filename in files:
                    path_to_file = os.path.join(dirpath,filename)
                    if path_to_file.endswith(".dcm"):
                        list_path.append(path_to_file)
    return(list_path)



# Initialise the Application Entity
ae = AE()

ae.requested_contexts = StoragePresentationContexts

ae.ae_title = b"DEVICE"
# Add a requested presentation context
# ae.requested_contexts = StoragePresentationContexts


# Associate with peer AE at IP 127.0.0.1 and port 11112

# assoc = ae_scu.associate('127.0.0.1', 11112)
assoc = ae.associate('192.168.1.100', 4242, b"ORTHANC")

print("------------here----------------")

path_to_dicom_folder = "/home/zenbook/Documents/gleamer/venv_exporter/glm-export-data/tmp_dicom"


if assoc.is_established:
    
    # loop through all DICOM paths
    list_path = path_to_dicom(path_to_dicom_folder)
    total_dicom = len(list_path)
    for path in list_path:
        # Read in our DICOM CT dataset
        ds = dcmread(path)


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

print(f" {total_dicom} DICOM file transferred ")