#! /usr/bin/env python3
# coding = utf-8


from pynetdicom.presentation import PresentationContext

# instance a presentation context class
cx = PresentationContext()

# Context ID: odd-integer (1 to 255) identifies the context.
cx.context_id = 1 # pynetdicom deal with it

# Abstract Syntax: defines what the data represents, usually identified by a DICOM SOP Class UID
cx.abstract_syntax = '1.2.840.10008.1.1' # Verification SOP Class


# The Transfer Syntax defines how the data is encoded, usually identified by a DICOM Transfer Syntax UID:
cx.transfer_syntax = ['1.2.840.10008.1.2', '1.2.840.10008.1.2.4.50']
#                    ['Implicit VR Little Endian', 'JPEG Baseline']

print(f"Presentation context class:\n {cx}")

# However it’s easier to use the build_context() convenience function which returns a PresentationContext instance:
from pynetdicom import build_context

cx = build_context(
    '1.2.840.10008.1.1', ['1.2.840.10008.1.2', '1.2.840.10008.1.2.4.50']
)

cx = build_context('1.2.840.10008.1.1')
print(f"default transfert syntaxes:\n{cx}  ") 