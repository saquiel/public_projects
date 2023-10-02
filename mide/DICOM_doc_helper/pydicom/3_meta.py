#! /usr/bin/env python3
# coding = utf-8


from pydicom.data import get_testdata_file
from pydicom import dcmread

# A/ open a DICOM file
# get the path to the test file
fpath = get_testdata_file("CT_small.dcm")
# read the DICOM dataset
data_set = dcmread(fpath)


# Meta
# all the elements in the file_meta are group 0x0002
print(f"Preamble header: {data_set.preamble}")

print(f"File meta information:\n {data_set.file_meta}")

# (0002,0010) Transfer Syntax UID:
# the transfer syntax defines the way the entire dataset 
# (including the pixel data) has been encoded. 
print(f"\nTransfert syntax UID: {data_set.file_meta.TransferSyntaxUID}")

print(f"Transfert syntax UID: {data_set.file_meta.TransferSyntaxUID.name} ")
