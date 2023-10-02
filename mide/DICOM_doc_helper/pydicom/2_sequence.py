#! /usr/bin/env python3
# coding = utf-8


from pydicom.data import get_testdata_file
from pydicom import dcmread

# A/ open a DICOM file
# get the path to the test file
fpath = get_testdata_file("CT_small.dcm")

# read the DICOM dataset
data_set = dcmread(fpath)

#print(data_set)

# DICOM datasets use the tree data structure, 
# with non-sequence elements acting as leaves 
# and sequence elements acting as the nodes where branches start.

# (0010, 1002)  Other Patient IDs Sequence  2 item(s) ---- 
#    (0010, 0020) Patient ID                          LO: 'ABCD1234'
#    (0010, 0022) Type of Patient ID                  CS: 'TEXT'
#    ---------
#    (0010, 0020) Patient ID                          LO: '1234ABCD'
#    (0010, 0022) Type of Patient ID                  CS: 'TEXT'
#    ---------                 CS: 'TEXT'

seq = data_set[0x0010, 0x1002]
seq = data_set['OtherPatientIDsSequence']
print(seq)
print(f"Number of subsequence:{len(data_set.OtherPatientIDsSequence)}")

print(data_set.OtherPatientIDsSequence[0])


