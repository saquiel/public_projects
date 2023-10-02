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

# save 1
data_set.save_as('code/python/theory/dicom/pynetdicom/output.dcm')

# save 2
with open('code/python/theory/dicom/pynetdicom/output.dcm', 'wb') as outfile:
    data_set.save_as(outfile)

# save 3
from io import BytesIO
out = BytesIO()
data_set.save_as(out)


# By default, save_as() will write the dataset as-is.
# This means that even if your dataset is not conformant to the DICOM File Format 
# it will still be written exactly as given. 
# To be certain you’re writing the dataset in the DICOM File Format 
# you can use the write_like_original keyword parameter:

data_set.save_as('code/python/theory/dicom/pynetdicom/output.dcm', write_like_original=False)

# remove the file meta to create an error
# del data_set.file_meta

data_set.save_as('code/python/theory/dicom/pynetdicom/output.dcm', write_like_original=False)
# The exception message contains the required element(s) 
# that need to be added, usually this will only be the Transfer Syntax UID. 
# It’s an important element, so get in the habit of making sure it’s there and correct.

# add a file meta
# data_set.file_meta = FileMetaDataset()