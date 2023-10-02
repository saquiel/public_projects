#! /usr/bin/env python3
# coding = utf-8


from pynetdicom import AE, build_context
from pynetdicom.sop_class import VerificationSOPClass


# Presentation Contexts and the Association Acceptor

# When acting as the association acceptor (usually the SCP), 
# you should define which presentation contexts will be supported. 
# Unlike the requestor you can define an unlimited number of supported presentation contexts.


# methode 1
# Setting the AE.supported_contexts attribute directly using a list of PresentationContext items.
ae = AE()
ae.supported_contexts = [build_context(VerificationSOPClass)]

# start the SCP server:
# ae.start_server(('', 11112))


# methode 2:
# Using the AE.add_supported_context() method to add a new PresentationContext to the AE.supported_contexts attribute.
ae = AE()
ae.add_supported_context(VerificationSOPClass)
# ae.start_server(('', 11112))

# methode 3:
# Supplying a list of PresentationContext items to AE.start_server() via the contexts keyword parameter
ae = AE()
supported = [build_context(VerificationSOPClass)]
#ae.start_server(('', 11112), contexts=supported)

print(ae)

# The abstract syntaxes you support should correspond to the service classes that are being offered. 
# For example, if you offer the Storage Service then you should support one or more of the Storage Service’s corresponding SOP Classes.