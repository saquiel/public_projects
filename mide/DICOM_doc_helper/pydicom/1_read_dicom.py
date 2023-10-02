#! /usr/bin/env python3
# coding = utf-8



# get data test
from pydicom.data import get_testdata_file

from pydicom import dcmread

# A/ open a DICOM file
# get the path to the test file
fpath = get_testdata_file("CT_small.dcm")
print(fpath)

# read the DICOM dataset
data_set = dcmread(fpath)
# same with
with open(fpath, 'rb') as infile:
    data_set = dcmread(infile)
# with tricked dicom file => no exception
# data_set = dcmread(no_meta, force=True)


# B/ read a DICOM file

# print(data_set)
# The format of each line is:
# (0008, 0005): The element’s tag, as (group number, element number) in hexadecimal
# Specific Character Set: the element’s name, if known
# CS: The element’s Value Representation (VR), if known
# ‘ISO_IR_100’: the element’s stored value

# access a particular element in the dataset through its tag
data_elem = data_set[0x0008, 0x0016]
print("Data Element instance:")
print(data_elem)
private_elem = data_set[0x0043, 0x104E]
print(private_elem)
# access standard elements through their keyword
data_elem = data_set['SOPClassUID']
print(data_elem)

print("Element value:")
print(data_elem.value)
# list of value: http://dicom.nema.org/medical/dicom/current/output/chtml/part06/chapter_6.html

# multiple value
# multiple values
print("Multiple values:")
print(data_set.ImageType)
print(f"Number of values: {data_set['ImageType'].VM} ")
print(f"Second value: {data_set.ImageType[1]} ")