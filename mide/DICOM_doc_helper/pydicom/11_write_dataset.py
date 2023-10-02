#! /usr/bin/env python3
# coding = utf-8


from pydicom import dcmread
import hashlib

# A/ open a DICOM file
# get the path to the test file
# fpath = get_testdata_file("CT_small.dcm")

fpath = "/home/zenbook/Documents/code/python/dicom/data/multi_incidence/1IUPYRWDP28E8-res.dcm"
# read the DICOM dataset
data_set = dcmread(fpath)


# 3679,1000 : exportVersion
data_set.add_new([0x3679, 0x1000], "exportVersion",2.0)
print(f"exportVersion: {data_set[0x3679, 0x1000].value} ")

# 3679,1010 : glmPatientId => hashage du PatientId (0010,0020)
print(f"Patient ID: {data_set[0x0010, 0x0020].value}")
value = data_set[0x0010, 0x0020].value

hashed = hashlib.sha256(value.encode()).hexdigest()
data_set.add_new([0x3679, 0x1010], "glmPatientId",hashed)
print(f"glmPatientID: {data_set[0x3679, 0x1010].value} ")

# 3679,1020 : glmStudyId => hashage du StudyInstanceUID (0020,000D)
print(f"Study Instance UID: {data_set[0x0020, 0x000D].value}")
value = data_set[0x0010, 0x0020].value

hashed = hashlib.sha256(value.encode()).hexdigest()
data_set.add_new([0x3679, 0x1020], "glmStudyId",hashed)
print(f"glmStudyId: {data_set[0x3679, 0x1020].value} ")

# 3679,1030 : glmSeriesId => hashage du SerieInstanceUID (0020,000E)
print(f"Serie Instance UID: {data_set[0x0020, 0x000E].value}")
value = data_set[0x0020, 0x000E].value

hashed = hashlib.sha256(value.encode()).hexdigest()
data_set.add_new([0x3679, 0x1030], "glmSeriesID",hashed)
print(f"glmSeriesID: {data_set[0x3679, 0x1030].value} ")

# 3679,1040 : glmInstanceId => hashage du SOPInstanceUID (0008,0018)
print(f"SOPInstanceUID: {data_set[0x0008, 0x0018].value}")
value = data_set[0x0008, 0x0018].value

hashed = hashlib.sha256(value.encode()).hexdigest()
data_set.add_new([0x3679, 0x1040], "glmInstanceId",hashed)
print(f"glmInstanceId: {data_set[0x3679, 0x1040].value} ")

# 3679,1050 : exportBatchCode (nom du batch)
batch = "batch2"
data_set.add_new([0x3679, 0x1050], "exportBatchCode",batch)
print(f"exportBatchCode: {data_set[0x3679, 0x1040].value} ")

# 3679,1060 : clientId (nom du partenaire)
batch = "batch2"
data_set.add_new([0x3679, 0x1060], "clientId",batch)
print(f"exportBatchCode: {data_set[0x3679, 0x1060].value} ")

# 3679,1070 : date de l'export
date = "20200519"
data_set.add_new([0x3679, 0x1070], "clientId",date)
print(f"date: {data_set[0x3679, 0x1070].value} ")



    

