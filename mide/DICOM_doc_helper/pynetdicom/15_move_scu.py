#! /usr/bin/env python3
# coding = utf-8


from pydicom.dataset import Dataset

from pynetdicom import AE, evt, debug_logger, StoragePresentationContexts
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelMove, StudyRootQueryRetrieveInformationModelMove

debug_logger()



def move_scu():

    # Initialise the Application Entity
    ae = AE()
    ae.ae_title = b"DEVICE"

    # Add a requested presentation context
    # ae.add_requested_context("1.2.840.10008.5.1.4.1.2.1.2")
    ae.add_requested_context(StudyRootQueryRetrieveInformationModelMove)
    # Create out identifier (query) dataset
    ds = Dataset()
    
    # ds.PatientID
    # ds.StudyInstanceUID
    # ds.SeriesInstanceUID
    
    
    ds.QueryRetrieveLevel = 'STUDY'


    # ds.QueryRetrieveLevel = ''
    # ds.PatientID = ''
    # ds.StudyInstanceUID = ''
    # ds.SeriesInstanceUID = ''

# python -m pynetdicom movescu 192.168.1.100 4242 -k QueryRetrieveLevel=STUDY -aet DEVICE -aem DEVICE -aec ORTHANC -k StudyInstanceUID="1.2.250.1.439.0.1"
# movescu -v -S -k QueryRetrieveLevel=STUDY -aet DEVICE -aem DEVICE -aec ORTHANC 192.168.1.100 4242 -k StudyInstanceUID="1.2.250.1.439.0.1"

    # query CR:
    ds.StudyInstanceUID = "1.1.827.205.609781.689"

    # # query MRI:
    # ds.StudyInstanceUID = "2.16.124.113543.6006.99.5636401464989547188" 

    # ds.AccessionNumber = "2531514838096696"



    # Associate with peer AE at IP 127.0.0.1 and port 11112
    assoc = ae.associate('192.168.1.100', 4242, ae_title=b'ORTHANC')

    if assoc.is_established:
        # Use the C-MOVE service to send the identifier
        responses = assoc.send_c_move(ds, b'DEVICE', StudyRootQueryRetrieveInformationModelMove)
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

    return 0


move_scu()