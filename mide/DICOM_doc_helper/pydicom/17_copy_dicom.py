#! /usr/bin/env python3
# coding = utf-8


import os
import tempfile
import datetime

import pydicom
from pydicom import dcmread
from pydicom.dataset import Dataset, FileDataset, FileMetaDataset
import pandas as pd
from datetime import date
from random import randint
import hashlib

path_to_master = "/home/zenbook/Documents/code/python/dicom/data/all_kind/IM2P/790740f96ae57396d709aa767805d2daa544e0af8fdc88a69a74789b342d6f0d.dcm"
path_to_save = "/home/zenbook/Documents/code/python/dicom/output/test_dicom.dcm"
path_to_white_list = "/home/zenbook/Documents/Gleamer/glm-export-data/dicom_white_list.csv"

batch_name = "batch_1"
client_id = "CLIENT01"


ds_master = dcmread(path_to_master)
list_addr_dicom = list(ds_master.keys())

df_white_list = pd.read_csv(path_to_white_list, usecols=["tag", "private"])
list_to_copy = df_white_list[df_white_list["private"] != "x"]["tag"].to_list()

filename_little_endian = path_to_save

print(ds_master.file_meta[0x0002, 0x0002])

# print(ds_master)


# filename_big_endian = tempfile.NamedTemporaryFile(suffix=suffix).name

print("Setting file meta information...")
# Populate required values for file meta information
file_meta = FileMetaDataset()


file_meta.MediaStorageSOPClassUID = ds_master.file_meta[0x0002, 0x0002].value
file_meta.MediaStorageSOPInstanceUID = ds_master.file_meta[0x0002, 0x0003].value
# file_meta.TransferSyntaxUID = ds_master.file_meta[0x0002, 0x0010].value




file_meta.ImplementationClassUID = ds_master.file_meta[0x0002, 0x00012].value






print("Setting dataset values...")
# Create the FileDataset instance (initially no data elements, but file_meta supplied)
ds_dicom = FileDataset(filename_little_endian, {},
                 file_meta=file_meta, preamble=b"\0" * 128)

# Add the data elements -- not trying to set all required here. Check DICOM
# standard

for addr in list_addr_dicom:
    # delete DICOM tag that are not in the white list
    if  addr in list_to_copy:
        ds_dicom[addr] = ds_master[addr]

    # write DICOM tag


# block = ds_dicom.private_block(0x3679, "Gleamer", create=True)
# block.add_new(0x00, "US", 3)
# 3679,1000 US: exportVersion
ds_dicom.add_new([0x3679, 0x1000], "US", 3)
print(ds_dicom[0x3679, 0x1000])

# # 3679,1050 LO: exportBatchCode (batch name)
# ds_dicom.add_new([0x3679, 0x1050], "LO", batch_name)

# # 3679,1060 LO: clientId (client name)
# ds_dicom.add_new([0x3679, 0x1060], "LO", client_id)

# # 3679,1070 DA: '20190910': ExportDate
# today = date.today().strftime("%Y%m%d")
# ds_dicom.add_new([0x3679, 0x1070], "DA", today)

# # write hash DICOM values on Gleamer private tag
# # 3679,1010 LO: glmPatientId (hashage du PatientId [0x0010, 0x0020])
# try: glmPatientId = ds_dicom[0x0010, 0x0020].value.encode()
# except: glmPatientId = str(randint(0, 99999999)).encode()
# ds_dicom.add_new([0x3679, 0x1010], "LO", str(hashlib.sha256(glmPatientId).hexdigest()))


# # 3679,1020 LO: glmStudyId (hashage du StudyInstanceUID [0x0020, 0x000D])
# try: glmStudyId = ds_dicom[0x0010, 0x000D].value.encode()
# except: glmStudyId = str(randint(0, 99999999)).encode()
# ds_dicom.add_new([0x3679, 0x1020], "LO", hashlib.sha256(glmStudyId).hexdigest())


# # 3679,1030 LO: glmSeriesId (hashage du SerieInstanceUID [0x0020, 0x000E])
# try: glmSeriesId = ds_dicom[0x0020, 0x000E].value.encode()
# except: glmSeriesId = str(randint(0, 99999999)).encode()
# ds_dicom.add_new([0x3679, 0x1030], "LO", hashlib.sha256(glmSeriesId).hexdigest())

# # 3679,1040 LO: glmInstanceId (hashage du SOPInstanceUID [0x0008, 0x0018])
# try :glmInstanceId = ds_dicom[0x0008, 0x0018].value.encode()
# except: glmInstanceId = str(randint(0, 99999999)).encode()
# ds_dicom.add_new([0x3679, 0x1040], "LO", hashlib.sha256(glmInstanceId).hexdigest())








# Set the transfer syntax
ds_dicom.is_little_endian = True
ds_dicom.is_implicit_VR = False

# Set creation date/time
dt = datetime.datetime.now()
ds_dicom.ContentDate = dt.strftime('%Y%m%d')
timeStr = dt.strftime('%H%M%S.%f')  # long format with micro seconds
ds_dicom.ContentTime = timeStr

print("Writing test file", path_to_save)
ds_dicom.save_as(path_to_save)
print("File saved.")


ds_dicom = dcmread(path_to_save)
print(ds_dicom)