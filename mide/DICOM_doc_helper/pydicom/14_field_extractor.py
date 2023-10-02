#! /usr/bin/env python3
# coding = utf-8


from pydicom import dcmread,datadict
import os
import json
import pandas as pd

def path_to_dicom(path_to_folder):
    '''Find all dicom file and return their path
        input:  folder to search
        output: list of dicom file path'''
    list_path = []
    for dirpath, dirs, files in os.walk(path_to_folder):  
        for filename in files:
            path_to_file = os.path.join(dirpath,filename)
            if path_to_file.endswith(".dcm"):
                list_path.append(path_to_file)
    return(list_path)

input_folder = "/home/zenbook/Documents/code/python/dicom/data/all_kind"

list_path = path_to_dicom(input_folder)

df_dicom_tag = pd.DataFrame(columns=["tag", "tag_name","left_addr", "right_addr"])
list_path = path_to_dicom("/home/zenbook/Documents/code/python/dicom/data/all_kind")
# list_path = ["/home/zenbook/Documents/code/python/dicom/data/all_kind"]

for path in list_path:
    print(path)
    data_set = dcmread(path)

    json_data_set = data_set.to_json()
    dict_data_set = json.loads(json_data_set)
    list_addr_dicom = list(dict_data_set.keys())


    try:
        print(data_set[0x3679, 0x1000])
    except:
        pass
    # print(data_set[0x3679, 0x1010])
    # print(data_set[0x3679, 0x1020])
    # print(data_set[0x3679, 0x1030])
    # print(data_set[0x3679, 0x1040])
    # print(data_set[0x3679, 0x1050])
    # print(data_set[0x3679, 0x1060])
    # print(data_set[0x3679, 0x1070])


    for addr in list_addr_dicom:

        dict_tag_tmp = dict()
        dict_tag_tmp["tag"] = addr
        left_addr = addr[0:4]
        left_addr = int(left_addr, 16)
        right_addr = addr[4:]
        right_addr = int(right_addr, 16)

        addr_tuple = data_set[left_addr, right_addr].tag
        dict_tag_tmp["tag_tuple"] = addr_tuple

        try:
            tag_name = datadict.dictionary_keyword(addr_tuple)
        except:
            tag_name = "private_name"

        df_dicom_tag = df_dicom_tag.append({"tag":addr, "tag_name": tag_name ,"left_addr": left_addr, "right_addr": right_addr}, ignore_index=True)
    else:
        pass
        # 3679,1000 : exportVersion
        print()

df_dicom_tag.drop_duplicates(inplace=True)
df_dicom_tag["left_addr"] = df_dicom_tag["left_addr"].astype(int)
df_dicom_tag["right_addr"] = df_dicom_tag["right_addr"].astype(int)

df_dicom_tag.sort_values(by="tag", inplace = True)
print(df_dicom_tag)

df_dicom_tag.to_csv("/home/zenbook/Documents/code/python/dicom/pydicom/dicom_tag_extracted.csv", index = False)
