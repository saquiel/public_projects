#! /usr/bin/env python3
# coding = utf-8

# label to modify
# 3679,1000 : exportVersion
# 3679,1010 : glmPatientId (hashage du PatientId)
# 3679,1020 : glmStudyId (hashage du StudyInstanceUID)
# 3679,1030 : glmSeriesId (hashage du SerieInstanceUID)
# 3679,1040 : glmInstanceId (hashage du SOPInstanceUID)
# 3679,1050 : exportBatchCode (nom du batch)
# 3679,1060 : clientId (nom du partenaire)
# 3679,1070 : date de l'export

# Change directory to local extractor.py directory
# python extractor.py path-to-list_dicom.csv client_id
# example:
# python extractor.py dicom_imported_scaner.csv pacs_orthanc


from hashlib import new
import os
import sys
from pydicom.dataset import Dataset
from pynetdicom import AE, evt, StoragePresentationContexts, debug_logger, AllStoragePresentationContexts, ALL_TRANSFER_SYNTAXES
from pydicom.filewriter import write_file_meta_info
import json
import pandas as pd
import psutil
import subprocess
import multiprocessing
import numpy as np
from anonymization import main_anonymization
from pydicom import dcmread
from package.dicom import read_dicom_with_pydicom
import datetime
import time
import platform
import pathlib
from pydicom.dataset import FileDataset, FileMetaDataset
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind
from schedule import every, repeat, run_pending, run_all
from random import randint
from datetime import datetime as dt
import hashlib
# TEST
# debug_logger()


def initialization_json(path_to_json, client_id):
    """
    Initialise extractor with a json
    input:  json
    output: aet_title, aet_port, aec_title, aec_ip, aec_port, output_folder, modality, delay
    """
    with open(path_to_json, "r") as tmp_file:
        dict_init = json.load(tmp_file)

    # AE name encoded in bytes ascii
    aet_title = dict_init[client_id]["aet_title"].encode('ascii')
    aet_ip = dict_init[client_id]["aet_ip"]
    aet_port = dict_init[client_id]["aet_port"]
    aec_title = dict_init[client_id]["aec_title"].encode('ascii')
    aec_ip = dict_init[client_id]["aec_ip"]
    aec_port = dict_init[client_id]["aec_port"]
    output_folder = dict_init[client_id]["output_folder"]
    modality = dict_init[client_id]["modality"]
    image_modality_anonymisation = dict_init[client_id]["image_modality_anonymisation"]
    delay = dict_init[client_id]["delay"]



    return aet_title, aet_ip, aet_port, aec_title, aec_ip, aec_port, output_folder, modality, image_modality_anonymisation, delay


def CsvToPandas(path_to_csv, input_col):
    ''' load csv to a pandas data frame:
        input:  path to csv file
                column to extract
        output: pandas data frame'''
    try:
        output_df = pd.read_csv(path_to_csv, dtype=str, usecols=input_col)
    except FileNotFoundError:
        print("file not found, input the path to the csv file")
        sys.exit(1)
        
    return output_df


def random_date():
# Change for a year date
    """Compute a randomized date
    output: random date YYMMDD"""

    year = randint(2001,2021)
    month = randint(1,12)
    day = randint(1,28)
    random_date =  dt(year, month, day).strftime('%Y%m%d')

    return random_date

# TODO study_date_deidentification
def study_date_deidentification(input_study_date):
    """Study date deidentification by reducing precision to with month + year
    input:  input_study_date
    output: deid_study_date (YYYYMM)"""

    # Check for study date conformance
    if not (isinstance(input_study_date, str)):
        study_date_deid = "00000000"
    elif not(len(input_study_date) == 8):
        study_date_deid = "00000000"
    else:
        day = int(input_study_date[-2:])
        week = (day // 8) + 1
        study_date_deid = input_study_date[:-2] + "W" + str(week)

    return study_date_deid


def glm_study_date(ds_dicom, df_log):
    # change for study date de-identification. Precision reduce to with month + year
    """Filter DICOM:
    No glm_study_id + no glm_instance_uid in DICOM => flag_pass = 0 (new date)
    Same glm_study_id + same glm_instance_uid => 1 (pass)
    Same glm_study_id + !=glm_instance_uid => same report_date

    Actually, only use for Chn
    """

    report_date = 0
    encoded = ds_dicom[0x0020, 0x000D].value.encode()
    glm_study_id = hashlib.sha256(encoded).hexdigest()

    encoded = ds_dicom[0x0008, 0x0018].value.encode()
    glm_instance_id = hashlib.sha256(encoded).hexdigest()


    # IF glm_study_id not in log => new DICOM => flag_pass = 0 (new date)
    if len(df_log.loc[df_log["glm_study_id"] == glm_study_id]) == 0:
        report_date = random_date()
        flag_pass = 0
        return report_date, flag_pass

    # IF glm_study_id in log + glm_instance_uid not in log => DICOM in same study => flag_pass = 0 (same_date)
    else:
        if len(df_log.loc[df_log["glm_instance_id"] == glm_instance_id]) == 0:
            report_date = df_log.loc[df_log["glm_study_id"] == glm_study_id]["report_date"].values[0]
            flag_pass = 0
            return report_date, flag_pass
        # IF glm_study_id in log + glm_instance_uid in log => already processed => flag_pass = 1
        else:
            report_date = df_log.loc[df_log["glm_study_id"] == glm_study_id]["report_date"].values[0]
            flag_pass = 1
            return str(report_date), flag_pass

# TODO remove
def df_formater(df_dicom_to_extract, client_id, debug_mode):
    """format input df to fit exporter process
        Sorted by priority
        IF no AN => exit
        IF debug_mode => double AN won't be removed
        input:  dataframe
                client name
                flag debug_mode
        output: dataframe formated"""

    # NEED to remove all the useless columns
    df_dicom_to_extract["client"] = client_id
    df_dicom_to_extract.rename(columns={"prio": "priority", "date": "report_date", "accessionNumber":"accession_number"}, inplace=True)
    df_dicom_to_extract["query_level"] = "STUDY"
    df_dicom_to_extract["status"] = np.nan
    df_dicom_to_extract["dicom_name"] = np.nan # useless ?
    df_dicom_to_extract["ram_load"] = np.nan
    df_dicom_to_extract["cpu_load"] = np.nan
    df_dicom_to_extract["cpu_temp"] = np.nan
    df_dicom_to_extract["disk_load"] = np.nan
    df_dicom_to_extract["timer_process"] = np.nan
    df_dicom_to_extract["timer_query"] = np.nan
    df_dicom_to_extract["date"] = np.nan
    df_dicom_to_extract.sort_values(by=['priority'], inplace=True)
    df_dicom_to_extract["accession_number"] = df_dicom_to_extract["accession_number"].astype(str)
    df_dicom_to_extract['accession_number'].replace('nan', np.NaN, inplace=True)

    # IF no accesion_number => quit
    if pd.isna(df_dicom_to_extract.iloc[0].loc["accession_number"]):
        print(f"Can't proccess without accession_number in the csv file ")
        sys.exit(1)

    if debug_mode == False:
        df_dicom_to_extract.drop_duplicates(subset=["accession_number"], keep='first', inplace=True)

    return df_dicom_to_extract

# TODO remove
def hdd_save_health_check(list_path_to_folder):
    """
    select the drive to save
    """
    # TODO HDD health check
    # send status if HDD full
    file_to_save = list_path_to_folder[0]

    return file_to_save

#  TODO remove
def storage_check(output_folder):
    """Verify that the path to the output folder is a directory
    input:  path to the folder
    output: service_status
            0x0000: ok
            0xC003: Unable to reach the storage directory
    """
    if not os.path.isdir(os.path.normpath(output_folder)):
        return 0xC003
    else:
        return 0x0000

# Change for log file initialization
def file_initialization(csv_log):
    """"
    Create needed file :
        tmp_dicom folder
        anonymization_result.csv
        exporter_log.csv
    """

    # IF tmp_dicom folder don't exist not exist, create it
    if not os.path.isdir(os.path.normpath("tmp_dicom")):
        print("tmp_dicom folder don't exist, created it")
        os.mkdir("tmp_dicom")
    print("tmp_dicom folder => OK")

    # IF anonymization_result.csv not exist, create it
    if not os.path.exists(os.path.normpath("anonymization_result.csv")):
        print("anonymization_result.csv don't exist, will be created")
        df_anonym_tracker = pd.DataFrame(
            columns=["file_name", "blanked_word", "passed_word"])
        df_anonym_tracker.set_index("file_name", inplace=True)
        df_anonym_tracker.to_csv("anonymization_result.csv", header=True)
    print("Anonymization_result => OK")


    if not os.path.exists(os.path.normpath(csv_log)):
        print(f"{csv_log} don't exist, created it")
        df_exporter_log = pd.DataFrame(columns=["client", "priority", "batch", "report_date", "query_level", "accession_number", "study_instance_uid", "glm_study_id",
                            "glm_instance_id", "ram_load","cpu_load","cpu_temp","disk_load","timer_process","timer_query", "status" ,"date_export"])
        df_exporter_log.to_csv(csv_log, header=True, index=False)                    
    print(f"{csv_log} => OK")

    return 0

# TODO remove
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



# -----Query functions-----

def c_find_query_study_uid(aet_title, aec_title, aec_ip, aec_port, accession_number):
    """Query the PACS with C-FIND with an AccessionNumber to get StudyInstanceUID associated
        input:  AccessionNumber
                network connexion parameters
        output: list of study_instance_uid
                status of C-FIND query"""

    ae = AE(ae_title=aet_title)

    # Presentation abstract context initialization
    ae.add_requested_context('1.2.840.10008.5.1.4.1.2.1.1')

    ds = Dataset()
    # Add query retrieve level
    ds.QueryRetrieveLevel = 'STUDY'
    ds.AccessionNumber=accession_number

    ds.StudyInstanceUID = "" #return Study UID

    assoc = ae.associate(aec_ip, aec_port, ae_title=aec_title)

    study_instance_uid = []
    if assoc.is_established:
        # Send the C-FIND request
        responses = assoc.send_c_find(ds, PatientRootQueryRetrieveInformationModelFind)
        for (status, identifier) in responses:
            if status:
                print(f"C-FIND query status: {status.Status}")
                try:
                    study_instance_uid.append(str(identifier[0x0020, 0x000d].value))
                    c_find_status = "c_find_ok"
                    assoc.release()
                    return study_instance_uid, c_find_status
                except:
                    c_find_status = "c_find_no_study_uid"

            else:
                c_find_status = "c_fing_invalid_response"

        assoc.release()
        return study_instance_uid, c_find_status
    else:
        c_find_status = "c_find_association_fail"
    
    return study_instance_uid, c_find_status
    

def query_builder(ser_log):
    """build the dicom query from the last df_log row
        input:  pandas series to query
        output: Pynetdicom query object"""

    query_level = ser_log["query_level"]
    study_instance_uid = ser_log["study_instance_uid"]
    query_key_type = "StudyInstanceUID"

    # Create out identifier (query) dataset
    ds_query = Dataset()
    # Add query retrieve level
    ds_query.QueryRetrieveLevel = query_level
    # set query key to the query attribute
    setattr(ds_query, query_key_type, study_instance_uid)

    return ds_query


# TODO: Save in ram
def handle_store(event):
    """Handle EVT_C_STORE events
    input:  trigger by evt.EVT_C_STORE
            path to the storage directory
    output: write the receive dicom in the storage directory
            return a storage success status      
    """

    # We rely on the UID from the C-STORE request instead of decoding
    dicom_name = event.request.AffectedSOPInstanceUID

    # temp DICOM will be write on local drive (SSD)
    path_to_folder = "tmp_dicom"
    file_path = pathlib.Path.cwd().joinpath(path_to_folder, dicom_name+".dcm")

    # save the DICOM
    with open(file_path, 'wb') as tmp_file:
        # write 128 bits preamble header
        tmp_file.write(b'\x00' * 128)
        # write 4 bits DICOM prefix
        tmp_file.write(b'DICM')
        # write meta info about the SCU encoded file
        write_file_meta_info(tmp_file, event.file_meta)
        # write SCU encoded data set
        tmp_file.write(event.request.DataSet.getvalue())

    return 0x0000

# TODO search to avoid handler
def move_scu(aet_title, aet_port, aec_ip, aec_port, aec_title, ser_log):
    """
    DICOM MOVE_SCU service
        build and start a STORE_SCP service
        build and request a MOVE_SCU to the AEC
        STORE_SCP wait for the AEC response
        close the STORE_SCP service

    input:  aet_title, aet_port, aec_ip, aec_port, aec_title, ser_log
    output: Service _status:
        0xC001: Connection timed out, was aborted or received invalid response
        0xC002: Association rejected, aborted or never connected
    """

    # on event C-Store call handler
    handlers = [(evt.EVT_C_STORE, handle_store)]

    # Initialise the Application Entity
    ae = AE()
    ae.ae_title = aet_title

    # Study Root Query/Retrieve Information Model – MOVE SOP UID
    sop_uid = "1.2.840.10008.5.1.4.1.2.1.2"
    # Add a requested presentation context
    ae.add_requested_context(sop_uid)

    # support both compressed and uncompressed transfer syntaxes:
    # separate out the abstract syntaxes then use add_supported_context() with ALL_TRANSFER_SYNTAXES instead
    storage_sop_classes = [
        cx.abstract_syntax for cx in AllStoragePresentationContexts]
    for uid in storage_sop_classes:
        ae.add_supported_context(uid, ALL_TRANSFER_SYNTAXES)

    # Start our Storage SCP in non-blocking mode, listening on port 11120
    scp = ae.start_server(("", aet_port), block=False, evt_handlers=handlers)

    # Associate with peer AE IP and port
    assoc = ae.associate(aec_ip, aec_port, ae_title=aec_title)

    if assoc.is_established:
        # Use the C-MOVE service to send the identifier
        ds_query = query_builder(ser_log)
        responses = assoc.send_c_move(ds_query, aet_title, sop_uid)

        for (status, identifier) in responses:
            if status:
                service_status = status.Status
            else:
                service_status = 0xC002

        # Release the association
        assoc.release()
    else:
        # Association rejected, aborted or never connected
        service_status = 0xC003

    # Stop our Storage SCP
    scp.shutdown()


    return service_status


# TODO add this after receiving the DICOM
# Split: dicom_corrupted_filter, dicom_modality_filter, dicom_repport_filter
def dicom_filter(ds_dicom, flag_dicom, list_modality):
    """
    analyse DICOM in tmp_dicom folder and kill unacceptable ones:
        check for corrumpted (can open pixel array parameter)
        check unnecessary modality
        check for report 
    input:  DICOM dataframe
            list of wanted modality
            dict of DICOM flag
    output: dict of DICOM flag (updated)
    """

    # Check for corrupted DICOM
    try:
        ds_dicom.pixel_array 
    except:
        # corrupted_dicom += 1
        # kill the corrumpted DICOM
        flag_dicom["corrupted"] += 1
        return flag_dicom

    # Check for modality
    if ds_dicom.Modality not in list_modality:
        flag_dicom["wrong_modality"] += 1
        return flag_dicom
    
    if ds_dicom.BodyPartExamined == "REPORT":
        flag_dicom["wrong_modality"] += 1
        return flag_dicom

    flag_dicom["ok"] += 1
    
    return flag_dicom


# TODO remove
def folder_tree_builder(output_folder, batch_name, date_folder, glm_study_id, glm_instance_id):
    """If folder tree not exist, create it
    input:  folders where to save the DICOM
            batch_name
            date_folder
            glm_study_id
            glm_instance_id
    output: path to the DICOM file"""



    path_to_batch = os.path.join(output_folder, batch_name)
    # IF batch folder not exist, create it
    if not os.path.isdir(os.path.normpath(path_to_batch)):
        os.mkdir(path_to_batch)

    path_to_date = os.path.join(path_to_batch, date_folder)
    # IF date folder not exist, create it
    if not os.path.isdir(os.path.normpath(path_to_date)):
        os.mkdir(path_to_date)

    # IF DICOM study folder not exist, create it
    path_to_dicom_study = os.path.join(path_to_date, glm_study_id)
    if not os.path.isdir(os.path.normpath(path_to_dicom_study)):
        os.mkdir(path_to_dicom_study)

    path_to_dicom = os.path.join(path_to_dicom_study, glm_instance_id + ".dcm")

    return path_to_dicom


# TODO rename network_verification
def network_check(aet_title, aec_ip, aec_port, aec_title):
    """Detect NIC, PACS, Internet dysfonctionment
    input:  PACS address
    output: df_log updated with status
    """

    # check network system status (need 4-6 secondes)
    network_status = "network_ok"
    # test network interface card status
    # auto check for linux, windows and mac
    local_host = "127.0.0.1"
    google = "8.8.8.8"
    if os.system("ping " + ("-n 1 " if platform.system().lower() == "windows" else "-c 1 ") + local_host) != 0:
        print("Network faillure: nic_default")
        sys.exit(1)
    # test network connection with AEC PACS
    elif os.system("ping " + ("-n 1 " if platform.system().lower() == "windows" else "-c 1 ") + aec_ip) != 0:
        print("Network faillure: aec_unreachable")
        sys.exit(1)
    # check internet connectivity (google)
    elif os.system("ping " + ("-n 1 " if platform.system().lower() == "windows" else "-c 1 ") + google) != 0:
        print("Network faillure: internet_unreachable")
        sys.exit(1)
    # C-ECHO to AEC
    ae = AE(ae_title=aet_title)  # set AE title
    # Presentation abstract context initialization
    ae.add_requested_context('1.2.840.10008.1.1')
    assoc = ae.associate(aec_ip, aec_port, ae_title=aec_title)
    # if the association has been established
    if assoc.is_established:
        status = assoc.send_c_echo()
        if status.Status == 0:
            assoc.release()
            print("Network check => OK")
            return 0
        
        else:
            print("Network faillure: c_echo_faillure")
            sys.exit(1)
    else:
        # Association rejected, aborted or never connected
        print("Network faillure: no_aec_association")
        sys.exit(1)


# TODO remove
def health_check(ser_log, output_folder):
    """Check the hardware status of the server
    input:  pandas series log status
            save folder
    output: ser_log updated with status
    """

    # date dd/mm/YY H:M:S:
    now = datetime.datetime.now()
    ser_log.at["date"] = now.strftime("%Y-%m-%d %H:%M:%S")

    # check cpu load (last 15 min)
    load_per_cpu = psutil.getloadavg()[2]
    cpu_counter = multiprocessing.cpu_count()
    system_load = cpu_counter * load_per_cpu
    ser_log.at["cpu_load"] = 15

    # check RAM
    ram_load = psutil.virtual_memory().percent
    # ser_log.at["ram_load"] = ram_load
    ser_log.at["ram_load"] = ram_load

    # check HDD
    try:
        disk_load = psutil.disk_usage(output_folder)[3]
    # ser_log.at["disk_load"] = disk_load
        ser_log.at["disk_load"] = disk_load
    except:
        ser_log.at["disk_load"] = "no_load"

    # Can't get sensors_temp from windows
    if platform.system() == "Windows":
        ser_log.at["cpu_temp"] = 0
        return ser_log

    # FAIL with DELL server => TRY LATER
    # # check CPU temperature
    # temps = psutil.sensors_temperatures()
    # total_sensor_cpu = 0
    # n_sensor_cpu = 0
    # for entry in temps['coretemp']:
    #     total_sensor_cpu += entry.current
    #     n_sensor_cpu += 1

    # avg_cpu_temp = total_sensor_cpu / n_sensor_cpu
    # ser_log.at["cpu_temp"] = avg_cpu_temp
    ser_log.at["cpu_temp"] = 0

    return ser_log



def dicom_tag_filter(ds_dicom, df_white_list):
    """Delete unnecessay DICOM tags:
        input:  dicom file
        output: dicom file"""

    # add to white list
    # 0028,0006 Planar Configuration Attribute
    # 0020,4000 Image Comments Attribute
    # 0028,0301 Burn in anotation
    # 0020,0062 Image Laterality Attribute


    list_usefull_tags = df_white_list["tag"].to_list()

    list_usefull_tags += [  "00020000",# file meta
                            "00020010",# file meta
                            "00020012",# file meta
                            "00020013",# file meta
                            "00080008",# Image Type Attribute
                            "00080016",# SOP Class UID Attribute
                            "00080018",# SOP Instance UID Attribute
                            "00101010",# Patient's Age Attribute
                            "0020000D",# Study Instance UID Attribute
                            "0020000E",# Series Instance UID Attribute
                            "00200011",# Series Number Attribute
                            "00200013",# Instance Number Attribute
                            "00080050",# Accession Number Attribute 
                            "0020000D",# Study Instance UID Attribute
                            "00100030",# Patient's Birth Date Attribute 
                            "00100020" # Patient ID Attribute
                            ]



    # extract dicom tags
    list_tag_dicom = list(ds_dicom)
    list_addr_dicom = [str(addr.tag).replace(', ', '').replace(
            ')', '').replace('(', '').upper() for addr in list_tag_dicom]

    # delete unecessay DICOM tags 
    for addr in list_addr_dicom:
        if (addr) not in list_usefull_tags:
            del ds_dicom[addr]

    return ds_dicom


# TODO remove no image and wrong modality cond
def dicom_normalization(input_dicom, file_path, list_modality):
    """
    Normalize DICOM: uncompress and set transfert syntax to little endian
    input:  file path to dicom
    """
    ds = input_dicom
    flag = 0
    # ds = dcmread(file_path)

    # IF no image, break
    try:
        tmp = ds.pixel_array.tobytes()
    except:
        flag = 1
        return ds, flag

    # IF wrong modality, break
    if ds.Modality not in list_modality:
        print("normalization: bad modality")
        flag = 1
        return ds, flag


    # IF dicom file is normalized: exit
    # if ds.file_meta.TransferSyntaxUID == "1.2.840.10008.1.2": # if little endian and uncompressed => do nothing
    if ds.file_meta.TransferSyntaxUID == "1.2.840.10008.1.2.1": # if little endian and uncompressed and explicite => do nothing
        return ds, flag


    # normalize DICOM file
    ds = dcmread(file_path)
    dicom_path = file_path
    file_meta = FileMetaDataset()
    file_meta.FileMetaInformationGroupLength = ds.file_meta.FileMetaInformationGroupLength
    file_meta.MediaStorageSOPClassUID = ds.file_meta.MediaStorageSOPClassUID
    file_meta.MediaStorageSOPInstanceUID = ds.file_meta.MediaStorageSOPInstanceUID
    file_meta.TransferSyntaxUID = "1.2.840.10008.1.2.1"  # Explicite VR Little Endian + uncompressed 

    file_meta.ImplementationClassUID = ds.file_meta.ImplementationClassUID
    file_meta.ImplementationVersionName = ds.file_meta.ImplementationVersionName
    data = FileDataset(dicom_path, {}, file_meta=file_meta, preamble=b"\0" * 128)
    data.is_little_endian = True

    data.is_implicit_VR = False # set to Explicite


    # uncompress
    data.PixelData = ds.pixel_array.tobytes()
    list_addr_dicom = list(ds)
    for addr in list_addr_dicom:
        tag = str(addr.tag).replace(', ','').replace(')','').replace('(','').upper()
        data[tag] = ds[tag]
    data.PixelData = ds.pixel_array.tobytes()
    data.save_as(file_path)

    return data, flag




# TODO to remove
def anonymization_tracker (glm_instance_id, list_anonym_tracker_tmp):
    """Build and save anonymization tracker in csv format
        input:  glm_instance_id
                list of blancked words and keeped words
    """

    # Add the line anonymization tracker to anonymization_result.csv

    # In case of empty list_anonym_tracker => set value to 0
    try: 
        df_anonym_tracker_tmp = pd.DataFrame({"file_name": glm_instance_id, "blanked_word": [
                                        list_anonym_tracker_tmp[0]], "passed_word": [list_anonym_tracker_tmp[1]]})
    except:
        df_anonym_tracker_tmp = pd.DataFrame({"file_name": glm_instance_id, "blanked_word": [0], "passed_word": [0]})
    
    df_anonym_tracker_tmp.set_index("file_name", inplace=True)
    df_anonym_tracker_tmp.to_csv("anonymization_result.csv", mode='a', header=False, index=True)

    return 0

# TODO remove lot of field
def exporter_log(flag_dicom, ser_log, glm_study_id, glm_instance_id, path_save_anonymized, output_folder, csv_log):
    """
    Build and save the log csv:
    (link between dicom tags and hashed dicom tags)
    input:  ser_log
    """


    ser_log_tmp = ser_log.copy()
    
    corrupted = flag_dicom["corrupted"]
    wrong_modality = flag_dicom["wrong_modality"]
    fract = flag_dicom["fract"]
    ok = flag_dicom["ok"]
    total_bad_dicom = corrupted + wrong_modality + fract

    # IF no DICOM
    if (total_bad_dicom == 0) and (ok == 0):
        ser_log.at["report_date"] = ""
        status = "no_image"
    # IF only bad DICOM
    elif (total_bad_dicom != 0) and (ok == 0):
        status = f"all_deleted: corrupted:{corrupted} modality:{wrong_modality} fract:{fract} ok:{ok}"
        ser_log.at["report_date"] = ""
    # some bad DICOM + some ok DICOM
    elif  (total_bad_dicom != 0) and (ok != 0):
        status = f"Some_deleted: corrupted:{corrupted} modality:{wrong_modality} fract:{fract} ok:{ok}"
    # only good DICOM
    else:
        status = "ok"


    now = datetime.datetime.now()
    date_export = now.strftime("%Y-%m-%d %H:%M:%S")

    ser_log_tmp = health_check(ser_log_tmp, output_folder)

    delta = datetime.datetime.now() - ser_log_tmp.at["timer_process"]
    ser_log_tmp.at["timer_process"] = round(delta.total_seconds(), 3)


    df_log_to_save = pd.DataFrame({    "client": ser_log_tmp["client"], #
                                    "priority": ser_log_tmp["priority"], #
                                    "batch": [ser_log.at["batch"]], #
                                    "report_date": [ser_log.at["report_date"]], #
                                    "query_level": ser_log_tmp["query_level"], #
                                    "accession_number": [ser_log.at["accession_number"]], #
                                    "study_instance_uid": [ser_log.at["study_instance_uid"]], #
                                    "glm_study_id": [glm_study_id], #
                                    "glm_instance_id": [glm_instance_id], #
                                    "ram_load": ser_log_tmp["ram_load"], #
                                    "cpu_load": ser_log_tmp["cpu_load"], #
                                    "cpu_temp": ser_log_tmp["cpu_temp"], #
                                    "disk_load": ser_log_tmp["disk_load"], #
                                    "timer_process": ser_log_tmp["timer_process"], #
                                    "timer_query": ser_log_tmp["timer_query"],  #
                                    "status" : status, #
                                    "date_export": date_export  }) #
    df_log_to_save.to_csv(csv_log, mode="a", header=False, index=False)

    return df_log_to_save



def path_dicom_ext(path_to_folder, output_folder):
    """ Find all dicom file in folder,
        add extension .dcm to file without ext
        save the file in the tmp_dicom folder
    Actually, only use for Cochin
        input: folder path
        output: list of path
    """

    list_path = []
    for dirpath, dirs, files in os.walk(path_to_folder):  
                for filename in files:
                    path_to_file = os.path.join(dirpath,filename)

                    file_name = os.path.basename(path_to_file)
                    extension = os.path.splitext(file_name)[1]
                    
                    ds_dicom = dcmread(path_to_file)
                    if ".dcm" not in extension:
                        new_path = os.path.join(output_folder,(filename + ".dcm"))
                        ds_dicom.save_as(new_path)
                        list_path.append(new_path) 
                    else:

                        new_path = os.path.join(output_folder,filename)
                        ds_dicom.save_as(new_path)
                        list_path.append(new_path)  

    return(list_path)


def main_extractor(path_to_json, path_to_white_list, path_to_dicom_csv, client_id, csv_log, debug_mode, query_delay, stop):
    """
    main function
    """




    # open initialization file .json
    try:
        aet_title, aet_ip, aet_port, aec_title, aec_ip, aec_port, output_folders, modality, image_modality_anonymisation, delay = initialization_json(
            path_to_json, client_id)
        print("Initialization file => OK")
    except:
        print("Can't find the initialization file .json")
        exit(1)

    list_modality = modality

    # open the white list .csv
    try:
        df_white_list = CsvToPandas(path_to_white_list, ["tag", "private"])
        print("White list => OK")
    except:
        print("Can't find the white list .csv")
        exit(1)

    output_folder = "./output"
    # # IF storage drive exist
    # if storage_check(output_folder) != 0x0000:
    #     print(f"Wrong save folder path:\n {output_folder} ")
    #     sys.exit(1)
    # else:
    #     print("Save HDD => OK")


    file_initialization(csv_log)

    df_log = pd.read_csv(csv_log)

    print(f"Debug mode: {debug_mode}")

    # check network
    network_check(aet_title, aec_ip, aec_port, aec_title)

    # open input csv and format it
    df_dicom_to_extract = CsvToPandas(path_to_dicom_csv, input_col=[
                                      "prio", "batch", "studyInstanceUID", "accessionNumber"])

    
    df_dicom_to_extract = df_formater(df_dicom_to_extract, client_id, debug_mode)
    print(df_dicom_to_extract)

    list_accession_number = [index for index in df_dicom_to_extract['accession_number']]
    print(list_accession_number)


    # remove examens already query if debug_mode off    
    if debug_mode == False:
        # get DICOM already query
        df_already_query = CsvToPandas(csv_log, input_col=["accession_number"])
        df_already_query.dropna(inplace=True)
        df_already_query.drop_duplicates(subset=["accession_number"], inplace=True)
        df_already_query["accession_number"] = df_already_query["accession_number"].astype(str)
        list_already_query = [index for index in df_already_query['accession_number']]
        print(f"list already query: {list_already_query}")
        list_accession_number = [item for item in list_accession_number if item not in list_already_query]
        print(f"Total accesion number already query: {len(list_already_query)} ")

    total_query = len(list_accession_number)
    query_counter = 0

    print(f"Total accesion number will be query: {len(list_accession_number)}")


    # Get all StudyUIDs from accession number
    for accession_number in list_accession_number:

        # Use for scheduler: IF job timer end, finish
        if stop < time.time():
            print(f"End of job at: {time.ctime(time.time())}")
            return 0

        query_counter += 1
        print(f"Query {query_counter}/{total_query} ")
        

        print(f"Sleep for {query_delay} secondes")
        time.sleep(query_delay)

        df_log_tmp = df_dicom_to_extract.loc[df_dicom_to_extract["accession_number"] == accession_number].copy()
        # debug_mode with identical queries => only 1 query
        df_log_tmp.drop_duplicates(subset=["accession_number"], inplace=True) 

        ser_log = df_log_tmp.squeeze().copy()

        # init ser_log status
        ser_log.at["timer_query"] = datetime.datetime.now()
        ser_log.at["status"] = "ok"

        # get studyUID
        list_study_instance_uid, c_find_status = c_find_query_study_uid(aet_title, aec_title, aec_ip, aec_port, accession_number)

        # IF empty AccessionNumber (no study UID)
        if c_find_status != "c_find_ok":
            flag_dicom = {"flag":0, "corrupted":0, "wrong_modality":0, "fract":0, "ok":0}
            ser_log.at["timer_process"] = datetime.datetime.now()
            ser_log.at["study_instance_uid"] = ""
            glm_study_id = ""
            glm_instance_id = ""
            path_save_anonymized = ""
            exporter_log(flag_dicom, ser_log, glm_study_id, glm_instance_id, path_save_anonymized, output_folder, csv_log)
            continue

        


        print(f"Study UID returned for C-FIND on AN:{accession_number} ")
        print(list_study_instance_uid)

        # query the StudyUIDs associated to the AN
        for study_instance_uid in list_study_instance_uid:

            print (study_instance_uid)
            ser_log["study_instance_uid"] = study_instance_uid

            service_status = move_scu(aet_title, aet_port, aec_ip, aec_port, aec_title, ser_log)

        # Chrono
        delta = datetime.datetime.now() - ser_log.at["timer_query"]
        ser_log.at["timer_query"] = round(delta.total_seconds(), 3)
        ser_log.at["timer_process"] = datetime.datetime.now()


        list_dicom_path = path_to_dicom("tmp_dicom")

        print(f"List_dicom: {list_dicom_path} ")
        # If empty DICOM folder => write log and continue
        if len(list_dicom_path) == 0:
            flag_dicom = {"flag":0, "corrupted":0, "wrong_modality":0, "fract":0, "ok":0}
            print(f" {study_instance_uid} is empty")
            # build and write the exporter log
            glm_instance_id = "not_processed"
            path_save_anonymized = "not_saved"
            glm_study_id = "not_processed"

            # Case: only query study_uid in export_list csv => empty_list => no study_uid
            try: 
                _ = ser_log["study_instance_uid"]
            except:
                ser_log["study_instance_uid"] = "no_study_uid"

            exporter_log(flag_dicom, ser_log, glm_study_id, glm_instance_id, path_save_anonymized, output_folder, csv_log)
            # safety clean
            list_dicom_path = path_to_dicom("tmp_dicom")
            for file_path in list_dicom_path:
                os.remove(file_path)
            continue #pass to the next AN

        already_process = 0
        # init flag for the AN
        flag_dicom = {"flag":0, "corrupted":0, "wrong_modality":0, "fract":0, "ok":0}

        # loop through all StudyUID from the accession_number
        # filter and clean the DICOM
        for path in list_dicom_path:

            # get total of bad DICOM at T0
            total_bad_dicom_t0 = flag_dicom["corrupted"]+flag_dicom["wrong_modality"]+flag_dicom["fract"]

            ds_dicom = dcmread(path)

            # date builder
            report_date, flag_pass = glm_study_date(ds_dicom, df_log)

            ser_log["report_date"] = report_date


            if (flag_pass != 0) and (debug_mode == False):
                # kill DICOM already process
                os.remove(path) 
                print("already_processed")
                already_process += 1
                continue

            ds_dicom = dcmread(path)

            ds_dicom = dicom_tag_filter(ds_dicom, df_white_list)

            # ds_dicom.save_as(path) # can be remove, need a few test
            # ds_dicom = dcmread(path) # can be remove, need a few test

            ds_dicom, flag = dicom_normalization(ds_dicom, path, list_modality)
            
            file_name = os.path.basename(path)


            try :
                ser_log["accession_number"] = ds_dicom[0x0008, 0x0050].value
            except:
                ser_log["accession_number"] = "no_an"
            
            ser_log["study_instance_uid"] = ds_dicom[0x0020, 0x000D].value


            flag_dicom = dicom_filter(ds_dicom, flag_dicom, list_modality)
            total_bad_dicom_t1 = flag_dicom["corrupted"]+flag_dicom["wrong_modality"]+flag_dicom["fract"]

            # IF the dicom is bad => delete it
            if (total_bad_dicom_t1-total_bad_dicom_t0)> 0:
                # kill the tmp dicom
                os.remove(path)
                continue


        list_dicom_path = path_to_dicom("tmp_dicom")
        # If empty DICOM folder => only bad DICOM => write log and continue
        if len(list_dicom_path) == 0:
            print(f" {study_instance_uid} is empty")
            # build and write the exporter log
            glm_instance_id = "not_processed"
            path_save_anonymized = "not_saved"
            glm_study_id = "not_processed"
            exporter_log(flag_dicom, ser_log, glm_study_id, glm_instance_id, path_save_anonymized, output_folder, csv_log)
            # safety clean
            list_dicom_path = path_to_dicom("tmp_dicom")
            for file_path in list_dicom_path:
                os.remove(file_path)
            continue #pass to the next AN

        # loop through all StudyUID from the accession_number
        for path in list_dicom_path:

            if pd.isna(ser_log.at["timer_process"]):
                ser_log.at["timer_process"] = datetime.datetime.now()

            file_name = os.path.basename(path)

            # Anonymize DICOM image and tags
            dicom_anonymized, list_anonym_tracker_tmp, image_filtered, image_png, batch_name = main_anonymization(
                path, df_white_list, client_id, report_date)

            # build and write the csv anonymization_tracker
            glm_study_id = dicom_anonymized[0x3679, 0x1020].value
            glm_instance_id = dicom_anonymized[0x3679, 0x1040].value
            anonymization_tracker (glm_instance_id, list_anonym_tracker_tmp)

            date_folder = report_date

            # save anonymized DICOM
            path_save_anonymized = folder_tree_builder(output_folder, batch_name, date_folder, glm_study_id, glm_instance_id)

            dicom_anonymized.is_implicit_VR = False # test line to supp

            print(path_save_anonymized)
            dicom_anonymized.save_as(path_save_anonymized, write_like_original=False)
            os.remove(path) # clean tmp dicom

            # # TEST -----------------
            # # import cv2
            # # file_path_png = os.path.join(output_folder, dicom_name+".png")
            # # cv2.imwrite(file_path_png, image_png)
            # # print(f"PNG anonymized saved at: {file_path} ")
            # # file_path_png = os.path.join(output_folder, dicom_name+"_filter.png")
            # # cv2.imwrite(file_path_png, image_filtered)
            # # print(f"PNG filter saved at: {file_path} ")
            # # TEST -----------------

            # build and write the exporter log
            exporter_log(flag_dicom, ser_log, glm_study_id, glm_instance_id, path_save_anonymized, output_folder, csv_log)            

    return query_counter



if __name__ == '__main__':


    # nohup python3 extractor.py export_list_risf.csv RISF > log_2021_10_25.txt &

    # python3 main.py pacs_list/dicom_imported_an_x3.csv pacs_orthanc

    # Initialization
    # variables:
    path_to_json = "extractor.json"
    path_to_white_list = "dicom_white_list.csv"
    csv_log = "exporter_log.csv"

    debug_mode = True
    query_delay = 1
    # end of script: used for scheduler script 
    stop = time.time() + 365*24*60*60 # max script time = 1 year

    if (len(sys.argv) != 3):
        print("Usage: python extractor.py path_to_dicom_list.csv client_id")
        exit(1)
    else:
        print("Input files => OK")
        path_to_dicom_csv = sys.argv[1]
        client_id = sys.argv[2]


    # normal run
    query_counter = main_extractor(path_to_json, path_to_white_list, path_to_dicom_csv, client_id, csv_log, debug_mode, query_delay, stop)

    print(f"End of {query_counter} query at: {time.ctime(time.time())}")


