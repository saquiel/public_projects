#! /usr/bin/env python3
# coding = utf-8



from pydicom import dcmread
from pydicom.data import get_testdata_file



filename = get_testdata_file("MR_small.dcm")
ds = dcmread(filename)
print(ds.PixelData)


arr = ds.pixel_array
arr[arr < 300] = 0
ds.PixelData = arr.tobytes()
ds.save_as("/home/zenbook/Documents/code/python/dicom/pydicom/temp.dcm")