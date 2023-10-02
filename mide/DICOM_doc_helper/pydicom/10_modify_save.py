#! /usr/bin/env python3
# coding = utf-8


from pydicom import dcmread
from pydicom.datadict import dictionary_VR





# read the DICOM dataset
pydicom_dataset = dcmread("/home/zenbook/Documents/code/python/dicom/data/multi_incidence/1IUPYRWDP28E8-res.dcm")
# pydicom_dataset = dcmread("/home/zenbook/Documents/code/python/dicom/output/1.3.6.1.4.1.14519.5.2.1.7777.9002.154181272448537806873380883469")


# print(pydicom_dataset[0x0008, 0x0050])

# set accession number:
# 0008,0050  Accession Number: 1234

pydicom_dataset[0x0008, 0x0050].insert('SH', '1234')

# print(pydicom_dataset[0x0008, 0x0050])


# save
# data_set.save_as('/home/zenbook/Documents/code/python/dicom/output/1IUPYRWDP28E8-res.dcm', write_like_original=False)

# remove the file meta to create an error
# del data_set.file_meta

