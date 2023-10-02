#! /usr/bin/env python3
# coding = utf-8

# echoscu -ll debug -aet DEVICE -aec DEVICE 127.0.0.1 11112


from pynetdicom import AE, evt, debug_logger
from pynetdicom.sop_class import VerificationSOPClass

debug_logger()

# Implement a handler for evt.EVT_C_ECHO
def handle_echo(event):
    """Handle a C-ECHO request event."""
    return 0x0000

handlers = [(evt.EVT_C_ECHO, handle_echo)]

ae = AE()
ae.add_supported_context(VerificationSOPClass)
ae.start_server(('', 10400), evt_handlers=handlers)