#! /usr/bin/env python3
# coding = utf-8


from cgi import test
from doctest import Example
from optparse import Values
from turtle import width
import pytest
from pynetdicom.sop_class import CTImageStorage
from anonymization import *
from python.mide.main import *
import pandas as pd

import numpy
from multiprocessing import Process, Queue
import time
import hashlib
import pathlib


from pydicom.dataset import Dataset

from pynetdicom import AE, evt
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind, StudyRootQueryRetrieveInformationModelFind



from pydicom.dataset import Dataset

from pynetdicom import AE, evt, debug_logger
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind, StudyRootQueryRetrieveInformationModelFind
import time
# debug_logger()

#! /usr/bin/env python3
# coding = utf-8

import os

from pydicom import dcmread
from pydicom.dataset import Dataset
from pynetdicom import AE, StoragePresentationContexts, evt, debug_logger
import time


# debug_logger()


import difflib


from PIL import Image

import imageio





path_dicom = "data_test/test_dx.dcm"
ds_test_dx = dcmread(path_dicom)

path_to_json = "extractor.json"
client_id = "unit_test"
path_white_list = "dicom_white_list.csv"
path_to_dicom_csv = "pacs_list/dicom_imported_an_x3.csv"
debug = False
path_to_json = "extractor.json"

test_exam = medical_exam(client_id, path_to_json, path_white_list, path_to_dicom_csv, debug)

test_exam.ds_dicom = ds_test_dx

test_exam.report_link_id = "test.456.789"

test_exam.study_uid_number = 1

test_exam.dicom_number = 9

test_exam.store_on_cloud()

assert test_exam.status != "cloud_storage_faillure"

