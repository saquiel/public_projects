#! /usr/bin/env python3
# coding = utf-8



# get data test

from pydicom import dcmread


path_to_dicom = "/home/zenbook/Documents/code/python/dicom/data/all_kind/IM2P/790740f96ae57396d709aa767805d2daa544e0af8fdc88a69a74789b342d6f0d.dcm"

ds_dicom = dcmread(path_to_dicom)

print(ds_dicom.file_meta)