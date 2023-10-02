#! /usr/bin/env python3
# coding = utf-8


from pydicom.dataset import Dataset

from pynetdicom import AE, debug_logger
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind, StudyRootQueryRetrieveInformationModelFind

# debug_logger()




def c_find_study_uid(aet_title, aec_title, aec_ip, aec_port, accession_number):
    ae = AE(ae_title=aet_title)

    # Presentation abstract context initialization
    # verification SOP class service
    # Study Root Query/Retrieve Information Model – FIND
    ae.add_requested_context('1.2.840.10008.5.1.4.1.2.1.1')

    # Create our Identifier (query) dataset
    ds = Dataset()
    # Add query retrieve level
    ds.QueryRetrieveLevel = 'STUDY'
    # add assession number

    # ds.AccessionNumber="33.2165191"
    # ds.AccessionNumber="12.3456789"

    ds.AccessionNumber=accession_number
    ds.StudyInstanceUID = "" #please return Study UID

    # assoc = ae.associate('192.168.1.100', 4242, ae_title=b'ORTHANC')
    # assoc = ae.associate('127.0.0.1', 11112, ae_title=b'LOCAL')
    assoc = ae.associate(aec_ip, aec_port, ae_title=aec_title)

    study_instance_uid = []
    if assoc.is_established:
        # Send the C-FIND request
        responses = assoc.send_c_find(ds, PatientRootQueryRetrieveInformationModelFind)
        for (status, identifier) in responses:
            if status:
                print(f"C-FIND query status: {status.Status}")
                try:
                    study_instance_uid.append(str(identifier[0x0020, 0x000d].value))
                    c_find_status = "c_find_ok"
                    assoc.release()
                    return study_instance_uid, c_find_status
                except:
                    c_find_status = "c_find_no_study_uid"

            else:
                c_find_status = "c_fing_invalid_response"

        assoc.release()
        return study_instance_uid, c_find_status
    else:
        c_find_status = "c_find_association_fail"
    
    return study_instance_uid, c_find_status





aet_title = b'DEVICE'
aec_title = b'ORTHANC'
aec_ip = "192.168.1.100"
aec_port = 4242


accession_number = "33.2165191"

study_instance_uid, c_find_status = c_find_study_uid(aet_title, aec_title, aec_ip, aec_port, accession_number)

print(f"C_FIND status: {c_find_status}")
print(f"Study UID: {study_instance_uid} ")

