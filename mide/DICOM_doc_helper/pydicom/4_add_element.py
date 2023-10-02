#! /usr/bin/env python3
# coding = utf-8


from pydicom.data import get_testdata_file
from pydicom import dcmread
from pydicom.datadict import dictionary_VR
from pydicom.dataset import Dataset


# get the path to the test file
fpath = get_testdata_file("CT_small.dcm")
# read the DICOM dataset
data_set = dcmread(fpath)


# Adding elements

# A/ Any category

# add the (0028,1050) Window Center standard element
# need to get the VR and the python type

# 1/ Value representation
print(f"Value representation: {dictionary_VR([0x0028, 0x1050])} ")
# https://pydicom.github.io/pydicom/stable/guides/element_value_types.html
# => str, float or int

# add the new element
data_set.add_new([0x0028, 0x1050], 'DS', "100.0")
print("\nNew element:")
print(data_set[0x0028, 0x1050])


# B/ Standard elements

# Adding elements with add_new() is a lot of work,
# so for standard elements you can just use the keyword and pydicom will do the lookup for you

# look for the element
print(f"\nIs WindowWidth in data_set? {'WindowWidth' in data_set}")
print(f"\nIs StudyID in data_set? {[0x0020, 0x000D] in data_set}")
# add the element
data_set.WindowWidth = 500
print(f"New element: {data_set['WindowWidth']}")

# This also works with element tags
print(f"0x0043, 0x104E in data_set? {[0x0043, 0x104E] in data_set}")


# C/ Sequences

# Because sequence items are also Dataset instances,
# you can use the same methods on them as well.

seq = data_set.OtherPatientIDsSequence
print(f"\nSome sequence:\n{seq}")

# add 3 data sets
seq += [Dataset(), Dataset(), Dataset()]
# add value
seq[0].PatientID = 'Citizen^Jan'
seq[0].TypeOfPatientID = 'TEXT'
seq[1].PatientID = 'CompressedSamples^CT1'
seq[1].TypeOfPatientID = 'TEXT'
print(f"\nSequence with values:\n{seq}")
print(f"\nsequence 0 and VR:\n{seq[0]}")
print(f"\nsequence 1 and VR:\n{seq[1]}")


