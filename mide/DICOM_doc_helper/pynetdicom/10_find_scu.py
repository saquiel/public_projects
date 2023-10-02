#! /usr/bin/env python3
# coding = utf-8

from pydicom.dataset import Dataset
from pynetdicom import AE, debug_logger
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind

# debug_logger()

ae = AE(ae_title=b'DEVICE')

# Presentation abstract context initialization
# verification SOP class service
# Study Root Query/Retrieve Information Model – FIND
ae.add_requested_context('1.2.840.10008.5.1.4.1.2.1.1')

# Create our Identifier (query) dataset
ds = Dataset()
# Add query retrieve level
ds.QueryRetrieveLevel = 'STUDY'
# add assession number

# ask for patient ID field
# ds.PatientID =""

# ds.AccessionNumber="2531514838096696"
ds.AccessionNumber="3044380396396460"
# ds.StudyInstanceUID =  "1001" 

# connection to ORTHANC on 192.168.1.3 port 4242
assoc = ae.associate('192.168.1.100', 4242, ae_title=b'ORTHANC')

if assoc.is_established:
    # Send the C-FIND request
    responses = assoc.send_c_find(ds, PatientRootQueryRetrieveInformationModelFind)
    for (status, identifier) in responses:
        if status:
            print('C-FIND query status: 0x{0:04X}'.format(status.Status))
        else:
            print('Connection timed out, was aborted or received invalid response')

        if identifier:
            print(identifier)
        else:
            print("No identifier")

    # Release the association
    assoc.release()
else:
    print('Association rejected, aborted or never connected')

