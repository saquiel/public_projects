import os

from pydicom import dcmread
from pydicom.dataset import Dataset

from pynetdicom import AE, evt
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind


# C_FIND SCP server for AN

# Implement the handler for evt.EVT_C_FIND
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

handlers = [(evt.EVT_C_FIND, handle_find)]

# Initialise the Application Entity and specify the listen port
ae = AE()

# Add the supported presentation context
ae.add_supported_context(PatientRootQueryRetrieveInformationModelFind)

# Start listening for incoming association requests
ae.start_server(("127.0.0.1", 11112), evt_handlers=handlers)

