#! /usr/bin/env python3
# coding = utf-8


# The DICOMDIR file is used to summarize the contents of the File-set, 
# and is a Media Storage Directory instance that follows the Basic Directory Information Object Definition (IOD).


from pydicom import dcmread
from pydicom.data import get_testdata_file


path = get_testdata_file("DICOMDIR")
ds = dcmread(path)

print("Media Storage SOP Class UID name:")
print(ds.file_meta.MediaStorageSOPClassUID.name)


# Here we have a 'PATIENT' record, 
# which from Table F.5-1 we see must also contain Patient’s Name and Patient ID elements. 
# http://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_F.4.html#table_F.4-1
print("\nDirectory Record Sequence (0004,1220):")
print(ds.DirectoryRecordSequence[0])
