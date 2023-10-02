#! /usr/bin/env python3
# coding = utf-8

import os
import tempfile
import datetime

import pydicom
from pydicom import dcmread
from pydicom.dataset import Dataset, FileDataset, FileMetaDataset
import pandas as pd



path_to_dicom = "/home/zenbook/Documents/code/python/dicom/data/all_kind/1IUKCVPT8PPFK.dcm"

print("start")
ds = dcmread(path_to_dicom)


# SOPInstanceUID
ds.add_new([0x0008, 0x0018], "LO", "sop.instance.uid.123456789")
# 0008 0050,AccessionNumber SH
ds.add_new([0x0008, 0x0050], "SH", "AccessionNumber.123456789")
# 00080080,InstitutionName LO
ds.add_new([0x0008, 0x0080], "LO", "InstitutionName.123456789")
# 00080090,ReferringPhysicianName PN
ds.add_new([0x0008, 0x0090], "PN", "ReferringPhysicianName.123456789")
# 00081111,ReferencedPerformedProcedureStepSequence SQ
ds.add_new([0x0008, 0x1111], "SQ", [Dataset()])
# 00082112,SourceImageSequence SQ
ds.add_new([0x0008, 0x2112], "SQ", [Dataset()])
# 00100010,PatientName PN
ds.add_new([0x0010, 0x0010], "PN", "PatientName")
# 00100020,PatientID LO
ds.add_new([0x0010, 0x0020], "LO", "PatientID.123456789")
# (0x0010,0x0021) Issuer of Patient ID LO
ds.add_new([0x0010, 0x0020], "LO", "IssuerOfPatientID.123456789")

# (0x0010,0x0022) Type of Patient ID CS
ds.add_new([0x0010, 0x0022], "CS", "123456789")
# (0x0010,0x0024) Issuer of Patient ID Qualifiers Sequence SQ
ds.add_new([0x0010,0x0024], "SQ", [Dataset()])
# (0x0010,0x0033) Patient's Birth Date in Alternative Calendar LO
ds.add_new([0x0010,0x0033], "LO", "PatientBirthDateAlternativeCalendar")
# (0x0010,0x0034) Patient's Death Date in Alternative Calendar LO
ds.add_new([0x0010,0x0034], "LO", "PatientBirthDateAlternativeCalendar")
# (0x0010,0x0035) Patient's Alternative Calendar CS
ds.add_new([0x0010,0x0035], "CS", "123456789")
# (0x0010,0x1001) Other Patient Names PN
ds.add_new([0x0010,0x1001], "PN", "OtherPatientNames")
# (0x0010,0x1002) Other Patient IDs Sequence SQ
ds.add_new([0x0010,0x1002], "SQ", [Dataset()])

# (0010,1010) Patient's Age AS
ds.add_new([0x0010, 0x1010], "AS", "99")

# (0x0010,0x1100) Referenced Patient Photo Sequence SQ
ds.add_new([0x0010,0x1100], "SQ", [Dataset()])
# (0x0010,0x2297) Responsible Person Attribute PN
ds.add_new([0x0010,0x2297], "PN", "ResponsiblePersonAttribute")
# (0x0010,0x4000) Patient Comments Attribute LT
ds.add_new([0x0010,0x4000], "LT", "PatientComments")
# (0x0008,0x0096) Referring Physician Identification Sequence SQ
ds.add_new([0x0008,0x0096], "SQ", [Dataset()])
# (0x0008,0x009C) Consulting Physician's Name PN
ds.add_new([0x0008,0x009C], "PN", "ConsultingPhysicianName")
# (0x0008,0x1048) Physician(s) of Record PN
ds.add_new([0x0008,0x1048], "PN", "PhysicianOfRecord")
# (0x0008,0x1049) Physician(s) of Record Identification Sequence SQ
ds.add_new([0x0008,0x1049], "SQ", [Dataset()])
# (0x0008,0x1060) Name of Physician(s) Reading Study PN
ds.add_new([0x0008,0x1060], "PN", "PhysicianOfRecord")
# (0x0008,0x1062) Physician(s) Reading Study Identification Sequence SQ
ds.add_new([0x0008,0x1062], "SQ", [Dataset()])
# (0x0008,0x009C) Consulting Physician's Name PN
ds.add_new([0x0008,0x009C], "PN", "ConsultingPhysicianName")
# (0x0008,0x1052) Performing Physician Identification Sequence SQ
ds.add_new([0x0008,0x1052], "SQ", [Dataset()])
# (0x0008,0x1070) Operators' Name PN
ds.add_new([0x0008,0x1070], "PN", "OperatorsName")
# (0x0008,0x1072) Operator Identification Sequence SQ
ds.add_new([0x0008,0x1072], "SQ", [Dataset()])



# 00100030,PatientBirthDate DA
ds.add_new([0x0010, 0x0030], "DA", "20210221")
# 0020000D,StudyInstanceUID LO
ds.add_new([0x0020, 0x000D], "LO", "study.instance.uid.123456789")
# 0020000E,SeriesInstanceUID LO
ds.add_new([0x0020, 0x000E], "LO", "series.instance.uid.123456789")
# 00200010,StudyID SH
ds.add_new([0x0020, 0x0010], "SH", "AccessionNumber.123456789")
# 00200011,SeriesNumber IS
ds.add_new([0x0020, 0x0011], "IS", 1)
# 00200013,InstanceNumber IS
ds.add_new([0x0020, 0x0013], "IS", 1)
# 00321032,RequestingPhysician LO
ds.add_new([0x0032, 0x1032], "LO", "RequestingPhysician.123456789")
# 00321033,RequestingService LO
ds.add_new([0x0032, 0x1032], "LO", "RequestingService.123456789")

# # Private tags
# # 00080000,private_name LO
# ds.add_new([0x0008, 0x0000], "LO", "private_name.123456789")
# # 00100000,private_name LO
# ds.add_new([0x0010, 0x0000], "LO", "private_name.123456789")
# # 00180000,private_name LO
# ds.add_new([0x0018, 0x0000], "LO", "private_name.123456789")
# # 00200000,private_name LO
# ds.add_new([0x0020, 0x0000], "LO", "private_name.123456789")
# # 00280000,private_name LO
# ds.add_new([0x0028, 0x0000], "LO", "private_name.123456789")
# # 00320000,private_name LO
# ds.add_new([0x0032, 0x0000], "LO", "private_name.123456789")
# # 00400000,private_name LO
# ds.add_new([0x0040, 0x0000], "LO", "private_name.123456789")


save_path = "/home/zenbook/Documents/code/python/dicom/pydicom/tag_test.dcm"
ds.is_implicit_VR = False
ds.save_as(save_path, write_like_original=False)

print(f"DICOM created: {save_path} ")
