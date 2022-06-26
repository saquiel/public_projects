#! /usr/bin/env python3
# coding = utf-8



# Change directory to local extractor.py directory
# python extractor.py path-to-list_dicom.csv client_id
# example:
# nohup python3 main_new.py pacs_list/dicom_imported_an_x3.csv pacs_orthanc > log_mide.txt &
# python3 main_new.py pacs_list/dicom_imported_an_x3.csv pacs_orthanc


import os
import sys
from pydicom.dataset import Dataset
from pynetdicom import AE, evt, StoragePresentationContexts, debug_logger, AllStoragePresentationContexts, ALL_TRANSFER_SYNTAXES
import json
import pandas as pd
import numpy as np
from pydicom import dcmread
import datetime
import time
import pathlib
from pydicom.dataset import FileDataset, FileMetaDataset
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind
from pydicom.pixel_data_handlers.util import apply_modality_lut, apply_voi_lut
import cv2
import pytesseract
import difflib
from google.cloud import storage
# TEST
# debug_logger()

class medical_exam:
    def __init__(self, client_id, path_json, path_white_list, path_to_dicom_csv, debug):
        self.mide_version = "2.1"
        self.client_id = client_id
        self.path_json = path_json
        self.path_white_list = path_white_list
        self.path_dicom_to_query_csv = path_to_dicom_csv
        self.path_anonymization_csv = "anonymization_result.csv"
        self.path_mide_log_csv = "mide_log.csv"
        self.path_word_white_list = "word_white_list.csv"
        self.debug = debug
        self.delay = None
        # Network init
        self.aet_title = None
        self.aet_ip = None
        self.aet_port = None
        self.aec_title = None
        self.aec_ip = None
        self.aec_port = None
        self.output_folder = None
        self.cloud_storage = None
        self.network_faillure = False
        # Medical exam init
        self.list_modality = None
        self.image_modality_anonymisation = None
        self.df_white_list = None
        self.list_white_word = []
        self.prefilters_to_apply = []
        self.tesserac_config = '--psm 3'
        self.ocr_confidence_trigger = -1.0
        self.df_anonym_tracker = pd.DataFrame(
            columns=["file_name", "blanked_word", "passed_word"])

        # DICOM variables
        self.df_dicom_to_query = None
        self.list_accession_number_query = None
        self.an_to_query = None
        self.report_link_id = None
        self.batch_name = None
        self.list_study_uid_to_query = []
        self.study_uid_number = 0
        self.study_uid_to_query = None
        self.list_dicom = []
        self.dicom_number = 0
        self.ds_dicom = None
        self.png_image = None
        self.df_ocr = None
        self.image_background_color = None
        self.list_blanked_word = []
        self.list_unblanked_word = []

        # Status
        self.status = None
        self.network_faillure = False
        self.c_find_status = None
        self.c_move_status = None
        
        self.df_log = None
        self.study_status_corrupted = 0
        self.study_status_total_w_modality = 0
        self.study_status_total_report = 0       
        self.timer_query = None
        self.query_date = None
        self.mide_log_csv_status = None

        # auto initialization
        self.parse_json()
        self.parse_white_list()
        self.log_initialization()
        # self.init_anonymization_result()
        self.parse_dicom_to_query()
        self.edit_list_accession_number_query()

        
    def parse_json(self):
        """Initialize the class object with the json file"""
        with open(self.path_json, "r") as tmp_file:
            dict_init = json.load(tmp_file)

        self.aet_title = dict_init[self.client_id]["aet_title"].encode('ascii') # PACS requirement
        self.aet_ip = dict_init[self.client_id]["aet_ip"]
        self.aet_port = dict_init[self.client_id]["aet_port"]
        self.aec_title = dict_init[self.client_id]["aec_title"].encode('ascii')
        self.aec_ip = dict_init[self.client_id]["aec_ip"]
        self.aec_port = dict_init[self.client_id]["aec_port"]
        self.output_folder = dict_init[self.client_id]["output_folder"]
        self.cloud_storage = dict_init[self.client_id]["cloud_storage"]
        self.list_modality = dict_init[self.client_id]["modality"]
        self.image_modality_anonymisation = dict_init[self.client_id]["image_modality_anonymisation"]
        self.delay = dict_init[self.client_id]["delay"]


    def parse_white_list(self):
        """Initialize the white list df"""
        self.df_white_list = pd.read_csv(self.path_white_list, dtype=str, usecols=["tag", "private"], na_values=" NaN")
        self.df_white_list.dropna(inplace=True)

        df_word_white_list = pd.read_csv(self.path_word_white_list)
        self.list_white_word = df_word_white_list["white_word"].tolist()


    def parse_dicom_to_query(self):
        self.df_dicom_to_query = pd.read_csv(self.path_dicom_to_query_csv, dtype=str, usecols=["batch", "report_link_id", "accession_number"], na_values=" NaN")
        self.df_dicom_to_query.dropna(inplace=True)
        if self.df_dicom_to_query.empty:
            print(f"Can't proccess without accession_number in the csv file ")
            self.network_faillure = True
        # Query the same AN multiple time for debuging
        if self.debug == False:
            self.df_dicom_to_query.drop_duplicates(subset=["accession_number"], keep='first', inplace=True)


    def log_initialization(self):
        csv_cols = ["client", "batch", "report_link_id", "accession_number", 
                    "study_instance_uid", "study_uid_number", "dicom_number",
                    "status", "study_status_corrupted", "study_status_total_w_modality", "study_status_total_report",
                    "timer_query", "date_export", "list_blanked_word", "list_unblanked_word"]
        if not os.path.exists(os.path.normpath(self.path_mide_log_csv)):
            self.mide_log_csv_status = "OK created"
            df_log = pd.DataFrame(columns=csv_cols)
            df_log.to_csv(self.path_mide_log_csv, header=True, index=False)                    
        else:
            self.mide_log_csv_status = "OK"
        
        self.df_log = pd.read_csv(self.path_mide_log_csv ,dtype=str,usecols=csv_cols)
        return


    def edit_list_accession_number_query(self):
        """Create the accession number list to query
        If debug: double duplicate AN accepted"""
        self.list_accession_number_query = self.df_dicom_to_query["accession_number"].to_list()
        if self.debug == False and not self.df_log.empty:
            list_AN_already_query = self.df_log["accession_number"].to_list()

            self.list_accession_number_query = [elem for elem in self.list_accession_number_query if elem not in list_AN_already_query]
            print(f"Total accesion number already query: {len(list_AN_already_query)} ")
        

    def network_verification(self):
        """Detect NIC, PACS, Internet dysfonctionment
        input:  PACS address
        output: df_log updated with status
        """

        # test network interface card status
        local_host = "127.0.0.1"
        google = "8.8.8.8"
        if os.system("ping " + ("-c 1 ") + local_host) != 0:
            print("Network faillure: nic_default")
            self.network_faillure == True
        # test network connection with AEC PACS
        elif os.system("ping " + ("-c 1 ") + self.aec_ip) != 0:
            print("Network faillure: aec_unreachable")
            self.network_faillure == True
        # check internet connectivity (google)
        elif os.system("ping " + ("-c 1 ") + google) != 0:
            print("Network faillure: internet_unreachable")
            self.network_faillure == True
        # C-ECHO to AEC
        ae = AE(ae_title=self.aet_title)  # set AE title
        # Presentation abstract context initialization
        ae.add_requested_context('1.2.840.10008.1.1')
        assoc = ae.associate(self.aec_ip, self.aec_port, ae_title=self.aec_title)
        # if the association has been established
        if assoc.is_established:
            status = assoc.send_c_echo()
            if status.Status == 0:
                assoc.release()
                print("C-ECHO verification => OK")
                return 0
            
            else:
                print("Network faillure: c_echo_faillure")
                sys.exit(1)
        else:
            # Association rejected, aborted or never connected
            print("Network faillure: no_aec_association")
            sys.exit(1)


    # -----Query functions-----
    def c_find_query_study_uid(self):
        """Query the PACS with C-FIND with an AccessionNumber to get StudyInstanceUID associated
            input:  AccessionNumber
                    network connexion parameters
            output: list of study_instance_uid
                    status of C-FIND query"""     

        ae = AE(ae_title=self.aet_title)
        # Presentation abstract context initialization
        ae.add_requested_context('1.2.840.10008.5.1.4.1.2.1.1')

        ds = Dataset()
        # Add query retrieve level
        ds.QueryRetrieveLevel = 'STUDY'

        ds.AccessionNumber=self.an_to_query
        ds.StudyInstanceUID = "" #return Study UID

        assoc = ae.associate(self.aec_ip, self.aec_port, ae_title=self.aec_title)

        list_study_uid = []
        if assoc.is_established:
            # Send the C-FIND request
            responses = assoc.send_c_find(ds, PatientRootQueryRetrieveInformationModelFind)
            for (status, identifier) in responses:
                if status:
                    try:
                        list_study_uid.append(str(identifier[0x0020, 0x000d].value))
                        self.c_find_status = "c_find_ok"
                        assoc.release()
                        self.list_study_uid_to_query = list_study_uid
                        return 
                    except:
                        self.c_find_status = "c_find_no_study_uid"
                else:
                    self.c_find_status = "c_fing_invalid_response"
            assoc.release()
            return 
        else:
            self.c_find_status = "c_find_association_fail"        
        return 


    def c_move_query_study_uid(self):
        """
        DICOM MOVE_SCU service
            build and start a STORE_SCP service
            build and request a MOVE_SCU to the AEC
            STORE_SCP wait for the AEC response
            close the STORE_SCP service

        Service _status:
            0xC001: Connection timed out, was aborted or received invalid response
            0xC002: Association rejected, aborted or never connected
        """

        def handle_store(event):
            """Handle EVT_C_STORE events
            input:  trigger by evt.EVT_C_STORE
            """

            ds = event.dataset
            # set the dataset’s file_meta attribute
            ds.file_meta = event.file_meta
            ds.SOPInstanceUID = event.request.AffectedSOPInstanceUID
            self.list_dicom.append(ds)

            return 0x0000

        self.query_date = datetime.datetime.now()

        # on event C-Store call handler
        handlers = [(evt.EVT_C_STORE, handle_store)]

        # Initialise the Application Entity
        ae = AE()
        ae.ae_title = self.aet_title

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
        scp = ae.start_server(("", self.aet_port), block=False, evt_handlers=handlers)

        # Associate with peer AE IP and port
        assoc = ae.associate(self.aec_ip, self.aec_port, ae_title=self.aec_title)

        if assoc.is_established:
            # Use the C-MOVE service to send the identifier
            # build the dicom query
            ds_query = Dataset()
            ds_query.QueryRetrieveLevel = "STUDY"
            setattr(ds_query, "StudyInstanceUID", self.study_uid_to_query)

            # ds_query = query_builder(query_level, study_instance_uid)
            responses = assoc.send_c_move(ds_query, self.aet_title, sop_uid)

            for (status, identifier) in responses:
                if status:
                    self.c_move_status = status.Status
                else:
                    self.c_move_status = 0xC002

            # Release the association
            assoc.release()
        else:
            # Association rejected, aborted or never connected
            self.c_move_status = 0xC003

        # Stop our Storage SCP
        scp.shutdown()

        self.timer_query = datetime.datetime.now() - self.query_date

        # TEST: write dicom on local drive
        # for ds in self.list_dicom:
        #     dicom_name = ds.SOPInstanceUID
        #     path_to_folder = "tmp_dicom"
        #     file_path = pathlib.Path.cwd().joinpath(path_to_folder, dicom_name+".dcm")
        #     ds.save_as(file_path, write_like_original=False)
        #     print(f"saved: {file_path}")

        return 


    # -----Filtering functions-----
    def dicom_tag_prefiltering(self):
        """Loop through the StudyUID list of DICOM:
        Delete unnecessay DICOM tags:
            add temporaire list of tag in order to correctly
            open the DICOM. Will be removed after processing.
            Avoid uncomformant DICOM field that could break the process
            """

        list_tag_tmp = self.df_white_list["tag"].to_list()

        list_tag_tmp += [  
                                "00080016",# SOP Class UID Attribute
                                "00080018",# SOP Instance UID Attribute
                                "0020000D",# Study Instance UID Attribute
                                "0020000E",# Series Instance UID Attribute
                                "00200011",# Series Number Attribute
                                "00200013",# Instance Number Attribute
                                "0020000D",# Study Instance UID Attribute
                                ]

        for ds_dicom in self.list_dicom:
            # extract dicom tags
            list_tag_dicom = list(ds_dicom)
            list_addr_dicom = [str(addr.tag).replace(', ', '').replace(
                    ')', '').replace('(', '').upper() for addr in list_tag_dicom]
            # delete unecessay DICOM tags 
            for addr in list_addr_dicom:
                if (addr) not in list_tag_tmp:
                    del ds_dicom[addr]

        return


    def dicom_image_corrupted_filter(self):
        """Loop through the StudyUID list of DICOM:
        Remove corrumpted (can open pixel array parameter)
        Update the corrupted DICOM flag"""
        tmp_list_dicom = []
        for ds_dicom in self.list_dicom:
            try:
                ds_dicom.pixel_array
                tmp_list_dicom.append(ds_dicom)
                try:
                     ds_dicom.pixel_array.tobytes()
                except:
                    self.study_status_corrupted += 1
            except:
                self.study_status_corrupted += 1

        self.list_dicom = tmp_list_dicom
        tmp_list_dicom = [] # free memory
        return


    def dicom_modality_filter(self):
        """Loop through the StudyUID list of DICOM:
            Remove unnecessary modality and report
            Update wrong modality flag 
        """

        tmp_list_dicom = []
        for ds_dicom in self.list_dicom:

            if ds_dicom.Modality not in self.list_modality:
                self.study_status_total_w_modality += 1

            elif ds_dicom.BodyPartExamined == "REPORT":
                self.study_status_total_w_modality += 1

            else:
                tmp_list_dicom.append(ds_dicom)

        self.list_dicom = tmp_list_dicom
        tmp_list_dicom = [] # free memory

        return 0


    def conform_dicom_to_pydicom(self):
        """Write DICOM to a temporary folder to force the conformance with Pydicom
        => No UT"""
            
        dicom_name = self.ds_dicom.SOPInstanceUID
        path_to_folder = "tmp_folder"
        file_path = pathlib.Path.cwd().joinpath(path_to_folder, dicom_name+".dcm")
        self.ds_dicom.save_as(file_path, write_like_original=False)
        self.ds_dicom = dcmread(file_path)
        os.remove(file_path)


    def dicom_normalization(self):
        """
        Uncompress, set transfert syntax to little endian and VR explicite 
        """

        # IF dicom file is normalized: pass
        if self.ds_dicom.file_meta.TransferSyntaxUID != "1.2.840.10008.1.2.1": # if little endian and uncompressed and explicite => do nothing
            
            # normalize DICOM file
            file_meta = FileMetaDataset()
            file_meta.FileMetaInformationGroupLength = self.ds_dicom.file_meta.FileMetaInformationGroupLength
            file_meta.MediaStorageSOPClassUID = self.ds_dicom.file_meta.MediaStorageSOPClassUID
            file_meta.MediaStorageSOPInstanceUID = self.ds_dicom.file_meta.MediaStorageSOPInstanceUID
            file_meta.TransferSyntaxUID = "1.2.840.10008.1.2.1"  # Explicite VR Little Endian + uncompressed 

            file_meta.ImplementationClassUID = self.ds_dicom.file_meta.ImplementationClassUID
            file_meta.ImplementationVersionName = self.ds_dicom.file_meta.ImplementationVersionName
            output_dicom = FileDataset(self.ds_dicom, {}, file_meta=file_meta, preamble=b"\0" * 128)
            output_dicom.is_little_endian = True

            output_dicom.is_implicit_VR = False # set to Explicite

            # uncompress
            output_dicom.PixelData = self.ds_dicom.pixel_array.tobytes()
            list_addr_dicom = list(self.ds_dicom)
            for addr in list_addr_dicom:
                tag = str(addr.tag).replace(', ','').replace(')','').replace('(','').upper()
                output_dicom[tag] = self.ds_dicom[tag]
            output_dicom.PixelData = self.ds_dicom.pixel_array.tobytes()
            
            self.ds_dicom = output_dicom

        return 


    # ----Image anonymization----
    def dicom_to_png(self):
        """Convert DICOM pixel array to a png image
        Parts of the function came from Pydicom library"""

        img_array = self.ds_dicom.pixel_array

        # Rescale Slope Intercept
        img_transformed = apply_modality_lut(img_array, self.ds_dicom)

        # If VOILUTSequence exists => apply_voi_lut 
        if "VOILUTSequence" in self.ds_dicom:
            img_transformed = img_transformed.astype(np.int) # only accepts int array

        # If no info is available for VOI lut then use auto-windowing
        elif ("WindowCenter" not in self.ds_dicom) or ("WindowWidth" not in self.ds_dicom):
            # Init RescaleSlope and RescaleIntercept
            if "RescaleSlope" not in self.ds_dicom:
                self.ds_dicom.RescaleSlope = 1.0
            if "RescaleIntercept" not in self.ds_dicom:
                self.ds_dicom.RescaleIntercept = 0.0
            self.ds_dicom.WindowCenter = (
                np.max(img_transformed) + np.min(img_transformed) + 1
            ) / 2 * self.ds_dicom.RescaleSlope + self.ds_dicom.RescaleIntercept
            self.ds_dicom.WindowWidth = (
                np.max(img_transformed) - np.min(img_transformed) + 1
            ) * self.ds_dicom.RescaleSlope

        if self.ds_dicom.PhotometricInterpretation in ["MONOCHROME1", "MONOCHROME2"]:
            img_transformed = apply_voi_lut(img_transformed, self.ds_dicom)


        # 8-bit array conversion => Code from pydicom

        # calculate the correct min/max pixel value 
        if "ModalityLUTSequence" in self.ds_dicom:
            # Unsigned
            y_min = 0
            bit_depth = self.ds_dicom.ModalityLUTSequence[0].LUTDescriptor[2]
            y_max = 2 ** bit_depth - 1
        elif self.ds_dicom.PixelRepresentation == 0:
            # Unsigned
            y_min = 0
            y_max = 2 ** self.ds_dicom.BitsStored - 1
        else:
            # Signed
            y_min = -(2 ** (self.ds_dicom.BitsStored - 1))
            y_max = 2 ** (self.ds_dicom.BitsStored - 1) - 1

        # If RescaleSlope and RescaleIntercept => actual data range
        if "RescaleSlope" in self.ds_dicom and "RescaleIntercept" in self.ds_dicom:
            y_min = y_min * self.ds_dicom.RescaleSlope + self.ds_dicom.RescaleIntercept
            y_max = y_max * self.ds_dicom.RescaleSlope + self.ds_dicom.RescaleIntercept

        # convert to 8-bit array
        ndarray_img_8bit_float = np.round(255.0 * (img_transformed - y_min) / (y_max - y_min))

        # Inverse image pixel value (contrast) if MONOCHROME1
        if self.ds_dicom.PhotometricInterpretation in ["MONOCHROME1"]:
            ndarray_img_8bit_float = 255.0 - ndarray_img_8bit_float

        # Convert to rounded int array with 3 channels
        rounded_int = np.round(ndarray_img_8bit_float).astype(np.uint8)

        if len(rounded_int.shape) == 2:
            self.png_image = np.repeat(rounded_int[:, :, np.newaxis], 3, axis=-1)
        elif (len(rounded_int.shape) == 3) and (rounded_int.shape[-1] == 3):
            self.png_image = rounded_int

        return 


    def image_prefiltering(self):
        '''Apply a filter to a png image
            note:   filter are apply in the order bellow'''

        if "median_blur" in self.prefilters_to_apply:
            self.png_image = cv2.medianBlur(self.png_image, 3)
        if "grayscale" in self.prefilters_to_apply:
            self.png_image = cv2.cvtColor(self.png_image, cv2.COLOR_BGR2GRAY)
        if "morpho" in self.prefilters_to_apply:
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            self.png_image = cv2.morphologyEx(self.png_image, cv2.MORPH_OPEN, kernel, iterations=1)
        if "dilatation" in self.prefilters_to_apply:
            kernel = np.ones((5, 5), np.uint8)
            self.png_image = cv2.dilate(self.png_image, kernel, iterations=1)
        if "erosion" in self.prefilters_to_apply:
            kernel = np.ones((5, 5), np.uint8)
            self.png_image = cv2.erode(self.png_image, kernel, iterations=1)
        if "opening" in self.prefilters_to_apply:
            kernel = np.ones((5, 5), np.uint8)
            self.png_image = cv2.morphologyEx(self.png_image, cv2.MORPH_OPEN, kernel)
        if "normalization" in self.prefilters_to_apply:
            norm_img = np.zeros((self.png_image.shape[0], self.png_image.shape[1]))
            self.png_image = cv2.normalize(self.png_image, norm_img, 0, 255, cv2.NORM_MINMAX)
        if "clahe" in self.prefilters_to_apply:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            self.png_image = clahe.apply(self.png_image)
        if "unsharp" in self.prefilters_to_apply:
            gauss = cv2.GaussianBlur(self.png_image, (3, 3), 0)
            self.png_image = cv2.addWeighted(self.png_image, 2, gauss, -1, 0)
        if "inverse" in self.prefilters_to_apply:
            self.png_image = 255 - self.png_image
        if "gaussian_blur" in self.prefilters_to_apply:
            self.png_image = cv2.GaussianBlur(self.png_image, (5, 5), 0)

        return


    def image_thresholding(self):
        """
        If pixel intensity is greater than the set threshold, value set to 255, else set to 0 (black)
        and invert
        """
        _, self.png_image = cv2.threshold(
    self.png_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        return


    def ocr_processing(self):
        '''Run Tesseract OCR to extract character and word from
        the png image'''
        # oem(OCR Engine modes):
        # 0    Legacy engine only.
        # 1    Neural nets LSTM engine only.
        # 2    Legacy + LSTM engines.
        # 3    Default, based on what is available.

        # run tesseract
        dict_ocr = pytesseract.image_to_data(
            self.png_image, output_type=pytesseract.Output.DICT, config=self.tesserac_config)
        
        self.df_ocr = pd.DataFrame(dict_ocr) 
        self.df_ocr["conf"] = self.df_ocr["conf"].astype(float)

        return 


    def ocr_postfiltering(self):
        """Filter tesseract result based on:
        geometric position
        confidence level
        character size
        number of character
        white_list
        approximate white_list
        """

        # Blank only top and lower part of the image
        upper_cut = int(self.png_image.shape[0] * 0.85)
        lower_cut = int(self.png_image.shape[0] * 0.15)
        self.df_ocr = self.df_ocr[~self.df_ocr["top"].between(lower_cut, upper_cut)]
        list_ocr_word = self.df_ocr["text"].tolist()

        # Filter by confidence level
        self.df_ocr = self.df_ocr[self.df_ocr["conf"] > self.ocr_confidence_trigger]

        # remove smal blanking => avoid artefact (2 pixel)
        self.df_ocr = self.df_ocr[self.df_ocr["width"] > 2]
        self.df_ocr = self.df_ocr[self.df_ocr["height"] > 2]
        self.df_ocr["text"] = self.df_ocr["text"].str.lower()

        # Filter unique character
        self.df_ocr = self.df_ocr[self.df_ocr["text"].str.len() >= 1]

        self.df_ocr = self.df_ocr[~self.df_ocr["text"].isin([" ", "  ", "   "])]

        # Filter: remove all word that are in list white word
        self.df_ocr = self.df_ocr[~self.df_ocr["text"].isin(self.list_white_word)]

        # DIFFLIB: approximate dict
        list_tmp_word = []
        for word in self.list_white_word:
            list_tmp_word.extend(self.df_ocr.loc[self.df_ocr['text'].apply(lambda x: difflib.SequenceMatcher(None,word,x).ratio()) > 0.75]["text"].tolist())
        self.df_ocr = self.df_ocr[~self.df_ocr['text'].isin(list_tmp_word)]

        self.list_blanked_word = self.df_ocr["text"].tolist()
        self.list_unblanked_word = [text for text in list_ocr_word if text not in self.list_blanked_word]

        return


    def get_background_color(self):
        """Compute the DICOM file background color 
        based on max value for MONOCHROME1 and min otherwise"""
        
        pixel_array = self.ds_dicom.pixel_array
        photometric = self.ds_dicom.PhotometricInterpretation
        # IF normal image or inversed image
        if photometric == "MONOCHROME1":
            self.image_background_color = np.max(pixel_array)
        else:
            self.image_background_color = np.min(pixel_array)
        return 


    def image_blanking(self):
        """Replace word found by OCR by the image background value"""
        pixel_array = self.ds_dicom.pixel_array

        # image blanking with image background color
        for index in self.df_ocr.index:
            x = int(self.df_ocr[self.df_ocr.index == index]["left"].iloc[0])
            y = int(self.df_ocr[self.df_ocr.index == index]["top"].iloc[0])
            w = int(self.df_ocr[self.df_ocr.index == index]["width"].iloc[0])
            h = int(self.df_ocr[self.df_ocr.index == index]["height"].iloc[0])
            pixel_array[y:y+h, x:x+w] = self.image_background_color
        self.ds_dicom.PixelData = pixel_array.tobytes()

        return 


    def patient_birth_date_deidentification(self):
        """ Round patient birth date to the 5 years (lower):
        e.g 19980123 => 19950000"""

        # If PatientBirthDate exists
        if "PatientBirthDate" in self.ds_dicom:
            # IF PatientBirthDate not empty
            if self.ds_dicom[0x0010, 0x0030]:

                patient_birth_date = self.ds_dicom[0x0010, 0x0030].value
                # Check for patient birth date conformance
                if not (isinstance(patient_birth_date, str)):
                    birth_date_deid = "00000000"
                elif not(len(patient_birth_date) == 8):
                    birth_date_deid = "00000000"
                else:
                    birth_date = int(patient_birth_date[:4])                   
                    birth_date_deid = str((birth_date // 5)*5) + "0000"
                self.ds_dicom[0x0010, 0x0030].value = birth_date_deid
        return


    def study_date_deidentification(self):
        """
        Study date deidentification by reducing precision to with month + year
        """

        # If StudyDate exists 
        if "StudyDate" in self.ds_dicom:
            # IF StudyDate not empty
            study_date_deid = "00000000"
            if self.ds_dicom.StudyDate:
                study_date = self.ds_dicom[0x0008, 0x0020].value
                # Check for study date conformance
                if (isinstance(study_date, str)) and (len(study_date) == 8):
                    day = int(study_date[-2:])
                    week = (day // 8) + 1
                    study_date_deid = study_date[:-2] + "W" + str(week)
            self.ds_dicom[0x0008, 0x0020].value = study_date_deid
        return 


    def dicom_tag_blanking(self):
        """Delete DICOM tag that are not on the white list
        """

        list_white = self.df_white_list["tag"].to_list()
        # delete DICOM tag that are not in the white list
        list_addr_dicom = list(self.ds_dicom)
        for addr in list_addr_dicom:
            tag = str(addr.tag).replace(', ', '').replace(
                ')', '').replace('(', '').upper()
            if tag not in list_white:
                del self.ds_dicom[tag]

        # Set necessary DICOM tag to 0:
        self.ds_dicom.add_new([0x0010, 0x0020], "LO", "0000")

        return 


    def dicom_tag_for_mide(self):
        """Write MIDE functionnal tag"""
        
        # add 00080080,InstitutionName,,client_id* LO
        self.ds_dicom.add_new([0x0008, 0x0080], "LO", self.client_id)
        # add 00081010,StationName,,MIDE_version* LO
        self.ds_dicom.add_new([0x0008, 0x1010], "LO", self.mide_version)
        # add 00080032,AcquisitionTime,,MIDE export date* TM*
        self.ds_dicom.add_new([0x0008, 0x0032], "TM", self.query_date)

        return


    def write_mide_log(self):
        """Append current log variable to the mide_log csv file"""
        values = [self.client_id,
                self.df_dicom_to_query[self.df_dicom_to_query["accession_number"] == self.an_to_query]["batch"].iloc[0],
                self.report_link_id,
                self.an_to_query,
                self.study_uid_to_query,
                self.study_uid_number,
                self.dicom_number,
                self.status,
                self.study_status_corrupted,
                self.study_status_total_w_modality,
                self.study_status_total_report,
                self.timer_query,
                self.query_date,
                self.list_blanked_word,
                self.list_unblanked_word]
        df_log_to_append = pd.DataFrame([values], columns=self.df_log.columns)
        df_log_to_append.to_csv(self.path_mide_log_csv, mode="a", header=False, index=False)
        return


    def store_on_cloud(self):
        "Store the DICOM file on a cloud service"

        dicom_name = self.report_link_id + "." + str(self.study_uid_number) + "." + str(self.dicom_number) +".dcm"
        path_to_folder = "tmp_dicom"
        file_path = pathlib.Path.cwd().joinpath(path_to_folder, dicom_name)
        self.ds_dicom.save_as(file_path, write_like_original=False)

        try:
            storage_client = storage.Client()
            bucket = storage_client.get_bucket(self.cloud_storage)
            blob = bucket.blob(dicom_name)
            blob.upload_from_filename(file_path)
            self.status = "cloud_storage_success"
        except:
            self.status = "cloud_storage_faillure"
        os.remove(file_path)
        
        return 



def main_extractor(path_to_json, path_white_list, path_to_dicom_csv, client_id, csv_log, debug, stop):
    """
    main function
    """
    examen = medical_exam(client_id, path_to_json, path_white_list, path_to_dicom_csv, debug)

    if examen.network_faillure == True:
        sys.exit()

    print(f"MIDE log csv => {examen.mide_log_csv_status}")
    print(f"Starting query {len(examen.list_accession_number_query)} accession number ")
    
    examen.network_verification()

    query_counter = 0
    # Get all StudyUIDs from accession number
    for accession_number in examen.list_accession_number_query:

        examen.an_to_query = accession_number

        examen.report_link_id = examen.df_dicom_to_query[examen.df_dicom_to_query["accession_number"] == examen.an_to_query]["report_link_id"].iloc[0]

    #     # Use for scheduler: IF job timer end, finish
    #     if stop < time.time():
    #         print(f"End of job at: {time.ctime(time.time())}")
    #         return 0
        
        time.sleep(examen.delay)

        # get studyUID
        examen.c_find_query_study_uid()

        # IF C_find failled:
        if examen.c_find_status != "c_find_ok":
            print("C_FIND failled")
            examen.write_mide_log()
            continue

        examen.study_uid_number = 0
        for study_uid in examen.list_study_uid_to_query:
            
            examen.study_uid_number += 1

            examen.study_uid_to_query = study_uid

            # Query the DICOM file
            examen.c_move_query_study_uid()

            # Filter DICOM list based on modality, report, and image corruption
            examen.dicom_image_corrupted_filter()
            examen.dicom_modality_filter()

            # If no DICOM to process, pass to next StudyUID
            if len(examen.list_dicom) == 0:
                examen.status = "no_study_uid"
                examen.write_mide_log()
                continue

            examen.dicom_number = 0
            for dicom in examen.list_dicom:
                
                examen.dicom_number += 1

                examen.ds_dicom = dicom

                # TODO broken function => add all DICOM filed
                # AttributeError: Unable to convert the pixel data: one of Pixel Data, Float Pixel Data or Double Float Pixel Data must be present in the dataset
                # # Remove process uneccesary tags
                # examen.dicom_tag_prefiltering()

                examen.conform_dicom_to_pydicom()

                # DICOM normalization
                examen.dicom_normalization()

                # Convert DICOM to png
                examen.dicom_to_png()

                # Image prefiltering
                examen.prefilters_to_apply = ["grayscale"]
                examen.image_prefiltering()
                examen.image_thresholding()
                examen.prefilters_to_apply = ["clahe", "gaussian_blur"]
                examen.image_prefiltering()

                # detect word in image
                examen.ocr_processing()

                # filter word
                examen.ocr_postfiltering()

                # Get  background image value
                examen.get_background_color()

                # blank sensible data on image
                examen.image_blanking()

                # Tag de-identification of DICOM list
                examen.patient_birth_date_deidentification()
                examen.study_date_deidentification()

                # Anonymize DICOM tags
                examen.dicom_tag_blanking()

                # Write MIDE functionnal tags
                examen.dicom_tag_for_mide()

                # Send DICOM file to Cloud
                examen.store_on_cloud()

                # build and write the mide log
                examen.write_mide_log()

            # reset list_dicom
            examen.list_dicom = []

        # reset list_study_uid_to_query
        examen.list_study_uid_to_query = []

        query_counter += 1

    return query_counter


if __name__ == '__main__':

    # Initialization
    # variables:
    path_to_json = "extractor.json"
    path_white_list = "dicom_white_list.csv"
    csv_log = "exporter_log.csv"

    debug = False
    # end of script: used for scheduler script 
    stop = time.time() + 365*24*60*60 # max script time = 1 year

    if (len(sys.argv) != 3):
        print("Usage: python extractor.py path_to_dicom_list.csv client_id")
        exit(1)
    else:
        print("Input files => OK")
        path_to_dicom_csv = sys.argv[1]
        client_id = sys.argv[2]

    print(f"Process run for {client_id}, debug mode:{debug}")
    try:
        df_dum = pd.read_csv(path_to_dicom_csv, dtype=str)
        print(f"Dicom csv: {path_to_dicom_csv} found")
    except FileNotFoundError:
        print("Dicom csv not found, input the path to the dicom list file")
        sys.exit(1)
    try:
        df_dum = pd.read_csv(path_white_list, dtype=str)
        print(f"White list: {path_white_list} found")
    except FileNotFoundError:
        print("White list not found, input the path to the white list csv")
        sys.exit(1)
    try:
        with open(path_to_json, "r") as tmp_file:
            dict_dum = json.load(tmp_file)
        print(f"JSON files: {path_to_json} found")
    except FileNotFoundError:
        print("JSON file not found, input the path to the JSON file")
        sys.exit(1)

    # normal run
    query_counter = main_extractor(path_to_json, path_white_list, path_to_dicom_csv, client_id, csv_log, debug, stop)

    print(f"End of {query_counter} query at: {time.ctime(time.time())}")


