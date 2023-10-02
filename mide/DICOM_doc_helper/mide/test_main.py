#! /usr/bin/env python3
# coding = utf-8

# CD to directory
# run:  pytest -v
# or group markers test: 
#   pytest -m anonymization_unit -v
#   pytest -m main_unit -v
#   pytest -m anonymization_functional -v
# output log
#   pytest -v > test_anonymization_result.log

#pytest -k 'test_dicom_ext'

import pytest
from pynetdicom.sop_class import CTImageStorage
# from anonymization import *
from main import *
import pandas as pd
import time
import copy
import imageio


@pytest.mark.main_unit
def test_obj_initialization():
    """Verify that Object is initialized with the correct element type"""

    path_to_json = "extractor.json"
    client_id = "unit_test"
    path_white_list = "data_test/dicom_white_list.csv"
    debug = False

    # Test for no accession number in dicom csv
    path_to_dicom_csv = "data_test/dicom_no_an.csv"
    test_exam = medical_exam(client_id, path_to_json, path_white_list, path_to_dicom_csv, debug)
    assert test_exam.network_faillure == True

    path_to_dicom_csv = "data_test/dicom_an_x3.csv"

    test_exam = medical_exam(client_id, path_to_json, path_white_list, path_to_dicom_csv, debug)
    
    assert test_exam.network_faillure == False

    # JSON test
    assert test_exam.aet_title ==  b"DEVICE"
    assert test_exam.aet_ip == "127.0.0.1"
    assert test_exam.aet_port == 10400
    assert test_exam.aec_title == b"UNIT_TEST_PACS"
    assert test_exam.aec_ip == "127.0.0.1"
    assert test_exam.aec_port == 11100
    assert test_exam.output_folder == ["./output"]
    assert test_exam.cloud_storage == "midedicomstorage"
    assert test_exam.list_modality == ["DX","CR", "US", "CT", "MRI"]
    assert test_exam.image_modality_anonymisation == ["DX", "CR"]
    assert test_exam.delay == 1

    # White list test
    assert type(test_exam.df_white_list) is pd.DataFrame
    
    # Dicom_to_query test
    df_dicom_to_query = pd.read_csv(path_to_dicom_csv, dtype=str, usecols=["batch", "accession_number"])
    assert list(test_exam.df_dicom_to_query["accession_number"]) == list(test_exam.df_dicom_to_query["accession_number"])

    # test for double AN cleaning
    path_to_dicom_csv = "data_test/dicom_an_multiple.csv"
    debug = True
    test_exam = medical_exam(client_id, path_to_json, path_white_list, path_to_dicom_csv, debug)
    assert len(test_exam.df_dicom_to_query) == 5
    debug = False
    test_exam = medical_exam(client_id, path_to_json, path_white_list, path_to_dicom_csv, debug)
    assert len(test_exam.df_dicom_to_query) == 3


@pytest.mark.main_unit
def test_c_find_query_study_uid():
    """With a C-FIND SCP service, verify that the function return correct StudyUID based on AccessionNumber"""

    def handler_find(event):
        """Handle a C-FIND request event."""
        ds = event.identifier

        if 'QueryRetrieveLevel' not in ds:
            # Failure
            yield 0xC000, None
            return

        elif ds.AccessionNumber == "12.3456789":
            identifier = Dataset()
            identifier.StudyInstanceUID = "01.123.456789.132"
            identifier.QueryRetrieveLevel = ds.QueryRetrieveLevel
            # Pending
            yield (0xFF00, identifier)

        else:
            yield 0xC000, None


    path_to_json = "extractor.json"
    client_id = "unit_test"
    path_white_list = "dicom_white_list.csv"
    path_to_dicom_csv = "pacs_list/dicom_imported_an_x3.csv"
    debug = False
    path_to_json = "extractor.json"

    examen = medical_exam(client_id, path_to_json, path_white_list, path_to_dicom_csv, debug)

    examen.list_accession_number_query = ["12.3456789", "01.789456"]

    handlers = [(evt.EVT_C_FIND, handler_find)]

    # Initialise the Application Entity and specify the listen port
    c_find_scp_server = AE()

    # Add the supported presentation context
    c_find_scp_server.add_supported_context(PatientRootQueryRetrieveInformationModelFind)

    # Start listening for incoming association requests
    c_find_scp_server.start_server(("127.0.0.1", 11100), block=False, evt_handlers=handlers)
    time.sleep(0.2)

    examen.an_to_query = examen.list_accession_number_query.pop(0)
    examen.c_find_query_study_uid()

    # SUID in PACS

    assert examen.list_study_uid_to_query == ["01.123.456789.132"]
    assert type(examen.list_study_uid_to_query) is list
    assert examen.c_find_status == "c_find_ok"

    # SUID not in PACS
    examen.an_to_query = examen.list_accession_number_query.pop(0)
    examen.c_find_query_study_uid()

    assert examen.c_find_status == "c_find_no_study_uid"

    c_find_scp_server.shutdown()


@pytest.mark.main_unit
def test_c_move_query_study_uid():
    """With a C-MOVE SCP service, verify that the function return correct DICOM based on Study UID"""

    def handle_move(event):
        """Handle a C-MOVE request event."""
        ds_query = event.identifier

        if 'QueryRetrieveLevel' not in ds_query:
            # Failure
            return 0xC000

        if event.move_destination == b'DEVICE':
            # yield the (address, port) of the destination AE to the SCU
            yield ("127.0.0.1", 10400)
        else:
            # Unknown destination AE
            yield (None, None)
            return
        if ds_query.StudyInstanceUID == ds_test.StudyInstanceUID:
            if event.is_cancelled:
                yield (0xFE00, None)
                return
            # Yield the total number of C-STORE sub-operations required
            yield 1
            # Yield the DICOM filed
            yield (0xFF00, ds_test)
            return 
        else:
            yield (None, None)
            return

    def move_scp(stored_dicom):
        """Simulate a PACS C-MOVE SCP service"""
        # Create application entity
        ae = AE()
        # Add the requested presentation contexts (Storage SCU)
        ae.requested_contexts = StoragePresentationContexts
        # Add a supported presentation context (QR Move SCP)
        ae.add_supported_context("1.2.840.10008.5.1.4.1.2.1.2")
        # Start listening for incoming association requests
        handlers = [(evt.EVT_C_MOVE, handle_move)]
        scp = ae.start_server(('', 11100), block=False, evt_handlers=handlers)
        return scp


    stored_dicom = "/home/zenbook/Documents/code/python/mide/data_test/1.3.6.1.4.1.14519.5.2.1.7777.9002.154181272448537806873380883469"
    ds_test = dcmread(stored_dicom)

    path_to_json = "extractor.json"
    client_id = "unit_test"
    path_white_list = "dicom_white_list.csv"
    path_to_dicom_csv = "pacs_list/dicom_imported_an_x3.csv"
    debug = False
    path_to_json = "extractor.json"

    test_examen = medical_exam(client_id, path_to_json, path_white_list, path_to_dicom_csv, debug)

    test_examen.study_uid_to_query = ds_test.StudyInstanceUID

    scp = move_scp(stored_dicom)
    time.sleep(0.2)
    test_examen.c_move_query_study_uid()
    scp.shutdown()


    assert test_examen.c_move_status == 0

    list_usefull_tags = test_examen.df_white_list["tag"].to_list()
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
    list_tag_dicom = list(ds_test)
    list_addr_dicom = [str(addr.tag).replace(', ', '').replace(
            ')', '').replace('(', '').upper() for addr in list_tag_dicom]


    # Verify the value of all required DICOM field
    for addr in list_addr_dicom:
        if (addr) in list_usefull_tags:
            assert test_examen.list_dicom[0][addr].value == ds_test[addr].value

    # Test for wrong AET title
    tmp_aet_title = test_examen.aet_title
    test_examen = medical_exam(client_id, path_to_json, path_white_list, path_to_dicom_csv, debug)
    tmp_aet_title = test_examen.aet_title
    test_examen.aet_title = b"BAD_AET"

    scp = move_scp(stored_dicom)
    time.sleep(0.2)
    test_examen.c_move_query_study_uid()
    scp.shutdown()

    assert test_examen.c_move_status == 43009

    test_examen.aet_title = tmp_aet_title
    #  Test for wrong Study_UID
    test_examen.study_uid_to_query = "12.123456789456"
    scp = move_scp(stored_dicom)
    time.sleep(0.2)
    test_examen.c_move_query_study_uid()
    scp.shutdown()

    assert test_examen.c_move_status ==  50451


@pytest.mark.main_unit
def test_dicom_image_corrupted_filter():
    """Test for rejection of corrupted image field:
    can open pixel array parameter"""

    path_to_json = "extractor.json"
    client_id = "unit_test"
    path_white_list = "dicom_white_list.csv"
    path_to_dicom_csv = "pacs_list/dicom_imported_an_x3.csv"
    debug = False
    path_to_json = "extractor.json"

    test_exam = medical_exam(client_id, path_to_json, path_white_list, path_to_dicom_csv, debug)

    file_path = "./data_test/test_mono_cr.dcm"
    ds_test = dcmread(file_path)
    file_path = "./data_test/test_cr.dcm"
    ds_test_2 = dcmread(file_path)
    # Break the DICOM image format
    ds_test[0x7FE0, 0x0010].value = ds_test_2[0x7FE0, 0x0010].value

    # DICOM correct image
    test_exam.list_dicom.append(ds_test_2)
    # DICOM with corrupted image
    test_exam.list_dicom.append(ds_test)

    test_exam.dicom_image_corrupted_filter()

    assert  test_exam.list_dicom[0] == ds_test_2
    assert len(test_exam.list_dicom) == 1
    assert test_exam.study_status_corrupted == 1


@pytest.mark.main_unit
def test_dicom_modality_filter():
    """Test for rejection of uneccesary modality and BodyPartExamined = REPORT"""

    stored_dicom = "/home/zenbook/Documents/code/python/mide/data_test/1.3.6.1.4.1.14519.5.2.1.7777.9002.154181272448537806873380883469"
    ds_test = dcmread(stored_dicom)

    path_to_json = "extractor.json"
    client_id = "unit_test"
    path_white_list = "dicom_white_list.csv"
    path_to_dicom_csv = "pacs_list/dicom_imported_an_x3.csv"
    debug = False
    path_to_json = "extractor.json"

    test_exam = medical_exam(client_id, path_to_json, path_white_list, path_to_dicom_csv, debug)

    # DICOM with accepted modality
    ds_test.Modality = "DX"
    test_exam.list_dicom.append(ds_test)
    # DICOM with unaccepted modality
    ds_test_2 = copy.deepcopy(ds_test)
    ds_test_2.Modality = "ECG"
    test_exam.list_dicom.append(ds_test_2)

    ds_test_3 = copy.deepcopy(ds_test)
    ds_test_3.BodyPartExamined = "REPORT"
    test_exam.list_dicom.append(ds_test_3)

    test_exam.dicom_modality_filter()
    assert  test_exam.list_dicom[0] == ds_test
    assert len(test_exam.list_dicom) == 1
    assert test_exam.study_status_total_w_modality == 2


@pytest.mark.main_unit
def test_dicom_normalization():
    """Test with a functitonnal DICOM => No modification
        Test with a compressed DICOM"""

    stored_dicom = "data_test/test_dx.dcm"
    ds_test = dcmread(stored_dicom)

    path_to_json = "extractor.json"
    client_id = "unit_test"
    path_white_list = "dicom_white_list.csv"
    path_to_dicom_csv = "pacs_list/dicom_imported_an_x3.csv"
    debug = False
    path_to_json = "extractor.json"

    test_exam = medical_exam(client_id, path_to_json, path_white_list, path_to_dicom_csv, debug)
    test_exam.ds_dicom = ds_test

    test_exam.conform_dicom_to_pydicom()

    # TransferSyntaxUID = 1.2.840.10008.1.2
    input_dicom = test_exam.ds_dicom

    test_exam.dicom_normalization()

    output_dicom = test_exam.ds_dicom

    # test for TransferSyntaxUID
    assert output_dicom.file_meta.TransferSyntaxUID == "1.2.840.10008.1.2.1"
    # Test for little endian
    assert output_dicom.is_little_endian == True
    # Test for explicite VR
    assert output_dicom.is_implicit_VR == False


    # TransferSyntaxUID = 1.2.840.10008.1.2.1 => no modification
    test_exam.ds_dicom.file_meta.TransferSyntaxUID = "1.2.840.10008.1.2.1"
    input_dicom = test_exam.ds_dicom

    test_exam.dicom_normalization()

    assert test_exam.ds_dicom == input_dicom


# TODO failled function
@pytest.mark.main_unit
def test_dicom_tag_prefiltering():


    pass
    """Verify that only listined tags are in the DICOM"""
 
    stored_dicom = "./data_test/test_mono_cr.dcm"
    ds_test = dcmread(stored_dicom)

    path_to_json = "extractor.json"
    client_id = "unit_test"
    path_white_list = "dicom_white_list.csv"
    path_to_dicom_csv = "pacs_list/dicom_imported_an_x3.csv"
    debug = False
    path_to_json = "extractor.json"
    test_exam = medical_exam(client_id, path_to_json, path_white_list, path_to_dicom_csv, debug)
    test_exam.list_dicom = [ds_test]
    list_tag_dicom = list(ds_test)

    # Get input tags
    list_input_tag = [str(addr.tag).replace(', ', '').replace(
            ')', '').replace('(', '').upper() for addr in list_tag_dicom]
    tuple_input_tags = tuple(list_input_tag)
    df_white_list = pd.read_csv(path_white_list, usecols=["tag"])
    list_to_keep = df_white_list["tag"].to_list()
    list_to_keep += ["00080016", "00080018", "0020000D", "0020000E", 
                    "00200011", "00200013", "0020000D"]
    set_to_keep = set(list_to_keep)

    test_exam.dicom_tag_prefiltering()

    # Get output tags
    list_tag_dicom = list(test_exam.list_dicom[0])
    list_output_tag = [str(addr.tag).replace(', ', '').replace(
            ')', '').replace('(', '').upper() for addr in list_tag_dicom]
    set_output_tag = set(list_output_tag)

    # Only necessary tags have to remain
    assert (set_to_keep.union(set_output_tag)) == set_to_keep


@pytest.mark.main_unit
def test_dicom_to_png():
    """Test output image type and shape with DX, CT and MRI DICOM"""

    path_dicom = "data_test/test_dx.dcm"
    ds_test_dx = dcmread(path_dicom)
    path_dicom = "data_test/test_ct.dcm"
    ds_test_ct = dcmread(path_dicom)
    path_dicom = "data_test/test_mri.dcm"
    ds_test_mri = dcmread(path_dicom)

    path_to_json = "extractor.json"
    client_id = "unit_test"
    path_white_list = "dicom_white_list.csv"
    path_to_dicom_csv = "pacs_list/dicom_imported_an_x3.csv"
    debug = False
    path_to_json = "extractor.json"

    test_exam = medical_exam(client_id, path_to_json, path_white_list, path_to_dicom_csv, debug)

    # Test DICOM DX
    test_exam.ds_dicom = ds_test_dx
    test_exam.dicom_to_png()
    assert isinstance(test_exam.png_image, np.ndarray)
    assert test_exam.png_image.shape == (1656, 1005, 3)

    # Test DICOM CT
    test_exam.ds_dicom = ds_test_ct
    test_exam.dicom_to_png()
    assert isinstance(test_exam.png_image, np.ndarray)
    assert test_exam.png_image.shape == (512, 512, 3)

    # Test MRI DICOM
    test_exam.ds_dicom = ds_test_mri
    test_exam.dicom_to_png()
    print(type(test_exam.png_image))
    print(test_exam.png_image.shape)
    assert isinstance(test_exam.png_image, np.ndarray)
    assert test_exam.png_image.shape == (256, 256, 3)


@pytest.mark.main_unit
def test_image_prefiltering():
    """Test output image type and shape with DX, CT and MRI DICOM
    Use dicom_to_png function"""

    path_dicom = "data_test/test_dx.dcm"
    ds_test_dx = dcmread(path_dicom)
    path_dicom = "data_test/test_ct.dcm"
    ds_test_ct = dcmread(path_dicom)
    path_dicom = "data_test/test_mri.dcm"
    ds_test_mri = dcmread(path_dicom)

    path_to_json = "extractor.json"
    client_id = "unit_test"
    path_white_list = "dicom_white_list.csv"
    path_to_dicom_csv = "pacs_list/dicom_imported_an_x3.csv"
    debug = False
    path_to_json = "extractor.json"

    test_exam = medical_exam(client_id, path_to_json, path_white_list, path_to_dicom_csv, debug)

    # Test DICOM DX
    test_exam.ds_dicom = ds_test_dx
    test_exam.dicom_to_png()
    test_exam.image_prefiltering()

    assert isinstance(test_exam.png_image, np.ndarray)
    assert test_exam.png_image.shape == (1656, 1005, 3)

    # Test DICOM CT
    test_exam.ds_dicom = ds_test_ct
    test_exam.dicom_to_png()
    test_exam.image_prefiltering()
    assert isinstance(test_exam.png_image, np.ndarray)
    assert test_exam.png_image.shape == (512, 512, 3)

    # Test MRI DICOM
    test_exam.ds_dicom = ds_test_mri
    test_exam.dicom_to_png()
    test_exam.image_prefiltering()
    assert isinstance(test_exam.png_image, np.ndarray)
    assert test_exam.png_image.shape == (256, 256, 3)


@pytest.mark.main_unit
def test_image_thresholding():
    """Test output image type and shape with DX, CT and MRI DICOM
    Use dicom_to_png function"""

    path_dicom = "data_test/test_dx.dcm"
    ds_test_dx = dcmread(path_dicom)
    path_dicom = "data_test/test_ct.dcm"
    ds_test_ct = dcmread(path_dicom)
    path_dicom = "data_test/test_mri.dcm"
    ds_test_mri = dcmread(path_dicom)

    path_to_json = "extractor.json"
    client_id = "unit_test"
    path_white_list = "dicom_white_list.csv"
    path_to_dicom_csv = "pacs_list/dicom_imported_an_x3.csv"
    debug = False
    path_to_json = "extractor.json"

    test_exam = medical_exam(client_id, path_to_json, path_white_list, path_to_dicom_csv, debug)

    # Test DICOM DX
    test_exam.ds_dicom = ds_test_dx
    test_exam.dicom_to_png()
    test_exam.prefilters_to_apply = ["grayscale"]
    test_exam.image_prefiltering()
    test_exam.image_thresholding()
    assert isinstance(test_exam.png_image, np.ndarray)
    assert test_exam.png_image.shape == (1656, 1005)

    # Test DICOM CT
    test_exam.ds_dicom = ds_test_ct
    test_exam.dicom_to_png()
    test_exam.image_prefiltering()
    test_exam.image_thresholding()
    assert isinstance(test_exam.png_image, np.ndarray)
    assert test_exam.png_image.shape == (512, 512)

    # Test MRI DICOM
    test_exam.ds_dicom = ds_test_mri
    test_exam.dicom_to_png()
    test_exam.image_prefiltering()
    test_exam.image_thresholding()
    assert isinstance(test_exam.png_image, np.ndarray)
    assert test_exam.png_image.shape == (256, 256)


@pytest.mark.main_unit
def test_get_background_color():
    """Test the result value"""

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

    test_exam.get_background_color()

    assert test_exam.image_background_color == 0


@pytest.mark.main_unit
def test_ocr_processing():
    """Test the correct word detection
    => requiere other functions"""

    path_dicom = "data_test/test_dx.dcm"
    ds_test_dx = dcmread(path_dicom)

    path_to_png = "data_test/test_png_on_bone_blur.png"
    png_image = imageio.v2.imread(path_to_png)

    path_to_json = "extractor.json"
    client_id = "unit_test"
    path_white_list = "dicom_white_list.csv"
    path_to_dicom_csv = "pacs_list/dicom_imported_an_x3.csv"
    debug = False
    path_to_json = "extractor.json"

    test_exam = medical_exam(client_id, path_to_json, path_white_list, path_to_dicom_csv, debug)

    test_exam.ds_dicom = ds_test_dx
    test_exam.png_image = png_image

    # Image prefiltering
    test_exam.prefilters_to_apply = ["grayscale"]
    test_exam.image_prefiltering()
    test_exam.image_thresholding()
    test_exam.prefilters_to_apply = ["clahe", "gaussian_blur"]
    test_exam.image_prefiltering()
    # detect word in image
    test_exam.ocr_processing()
    # filter word
    test_exam.ocr_postfiltering()

    assert test_exam.list_blanked_word[0] == "gendo"
    assert test_exam.list_blanked_word[1] == "ikari"


@pytest.mark.main_unit
def test_ocr_postfiltering():
    """Test OCR dataframe filtering:
    Normal name to erase
    Word in the of the image are not blanked 
    Word with low confidence level are not blanked
    Smal blanking are not done
    Small word are not blanked
    White listed word are not blanked
     """

    path_dicom = "data_test/test_dx.dcm"
    ds_test_dx = dcmread(path_dicom)
    path_to_png = "data_test/test_png_on_bone_blur.png"
    png_image = imageio.v2.imread(path_to_png)

    path_to_json = "extractor.json"
    client_id = "unit_test"
    path_white_list = "dicom_white_list.csv"
    path_to_dicom_csv = "pacs_list/dicom_imported_an_x3.csv"
    debug = False
    path_to_json = "extractor.json"

    test_exam = medical_exam(client_id, path_to_json, path_white_list, path_to_dicom_csv, debug)

    test_exam.ds_dicom = ds_test_dx
    test_exam.png_image = png_image

    df_ocr_test = pd.DataFrame([{"level":5, "page_num":1, "block_num":2, "par_num":1, 
                    "line_num": 1, "word_num": 1, "left": 475, "top": 1607, "width": 128, 
                    "height": 32, "conf": 92, "text": "asuka"}])

    # Normal name to erase
    test_exam.df_ocr = df_ocr_test
    test_exam.ocr_postfiltering()
    assert test_exam.list_blanked_word[0] == "asuka"

    # Test: Word in the of the image are not blanked 
    test_exam.df_ocr["top"] = test_exam.png_image.shape[0] // 2
    test_exam.ocr_postfiltering()
    assert len(test_exam.list_blanked_word) == 0
    test_exam.df_ocr = df_ocr_test

    # Word with low confidence level are not blanked
    test_exam.df_ocr["conf"] = -5
    test_exam.ocr_postfiltering()
    assert len(test_exam.list_blanked_word) == 0
    test_exam.df_ocr = df_ocr_test

    # Smal blanking are not done
    test_exam.df_ocr["width"] = 2
    test_exam.ocr_postfiltering()
    assert len(test_exam.list_blanked_word) == 0
    test_exam.df_ocr = df_ocr_test

    # Small word are not blanked
    test_exam.df_ocr["text"] = "j"
    test_exam.ocr_postfiltering()
    assert len(test_exam.list_blanked_word) == 0


    # White listed word are not blanked
    test_exam.df_ocr["text"] = "externe"
    assert len(test_exam.list_blanked_word) == 0


@pytest.mark.main_unit
def test_image_blanking():
    """Based on df_ocr coordinate, verify the blanking area mean value
    """

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

    df_ocr_test = pd.DataFrame([{"level":5, "page_num":1, "block_num":2, "par_num":1, 
                    "line_num": 1, "word_num": 1, "left": 475, "top": 800, "width": 150, 
                    "height": 50, "conf": 92, "text": "asuka"}])
    test_exam.df_ocr = df_ocr_test

    test_exam.image_background_color = 225

    # blank sensible data on image
    test_exam.image_blanking()
    pixel_array = test_exam.ds_dicom.pixel_array
    x = int(test_exam.df_ocr["left"].iloc[0])
    y = int(test_exam.df_ocr["top"].iloc[0])
    w = int(test_exam.df_ocr["width"].iloc[0])
    h = int(test_exam.df_ocr["height"].iloc[0])

    assert int(pixel_array[y:y+h, x:x+w].mean()) == test_exam.image_background_color


@pytest.mark.main_unit
def test_patient_birth_date_deidentification():
    """Verifiy patient age is rounded to the lower 5 years"""

    stored_dicom = "/home/zenbook/Documents/code/python/mide/data_test/1.3.6.1.4.1.14519.5.2.1.7777.9002.154181272448537806873380883469"
    path_to_json = "extractor.json"
    client_id = "unit_test"
    path_white_list = "dicom_white_list.csv"
    path_to_dicom_csv = "pacs_list/dicom_imported_an_x3.csv"
    debug = False
    path_to_json = "extractor.json"

    test_exam = medical_exam(client_id, path_to_json, path_white_list, path_to_dicom_csv, debug)
    
    # normal birth_date
    test_exam.ds_dicom = dcmread(stored_dicom)
    test_exam.ds_dicom.add_new([0x0010, 0x0030], "DA", "19940101")

    
    # test_exam.list_dicom = [ds_test, ds_test_2, ds_test_3, ds_test_4, ds_test_5]
    test_exam.patient_birth_date_deidentification()
    assert test_exam.ds_dicom[0x0010, 0x0030].value == "19900000"
    
    test_exam.ds_dicom.add_new([0x0010, 0x0030], "DA", "20210625")
    test_exam.patient_birth_date_deidentification()    
    assert test_exam.ds_dicom[0x0010, 0x0030].value == "20200000"
    
    # No birth_date
    del test_exam.ds_dicom[0x0010, 0x0030]
    test_exam.patient_birth_date_deidentification()    
    assert "PatientBirthDate" not in test_exam.ds_dicom

    # unmatch lengh
    test_exam.ds_dicom.add_new([0x0010, 0x0030], "DA", "2028december23")
    test_exam.patient_birth_date_deidentification()
    assert test_exam.ds_dicom[0x0010, 0x0030].value == "00000000"

    # unmatch type
    test_exam.ds_dicom.add_new([0x0010, 0x0030], "DA", 20221119)
    test_exam.patient_birth_date_deidentification()
    assert test_exam.ds_dicom[0x0010, 0x0030].value == "00000000"


@pytest.mark.main_unit
def test_study_date_deidentification():
    """test for type, lengh and correct deindentification of the study date"""
    
    stored_dicom = "/home/zenbook/Documents/code/python/mide/data_test/1.3.6.1.4.1.14519.5.2.1.7777.9002.154181272448537806873380883469"
    path_to_json = "extractor.json"
    client_id = "unit_test"
    path_white_list = "dicom_white_list.csv"
    path_to_dicom_csv = "pacs_list/dicom_imported_an_x3.csv"
    debug = False
    path_to_json = "extractor.json"

    test_exam = medical_exam(client_id, path_to_json, path_white_list, path_to_dicom_csv, debug)
    
    test_exam.ds_dicom = dcmread(stored_dicom)

    # normal study date
    test_exam.ds_dicom.add_new([0x0008, 0x0020], "DA", "20221119")
    test_exam.study_date_deidentification()
    assert test_exam.ds_dicom[0x0008, 0x0020].value == "202211W3"

    test_exam.ds_dicom.add_new([0x0008, 0x0020], "DA", "20221101")
    test_exam.study_date_deidentification()
    assert test_exam.ds_dicom[0x0008, 0x0020].value == "202211W1"

    # unmatch lengh
    test_exam.ds_dicom.add_new([0x0008, 0x0020], "DA", "2022111")
    test_exam.study_date_deidentification()
    assert test_exam.ds_dicom[0x0008, 0x0020].value == "00000000"

    # unmatch type
    test_exam.ds_dicom.add_new([0x0008, 0x0020], "DA", 20221119)
    test_exam.study_date_deidentification()
    assert test_exam.ds_dicom[0x0008, 0x0020].value == "00000000"

    # No date
    del test_exam.ds_dicom[0x0008, 0x0020]
    test_exam.study_date_deidentification()
    assert "PatientBirthDate" in test_exam.ds_dicom


@pytest.mark.main_unit
def test_dicom_tag_blanking():
    """Insure that only white list tag are present.
        Insure that needed sensible tags are set to 0
        Oppose a black list of sensible tag
        """

    stored_dicom = "data_test/tag_test.dcm"
    path_to_json = "extractor.json"
    client_id = "unit_test"
    path_white_list = "dicom_white_list.csv"
    path_to_black_list = "data_test/dicom_black_list.csv"
    path_to_dicom_csv = "pacs_list/dicom_imported_an_x3.csv"
    debug = False
    path_to_json = "extractor.json"
    test_exam = medical_exam(client_id, path_to_json, path_white_list, path_to_dicom_csv, debug)
    
    test_exam.ds_dicom = dcmread(stored_dicom)
    # test_exam.list_dicom = [ds_test]
    list_tag_dicom = list(test_exam.ds_dicom)

    # Get input tags
    df_white_list = pd.read_csv(path_white_list, usecols=["tag"])
    list_to_keep = df_white_list["tag"].to_list()
    set_to_keep = set(list_to_keep)

    test_exam.dicom_tag_blanking()

    # Get output tags
    list_tag_dicom = list(test_exam.ds_dicom)
    list_output_tag = [str(addr.tag).replace(', ', '').replace(
            ')', '').replace('(', '').upper() for addr in list_tag_dicom]
    set_output_tag = set(list_output_tag)

    # Only necessary tags have to remain
    assert (set_to_keep.union(set_output_tag)) == set_to_keep

    # tag set to 0:
    assert test_exam.ds_dicom[0x0010, 0x0020].value == '0000'

    # Test for black listed tag are not in the DICOM:
    df_black_list = pd.read_csv(path_to_black_list, usecols=["tag"])
    list_black = df_black_list["tag"].to_list()
    set_black = set(list_black)

    assert (set_black - set_output_tag)==set_black


@pytest.mark.main_unit
def test_dicom_tag_for_mide():
    """Verifiy the DICOM InstitutionName, StationName, AcquisitionTime"""

    stored_dicom = "data_test/test_dx.dcm"
    path_to_json = "extractor.json"
    client_id = "unit_test"
    path_white_list = "dicom_white_list.csv"
    path_to_dicom_csv = "pacs_list/dicom_imported_an_x3.csv"
    debug = False
    path_to_json = "extractor.json"

    test_exam = medical_exam(client_id, path_to_json, path_white_list, path_to_dicom_csv, debug)
    test_exam.ds_dicom = dcmread(stored_dicom)
    test_exam.query_date = "2022-06-17 11:29:12.708269"
    test_exam.mide_version = "2.1"

    test_exam.dicom_tag_for_mide()

    assert test_exam.ds_dicom[0x0008, 0x0080].value == "unit_test"
    assert test_exam.ds_dicom[0x0008, 0x1010].value == "2.1"
    assert test_exam.ds_dicom[0x0008, 0x0032].value == "2022-06-17 11:29:12.708269"


@pytest.mark.main_unit
def test_store_on_cloud():
    """Test by Sending a dicom file to GCP Cloud bucket
    without faillure. 
    GCP authentification (json) has to be done"""

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

    assert test_exam.status == "cloud_storage_success"


# # Functional test
# @pytest.mark.anonymization_functional
# def test_image_anonymization():
#     """Process a batch of DICOM to check if the sensible data had been correctly erazed
#         input:  Batch of DICOM
#                 file with the sensible and it's geomtric position (.csv)
#         output: test for less than 5% failure
#                 parameter report file for case analysis(.csv) """
                
#     # Initialization

#     # anonimization ratio
#     anonymization_ratio = 0.6 # ex: 0.6 => 40% of sensible data have to be deleted
    
#     path_to_folder = "data_test/anonym_batch"
#     path_to_white_list = "dicom_white_list.csv"
#     path_to_dicom_batch = "data_test/anonym_batch.csv"
#     # batch_name = "batch_unittest"
#     client_id = "client_unittest"
#     report_date = "01-01-2021"
#     # Read batch csv
#     df_batch =  pd.read_csv(path_to_dicom_batch)

#     # Initialize csv tracker
#     df_batch_tracker = pd.DataFrame(
#             columns=["file_name", "x", "y", "w", "h", "box_t0_mean", "box_mean_t1", "ratio","erased","word_to_blank"])
#     df_batch_tracker.set_index("file_name", inplace=True)
#     df_batch_tracker.to_csv("batch_tracker.csv", header=True)

#     df_white_list = pd.read_csv(path_to_white_list, usecols=["tag"])
    
#     total_batch = df_batch.shape[0]

#     for batch_ptr in range(total_batch):

#         fail_counter = 0
#         # Set eraze flag to Flase
#         ser_batch = df_batch.iloc[batch_ptr].copy()
#         ser_batch["erased"] = "False"

#         # Open DICOM
#         path = pathlib.Path(path_to_folder, ser_batch["file_name"])
#         ds_dicom = dcmread(path)



#         # Set Region Of Interrest geometry
#         x = ser_batch["x"]
#         y = ser_batch["y"]
#         w = ser_batch["w"]
#         h = ser_batch["h"]

#         # get ROI mean value after blanking
#         box_mean_t0 = np.mean(ds_dicom.pixel_array[y:y+h, x:x+w])


#         # call main anonymization function
#         ds_dicom, list_anonym_tracker_tmp, image_filtered, image_png, batch_name = main_anonymization(
#             path, df_white_list, client_id, report_date)


#         # get ROI mean value after blanking
#         box_mean_t1 = np.mean(ds_dicom.pixel_array[y:y+h, x:x+w])

#         # ROI consider to be erazed IF output ROI less than ratio
#         if box_mean_t1 < box_mean_t0 * anonymization_ratio:
#             ser_batch["erased"] = True
#         else:
#             fail_counter += 1

#         # Write the csv tacker 
#         df_batch_tracker = pd.DataFrame({"file_name": [ser_batch.at["file_name"]],
#                                 "x": [ser_batch.at["x"]],
#                                 "y": [ser_batch.at["y"]],
#                                 "w": [ser_batch.at["w"]],
#                                 "h": [ser_batch.at["h"]],
#                                 "box_t0_mean": box_mean_t0,
#                                 "box_mean_t1": box_mean_t1,
#                                 "blanck_ratio": round(box_mean_t1/box_mean_t0, 4),
#                                 "erased": [ser_batch.at["erased"]],
#                                 "word_to_blank": ser_batch.at["word_to_blank"]})
#         df_batch_tracker.set_index("file_name", inplace=True)
#         df_batch_tracker.to_csv("batch_tracker.csv", mode="a", header=False, index=True)


        
#         # # uncomment to get output DICOM and values
#         # path_to_save = "tmp_dicom"
#         # path_to_save = pathlib.Path(path_to_save, ser_batch["file_name"])
#         # print(path_to_save)
#         # ds_dicom.save_as(path_to_save)
#         # print(f"box t0 mean: {box_mean_t0}")
#         # print(f"box t mean: {box_mean_t1}")

#     assert fail_counter/total_batch < 0.2