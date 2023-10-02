


# open DICOM file as a readable output
dcmdump "/home/zenbook/Documents/code/python/theory/dicom/data/cancer_dicom/ID_0003_AGE_0075_CONTRAST_1_CT.dcm" 

# print only study instance uid 
dcmdump "/home/zenbook/Documents/code/python/theory/dicom/data/cancer_dicom/ID_0003_AGE_0075_CONTRAST_1_CT.dcm" +P "0020,000d"