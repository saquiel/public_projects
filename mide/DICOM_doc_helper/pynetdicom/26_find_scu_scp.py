#! /usr/bin/env python3
# coding = utf-8


from pydicom.dataset import Dataset

from pynetdicom import AE, evt, debug_logger
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind, StudyRootQueryRetrieveInformationModelFind
import time
# debug_logger()


def handle_find(event):
    """Handle a C-FIND request event."""

    ds = event.identifier
    an_instance = ["12.3456789", "98.7654321"]

    if 'QueryRetrieveLevel' not in ds:
        # Failure
        yield 0xC000, None
        return

    if ds.AccessionNumber in an_instance:
        print("AN in list")
        # Build DICOM dataset
        identifier = Dataset()
        identifier.StudyInstanceUID = "12.3456789"
        identifier.QueryRetrieveLevel = ds.QueryRetrieveLevel

        # Pending
        yield (0xFF00, identifier)
    else:
        print("not_found")

        

def c_find_study_uid(aet_title, aec_title, aec_ip, aec_port, accession_number):
    ae = AE(ae_title=aet_title)

    # Study Root Query/Retrieve Information Model – FIND
    ae.add_requested_context('1.2.840.10008.5.1.4.1.2.1.1')

    # Create our Identifier (query) dataset
    ds = Dataset()
    # Add query retrieve level
    ds.QueryRetrieveLevel = 'STUDY'
    # add assession number

    ds.AccessionNumber=accession_number
    ds.StudyInstanceUID = "" # Study UID query

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
        assoc.release()
    
    return study_instance_uid, c_find_status


aet_title = b'UT'
aec_title = b'LOCAL'
aec_ip = "127.0.0.1"
aec_port = 11112
accession_number = "12.3456789"

handlers = [(evt.EVT_C_FIND, handle_find)]

# Initialise the Application Entity and specify the listen port
ae = AE()

# Add the supported presentation context
ae.add_supported_context(PatientRootQueryRetrieveInformationModelFind)

# Start listening for incoming association requests
ae.start_server(("127.0.0.1", 11112), block=False, evt_handlers=handlers)

print("server started")
time.sleep(0.2)

study_instance_uid, c_find_status = c_find_study_uid(aet_title, aec_title, aec_ip, aec_port, accession_number)

print(f"Study UID: {study_instance_uid} ")

print(type(study_instance_uid))

ae.shutdown()