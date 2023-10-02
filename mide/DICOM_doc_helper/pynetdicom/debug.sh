#! /usr/bin/env python3
# coding = utf-8


from pynetdicom import debug_logger

# activate debug mode on terminal
debug_logger()

# log cathegories:
# I: state of associations and services
# E: errors
# D: content af messages

# echo scu:
I: Requesting Association # request association to the SCP
D: Request Parameters:
# 1/ association negociation
D: ======================= OUTGOING A-ASSOCIATE-RQ PDU ========================
D: Our Implementation Class UID:      1.2.826.0.1.3680043.9.3811.1.5.6
D: Our Implementation Version Name:   PYNETDICOM_156
D: Application Context Name:    1.2.840.10008.3.1.1.1
D: Calling Application Name:    PYNETDICOM      
D: Called Application Name:     ANY-SCP         
D: Our Max PDU Receive Size:    16382
D: Presentation Context:
D:   Context ID:        1 (Proposed)
# echo SCU SOP class
D:     Abstract Syntax: =Verification SOP Class
D:     Proposed SCP/SCU Role: Default
D:     Proposed Transfer Syntaxes:
D:       =Implicit VR Little Endian
D:       =Explicit VR Little Endian
D:       =Deflated Explicit VR Little Endian
D:       =Explicit VR Big Endian
D: Requested Extended Negotiation: None
D: Requested Common Extended Negotiation: None
D: Requested Asynchronous Operations Window Negotiation: None
D: Requested User Identity Negotiation: None
D: ========================== END A-ASSOCIATE-RQ PDU ==========================
D: Accept Parameters:
# 2/ association accepted by SCP
#    receive message
D: ======================= INCOMING A-ASSOCIATE-AC PDU ========================
D: Their Implementation Class UID:    1.2.826.0.1.3680043.9.3811.1.5.6
D: Their Implementation Version Name: PYNETDICOM_156
D: Application Context Name:    1.2.840.10008.3.1.1.1
D: Calling Application Name:    PYNETDICOM      
D: Called Application Name:     ANY-SCP         
D: Their Max PDU Receive Size:  16382
D: Presentation Contexts:
D:   Context ID:        1 (Accepted)
D:     Abstract Syntax: =Verification SOP Class
D:     Accepted SCP/SCU Role: Default
D:     Accepted Transfer Syntax: =Implicit VR Little Endian
D: Accepted Extended Negotiation: None
D: Accepted Asynchronous Operations Window Negotiation: None
D: User Identity Negotiation Response: None
D: ========================== END A-ASSOCIATE-AC PDU ==========================
I: Association Accepted
# 3/ release association
I: Releasing Association
Association established with Echo SCP!

# Error types:
TCP Initialisation error # nothing is listening on IP:port specified
# Check SCP is up and running and the firewall is allowing traffic through

Called AE title not recognized # SCP requires the A-ASSOCIATE-RQ's calling AE title value match its own.
# => set the ae_title keyword parameter in associate()

Calling AE title not recognized # SCP requires the A-ASSOCIATE-RQ's calling AE title value match its familliar with.
# => set the AE.ae_title property
# => configure the SCP with the details of the SCU

Local limit exceedded # SCP has too many current associations active
# => retry later

Association Aborded # Can happend during  DIMSE message (unusual during association negociation) 
# => SCP using TLS or other methods to secure the connection