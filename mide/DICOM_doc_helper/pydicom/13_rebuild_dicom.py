#! /usr/bin/env python3
# coding = utf-8


from pydicom import dcmread
import os
import random

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


input_folder = "/home/zenbook/Documents/code/python/dicom/data/to_fixe"
path_to_save =  "/home/zenbook/Documents/Gleamer/glm-export-data/raw_data/data/pacs/clean"

patient_id = 1000


list_path = path_to_dicom(input_folder)

total_dicom = len(list_path)

dicom_counter = 0

# for path in list_path:

for subdir, dirs, files in os.walk(input_folder):

    for folder in dirs:
        count = 1
        UID = "1.1" + "." + str(random.randint(0, 999)) + "." + str(random.randint(0, 999)) + "." + str(
            random.randint(0, 999)) + str(random.randint(0, 999)) + "." + str(random.randint(0, 999))
        patient_id += 1
        for subdir_2, dirs_2, files_2 in os.walk(subdir + os.sep + folder):
            print(subdir_2)
            for filename in files_2:

                filepath = subdir_2 + os.sep + filename
                if filename.endswith('.dcm'):
                    StudyInstanceUID = UID
                    SeriesInstanceUID = UID + ".1"
                    SOPInstanceUID = UID + ".1." + str(count)
                    count = count + 1

                    data_set = dcmread(filepath)

                    file_name = os.path.basename(filepath)
                    file_path = path_to_save + "/" + file_name.split(".")[0] + ".dcm"

                    # PatientId (0010,0020)
                    data_set.add_new([0x0010, 0x0020], "LO", str(patient_id))

                    # StudyInstanceUID (0020,000D)
                    data_set.add_new([0x0020, 0x000D], "UI", str(StudyInstanceUID))

                    # SerieInstanceUID (0020,000E)
                    data_set.add_new([0x0020, 0x000E], "UI", str(SeriesInstanceUID))

                    # SOPInstanceUID (0008,0018)
                    data_set.add_new([0x0008, 0x0018], "UI", str(SOPInstanceUID))


                    dicom_counter += 1
                    print(f"File {dicom_counter}/{total_dicom} DICOM fixed")

                    data_set.save_as(file_path, write_like_original=True)


