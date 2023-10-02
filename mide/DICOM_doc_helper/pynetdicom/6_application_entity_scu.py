#! /usr/bin/env python3
# coding = utf-8


from pydicom.uid import UID
from pynetdicom import AE, build_context, StoragePresentationContexts
from pynetdicom.sop_class import CTImageStorage


# Application Entity

# minimal initialisation of AE requires no parameters:
ae = AE() # create an AE with an AE title of b'PYNETDICOM      '

# AE title set with the ae_title keyword parameter
ae = AE(ae_title=b'MY_AE_TITLE')


# Or afterwards with the ae_title property:
ae = AE()
ae.ae_title = b'MY_AE_TITLE'


# Creating an SCU

# Adding requested Presentation Contexts


ae = AE()
ae.add_requested_context('1.2.840.10008.1.1')
ae.add_requested_context(UID('1.2.840.10008.5.1.4.1.1.4'))
ae.add_requested_context(CTImageStorage)

# Auto mode
ae = AE()
# Here StoragePresentationContexts is a prebuilt list of presentation contexts containing (almost) all the Storage Service Class’ supported SOP Classes, 
# and there’s a similar list for all the supported service classes.
ae.requested_contexts = StoragePresentationContexts

# Custom list of presentation contexts
ae = AE()
contexts = [
    build_context(CTImageStorage),
    build_context('1.2.840.10008.1.1')
]
ae.requested_contexts = contexts
print(ae)


ae = AE()
# add the first 17 contexts
ae.requested_contexts = StoragePresentationContexts[:127]
# add the 128 context (last)
ae.add_requested_context(VerificationSOPClass)
# number of max contexts: 128