#! /usr/bin/env python3
# coding = utf-8


from pynetdicom import evt, AE
from pynetdicom.sop_class import VerificationSOPClass, CTImageStorage

def handle_echo(event):
    # Because we used a 2-tuple to bind `handle_echo` we
    #   have no extra parameters
    return 0x0000

def handle_store(event, arg1, arg2):
    # Because we used a 3-tuple to bind `handle_store` we
    #   have optional extra parameters
    assert arg1 == 'optional'
    assert arg2 == 'parameters'
    return 0x0000

handlers = [
    (evt.EVT_C_ECHO, handle_echo),
    (evt.EVT_C_STORE, handle_store, ['optional', 'parameters']),
]

ae = AE()
ae.add_supported_context(VerificationSOPClass)
ae.add_supported_context(CTImageStorage)
ae.start_server(('localhost', 11112), evt_handlers=handlers)