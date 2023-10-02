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


# with element tag
del data_set[0x0043, 0x104E]
print(f"0x0043, 0x104E in data set? {[0x0043, 0x104E] in data_set}")

# with standard element
del data_set.WindowCenter

# multivalue element
del data_set.OtherPatientIDsSequence[2]
del ds.ImageType[2]