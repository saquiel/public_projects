#! /usr/bin/env python3
# coding = utf-8



import pydicom
from pydicom import dcmread



path_to_rx = "/home/zenbook/Documents/code/python/dicom/data/anonymized/1H7FUSZ9TEBCW.dcm"
path_to_mri = "/home/zenbook/Documents/code/python/dicom/data/MRI_ADNI4/002_S_0413/Axial_3TE_T2_STAR/2019-08-27_09_39_37.0/S868724/ADNI_002_S_0413_MR_Axial_3TE_T2_STAR__br_raw_20190828115108611_52_S868724_I1221049.dcm"
path_to_ct = "/home/zenbook/Documents/code/python/dicom/data/cancer_dicom/ID_0084_AGE_0067_CONTRAST_0_CT.dcm"

ds = dcmread(path_to_rx)
ds = dcmread(path_to_mri)
ds = dcmread(path_to_ct)

list_modality = ['DX','CR']

def modality_filter(ds, list_modality):
    if ds.Modality not in list_modality:
        print(f"Modality: {ds.Modality}")
    else:
        print("a radio")

modality_filter(ds, list_modality)