#! /usr/bin/env python3
# coding = utf-8

from pydicom.dataset import Dataset
from pynetdicom import AE, debug_logger
from pydicom import dcmread




path = "/home/zenbook/Documents/gleamer/venv_exporter/glm-export-data/raw_data/data/pacs/default_dicom/unknown_vr/DX.1.2.392.200046.100.14.181422110893939961618913563530073464142"
path_2 = "/home/zenbook/Documents/code/python/dicom/output/1.3.12.2.1107.5.3.33.7534.11.202005301443480920.dcm"

output = "/home/zenbook/Documents/code/python/dicom/output"


ds = dcmread(path_2)


try:
    ds.pixel_array 
    print(ds.pixel_array)
except:
    print("can't open pixel array")


# if ds.Modality not in list_modality:
print(ds.Modality)




# dicom_after_filter = len(path_to_dicom("tmp_dicom"))

# # IF no more DICOM => contained only bad DICOM
# if dicom_after_filter == 0:
#     deleted_status = f"all_deleted: corrupted:{corrupted_dicom} modality:{wrong_modality} fract:{fract}"
#     print(deleted_status)
#     ser_log.at["status"] = deleted_status

#     glm_instance_id = "not_processed"
#     # build and write the exporter log
#     exporter_log(ser_log, glm_study_id, glm_instance_id, path_save_anonymized, output_folder)
#     flag_dicom = 1
#     return ser_log, flag_dicom   
# # IF DICOM had been deleted
# elif dicom_after_filter < dicom_before_filter:
#     deleted_status = f"Some_deleted: corrupted:{corrupted_dicom} modality:{wrong_modality} fract:{fract}"
#     print(deleted_status)
#     ser_log.at["status"] = deleted_status
#     flag_dicom = 0
#     return ser_log, flag_dicom
# # else:
# #     flag_dicom = 0
# print(f" {study_instance_uid}: All {dicom_after_filter} images will be processed")