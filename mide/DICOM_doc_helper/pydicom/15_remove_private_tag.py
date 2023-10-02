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

input_folder = "/home/zenbook/Documents/code/python/dicom/data/all_kind/IMPF"

list_path = path_to_dicom(input_folder)

path_to_save = "/home/zenbook/Documents/code/python/dicom/output"

for path in list_path:


    file_name = os.path.basename(path)
    save_path = path_to_save + "/" + file_name.split(".")[0] + ".dcm"


    data_set = dcmread(path)
    print(data_set)
    data_set.remove_private_tags()
    data_set.save_as(save_path, write_like_original=False)

    # try:
    #     print(data_set[0x3679, 0x1000])
    # except:
    #     pass
    # # print(data_set[0x3679, 0x1010])
    # # print(data_set[0x3679, 0x1020])
    # # print(data_set[0x3679, 0x1030])
    # # print(data_set[0x3679, 0x1040])
    # # print(data_set[0x3679, 0x1050])
    # # print(data_set[0x3679, 0x1060])
    # # print(data_set[0x3679, 0x1070])
