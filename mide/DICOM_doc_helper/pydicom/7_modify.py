#! /usr/bin/env python3
# coding = utf-8


from pydicom.data import get_testdata_file
from pydicom import dcmread

# A/ open a DICOM file
# get the path to the test file
fpath = get_testdata_file("CT_small.dcm")
# read the DICOM dataset
data_set = dcmread(fpath)


print(f"Name 0: {data_set[0x0010, 0x0010].value}")

data_set[0x0010, 0x0010].value = 'Citizen^Jan'

print(f"Name 1: {data_set[0x0010, 0x0010].value}")

# access by keyword elements
data_set.PatientName = 'Citizen^Snips'
print(f"Name 2: {data_set.PatientName}")

# multivalue elements
print("\nMultivalue elements ImageType:")
print(data_set.ImageType)
# change a the second value
data_set.ImageType[1] = 'DERIVED'
print(data_set.ImageType)
# add a value
data_set.ImageType.insert(1, 'PRIMARY')
print(data_set.ImageType)

# remove an element: None
print("\nPatientName:")
print(data_set.PatientName)
data_set.PatientName = None
print(data_set.PatientName)
