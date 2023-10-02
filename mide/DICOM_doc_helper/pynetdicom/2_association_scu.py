#! /usr/bin/env python3
# coding = utf-8


from pynetdicom import AE, build_context
from pynetdicom.sop_class import VerificationSOPClass

# Presentation Contexts and the Association Requestor

# When acting as the association requestor (usually the SCU), 
# you must propose presentation contexts to be negotiated by the association process.


# Methode 1:
# Setting the AE.requested_contexts attribute directly using a list of PresentationContext items:

# instance a association requestor class
ae = AE()
# Setting the AE.requested_contexts attribute directly using a list of PresentationContext items
ae.requested_contexts = [build_context(VerificationSOPClass)]
assoc = ae.associate('127.0.0.1', 11112)


# Methode 2:
# Using the AE.add_requested_context() method to add a new PresentationContext to the AE.requested_contexts attribute.
ae = AE()
ae.add_requested_context(VerificationSOPClass)
assoc = ae.associate('127.0.0.1', 11112)


# Methode 3:
# Supplying a list of PresentationContext items to AE.associate() via the contexts keyword parameter.
ae = AE()
requested = [build_context(VerificationSOPClass)]
assoc = ae.associate('127.0.0.1', 11112, contexts=requested)
print(ae)

# The abstract syntaxes you propose should match the SOP Class or Meta SOP Class that corresponds to the service you wish to use. 
# For example, if you’re intending to use the storage service then you’d propose one or more abstract syntaxes from the corresponding SOP Class UIDs.