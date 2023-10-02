#! /usr/bin/env python3
# coding = utf-8



from pynetdicom import AE, build_role
from pynetdicom.pdu_primitives import SCP_SCU_RoleSelectionNegotiation
from pynetdicom.sop_class import CTImageStorage, MRImageStorage



# Presentation context negotiation for SCP/SCU Role Selection

# an association requestor to propose its role (SCU, SCP, or SCU and SCP) for each proposed abstract syntax.

# Role selection is used for services such as the Query/Retrieve Service’s C-GET requests, where the association acceptor sends data back to the requestor.



# 1/ SCP/SCU Role Selection as a requestor

# instance a association requestor class
ae = AE()
# add CTImageStorage PresentationContext to the AE.requested_contexts attribute.
ae.add_requested_context(CTImageStorage)
# add MRImageStorage PresentationContext to the AE.requested_contexts attribute.
ae.add_requested_context(MRImageStorage)

# include SCP_SCU_RoleSelectionNegotiation items in the extended negotiation
# A/ creating them from scratch
role_a = SCP_SCU_RoleSelectionNegotiation()
role_a.sop_class_uid = CTImageStorage
role_a.scu_role = True
role_a.scp_role = True
# B/ or using the build_role() convenience function
role_b = build_role(MRImageStorage, scp_role=True)

assoc = ae.associate('127.0.0.1', 11112, ext_neg=[role_a, role_b])


# 2/ SCP/SCU Role Selection as a acceptor
ae = AE()
ae.add_supported_context(CTImageStorage, scu_role=True, scp_role=False)
# ae.start_server(('', 11112))


# As can be seen there are four possible outcomes:

#     Requestor is SCU, acceptor is SCP (default roles)

#     Requestor is SCP, acceptor is SCU

#     Requestor and acceptor are both SCU/SCP

#     Requestor and acceptor are neither (context rejected)
