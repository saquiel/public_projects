#! /usr/bin/env python3
# coding = utf-8


# anonymize dicom tag

# run:
# python script_dicom_anonymization


from pydicom import dcmread,datadict
import os
import json
import pandas as pd
import hashlib
from datetime import date



def CsvToPandas (path_to_csv, input_col):
    ''' load csv to a pandas data frame:
        input:  path to csv file
                column to extract
        output: pandas data frame'''
    try:
        output_df = pd.read_csv(path_to_csv, usecols=input_col)
    except FileNotFoundError:
        return print("file not found, input the path to the csv file")
    return output_df


path_to_white_list = "/home/zenbook/Documents/code/python/dicom/pydicom/dicom_tag_extracted.csv"
# path to dicom
path = "/home/zenbook/Documents/Gleamer/glm-export-data/raw_data/data/pacs/IM2P_OTHER/1HBAHK224VAPS.dcm"

# variables
batch_name = "batch_123"
client_id = "CLIENT01"

# read the DICOM dataset
df_white_list = CsvToPandas(path_to_white_list, ["tag","left_addr","right_addr"])

list_white = df_white_list["tag"].to_list()

data_set = dcmread(path)


json_data_set = data_set.to_json()
dict_data_set = json.loads(json_data_set)
list_addr_dicom = list(dict_data_set.keys())

# 0008,0020 age
# IF not age or empty, create from birthday


# write DICOM tag
# 3679,1000 US: exportVersion
data_set.add_new([0x3679, 0x1000], "US", "3")
print(data_set[0x3679, 0x1000])

# 3679,1050 LO: exportBatchCode (nom du batch)
data_set.add_new([0x3679, 0x1050], "LO", batch_name)
print(data_set[0x3679, 0x1050])

# 3679,1060 LO: clientId (nom du partenaire)
data_set.add_new([0x3679, 0x1060], "LO", client_id)
print(data_set[0x3679, 0x1060])

# 3679,1070 DA: '20190910': date de l'export
today = date.today().strftime("%Y%m%d")
data_set.add_new([0x3679, 0x1070], "DA", today)
print(data_set[0x3679, 0x1070])


# write hash DICOM values on Gleamer private tag

# 3679,1010 LO: glmPatientId (hashage du PatientId [0x0010, 0x0020])
glmPatientId = data_set[0x0010, 0x0020].value.encode()
data_set.add_new([0x3679, 0x1010], "LO", hashlib.sha256(glmPatientId).hexdigest())
print(data_set[0x3679, 0x1010])

# 3679,1020 LO: glmStudyId (hashage du StudyInstanceUID [0x0020, 0x000D])
glmPatientId = data_set[0x0010, 0x0020].value.encode()
data_set.add_new([0x3679, 0x1020], "LO", hashlib.sha256(glmPatientId).hexdigest())
print(data_set[0x3679, 0x1020])

# 3679,1030 LO: glmSeriesId (hashage du SerieInstanceUID [0x0020, 0x000E])
glmPatientId = data_set[0x0020, 0x000E].value.encode()
data_set.add_new([0x3679, 0x1030], "LO", hashlib.sha256(glmPatientId).hexdigest())
print(data_set[0x3679, 0x1030])

# 3679,1040 LO: glmInstanceId (hashage du SOPInstanceUID [0x0008, 0x0018])
glmPatientId = data_set[0x0008, 0x0018].value.encode()
data_set.add_new([0x3679, 0x1040], "LO", hashlib.sha256(glmPatientId).hexdigest())
print(data_set[0x3679, 0x1040])



for addr in list_addr_dicom:
    # delete DICOM tag that are not in the white list
    if  addr not in list_white:
        del data_set[addr]


# black_list for test
# list_to_del = [ (0x0010,0x0010),(0x0010,0x0020),(0x0010,0x0021),
#                 (0x0010,0x0022),(0x0010,0x0024),(0x0010,0x0030),
#                 (0x0010,0x0033),(0x0010,0x0034),(0x0010,0x0035),
#                 (0x0010,0x1001),(0x0010,0x1002),(0x0010,0x1100),
#                 (0x0010,0x2297),(0x0010,0x4000),(0x0008,0x0050),
#                 (0x0008,0x0090),(0x0008,0x0096),(0x0008,0x009C),
#                 (0x0008,0x1048),(0x0008,0x1049),(0x0008,0x1060),
#                 (0x0008,0x1062),(0x0008,0x1050),(0x0008,0x1052),
#                 (0x0008,0x1070),(0x0008,0x1072),(0x0008,0x1070)]


# (0x0010,0x0010) Patient's Name Attribute
# (0x0010,0x0020) Patient ID Attribute
# (0x0010,0x0021) Issuer of Patient ID Attribute
# (0x0010,0x0022) Type of Patient ID Attribute
# (0x0010,0x0024) Issuer of Patient ID Qualifiers Sequence Attribute
# (0x0010,0x0030) Patient's Birth Date Attribute
# (0x0010,0x0033) Patient's Birth Date in Alternative Calendar Attribute
# (0x0010,0x0034) Patient's Death Date in Alternative Calendar Attribute
# (0x0010,0x0035) Patient's Alternative Calendar Attribute
# (0x0010,0x1001) Other Patient Names Attribute
# (0x0010,0x1002) Other Patient IDs Sequence Attribute
# (0x0010,0x1100) Referenced Patient Photo Sequence Attribute
# (0x0010,0x2297) Responsible Person Attribute
# (0x0010,0x4000) Patient Comments Attribute
# (0x0008,0x0050) Accession Number Attribute
# (0x0008,0x0090) Referring Physician's Name Attribute
# (0x0008,0x0096) Referring Physician Identification Sequence Attribute
# (0x0008,0x009C) Consulting Physician's Name Attribute
# (0x0008,0x1048) Physician(s) of Record Attribute
# (0x0008,0x1049) Physician(s) of Record Identification Sequence Attribute
# (0x0008,0x1060) Name of Physician(s) Reading Study Attribute
# (0x0008,0x1062) Physician(s) Reading Study Identification Sequence Attribute
# (0x0008,0x1050) Performing Physician's Name Attribute
# (0x0008,0x1052) Performing Physician Identification Sequence Attribute
# (0x0008,0x1070) Operators' Name Attribute
# (0x0008,0x1072) Operator Identification Sequence Attribute
