#! /usr/bin/env python3
# coding = utf-8


import os
import tempfile
import datetime

import pydicom
from pydicom.dataset import Dataset, FileDataset, FileMetaDataset



path_to_save = "/home/zenbook/Documents/code/python/dicom/output/test_dicom.dcm"

# Create some temporary filenames
suffix = '.dcm'
filename_little_endian = tempfile.NamedTemporaryFile(suffix=suffix).name
print(filename_little_endian)
print(type(filename_little_endian))


filename_big_endian = tempfile.NamedTemporaryFile(suffix=suffix).name

print("Setting file meta information...")
# Populate required values for file meta information
file_meta = FileMetaDataset()
file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'
file_meta.MediaStorageSOPInstanceUID = "1.2.3"
file_meta.ImplementationClassUID = "1.2.3.4"

print("Setting dataset values...")
# Create the FileDataset instance (initially no data elements, but file_meta
# supplied)
ds = FileDataset(filename_little_endian, {},
                 file_meta=file_meta, preamble=b"\0" * 128)

# Add the data elements -- not trying to set all required here. Check DICOM
# standard
ds.PatientName = "Test^Firstname"
ds.PatientID = "123456"

# Set the transfer syntax
ds.is_little_endian = True
ds.is_implicit_VR = True

# Set creation date/time
dt = datetime.datetime.now()
ds.ContentDate = dt.strftime('%Y%m%d')
timeStr = dt.strftime('%H%M%S.%f')  # long format with micro seconds
ds.ContentTime = timeStr

print("Writing test file", path_to_save)
ds.save_as(path_to_save)
print("File saved.")


ds = pydicom.dcmread(path_to_save)
print(ds)