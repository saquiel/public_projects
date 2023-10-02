echoscu localhost 4242 -ll debug -aec ORTHANC


# Find SCU on ORTHANC LOCAL
# findscu [options] peer port [dcmfile-in...]
findscu -v -S -k QueryRetrieveLevel=DICOM_LEVEL -aet MYSELF -aec PACS_NAME PACS_IP PACS_PORT -k StudyInstanceUID="<studyInstanceUID>"
# -v: verbose
# -k: dictionary key (query)
# -S: presentation contexte:
#   -W  --worklist => use modality worklist information model (default)
#   -P  --patient => use patient root information model
#   -S  --study => use study root information model
#   -O  --psonly => use patient/study only information model

# query accession number
findscu -v -S -k QueryRetrieveLevel=STUDY -aet DEVICE -aec ORTHANC localhost 4242 -k AccessionNumber="2819497684894126"

# query on VM PACS
findscu -v -S -k QueryRetrieveLevel=STUDY -aet DEVICE -aec ORTHANC 192.168.1.100 4242 -k AccessionNumber="2531514838096696"



# By DICOM level:

# -k QueryRetrieveLevel=PATIENT
# at patient level
findscu -v -S -k QueryRetrieveLevel=PATIENT -aet DEVICE -aec ORTHANC localhost 4242 -k StudyInstanceUID=StudyInstanceUID="1.3.6.1.4.1.14519.5.2.1.7777.9002.298971292505498901486117442131"

# at study level:
findscu -v -S -k QueryRetrieveLevel=STUDY -aet DEVICE -aec ORTHANC localhost 4242 -k StudyInstanceUID=StudyInstanceUID="1.3.6.1.4.1.14519.5.2.1.7777.9002.298971292505498901486117442131"

# at series level: 
findscu -v -S -k QueryRetrieveLevel=SERIES -aet DEVICE -aec ORTHANC localhost 4242 -k StudyInstanceUID=StudyInstanceUID="1.3.6.1.4.1.14519.5.2.1.7777.9002.298971292505498901486117442131"

# at image level:
findscu -v -S -k QueryRetrieveLevel=IMAGE -aet DEVICE -aec ORTHANC localhost 4242 -k StudyInstanceUID=StudyInstanceUID="1.3.6.1.4.1.14519.5.2.1.7777.9002.298971292505498901486117442131"

# to a distant server: www.dicomserver.co.uk
findscu -S -aec ORTHANC -aet DEVICE www.dicomserver.co.uk 11112 -k QueryRetrieveLevel=STUDY -k StudyDate



# To find study by modality add -k Modality=<modality> (CR or DX for example).
# To find study by date add -k StudyDate=<date>(specific day YYYYMMDD or range YYYYMMDD-YYYYMMDD)


# C-Store:
    # storescu -aet ${GLM_AET} -aec ${PACS_AET} ${PACS_IP} ${PACS_PORT} <dicom_file>
    
# test
findscu -v -S -k QueryRetrieveLevel=IMAGE -aet GLEAMER -aec DIAM4 10.1.118.203 104 -k StudyInstanceUID="CR" -k StudyTime="094826-100426" -k StudyDate="20210825-20210825" -k SOPClassUID -k StudyInstanceUID -k PatientName

movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k StudyInstanceUID="1.2.826.0.1.3680043.2.406.33.1.2167989.1.210407150251"

findscu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k AccessionNumber="33.2167989" -k StudyInstanceUID
# I: (0020,000d) UI [1.2.826.0.1.3680043.2.406.33.1.2167989.1.210407150251 ] #  54, 1 StudyInstanceUID
findscu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k AccessionNumber="33.1527013" -k StudyInstanceUID
# I: (0020,000d) UI [1.2.826.0.1.3680043.2.406.33.1.1526287.1.190606104624 ] #  54, 1 StudyInstanceUID
findscu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k AccessionNumber="33.2179035" -k StudyInstanceUID
# I: (0020,000d) UI [1.2.826.0.1.3680043.2.406.33.1.2179035.1.210416160314 ] #  54, 1 StudyInstanceUID

findscu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k AccessionNumber="33.2176344" -k StudyInstanceUID
# I: (0020,000d) UI [1.2.826.0.1.3680043.2.406.33.1.2176344.1.210414174253 ] #  54, 1 StudyInstanceUID

# no image
33.2181095 => 1.2.826.0.1.3680043.2.406.33.1.2181095.2.210419182427
findscu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k AccessionNumber="33.2181095" -k StudyInstanceUID
1.2.826.0.1.3680043.2.406.33.1.2181095.1.210419174750

33.2180853 => 1.2.826.0.1.3680043.2.406.33.1.2180853.2.210419155907 + 1.2.826.0.1.3680043.2.406.33.1.2180853.1.210419155906
findscu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k AccessionNumber="33.2180853" -k StudyInstanceUID
1.2.826.0.1.3680043.2.406.33.1.2180853.1.210419155906

33.2180632 => 1.2.826.0.1.3680043.2.406.33.1.2180632.1.210419144053 => problem
findscu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k AccessionNumber="33.2180632" -k StudyInstanceUID
1.2.826.0.1.3680043.2.406.33.1.2180632.1.210419144053

33.2176978 => 1.2.826.0.1.3680043.2.406.33.1.2176978.1.210415110148 => problem
findscu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k AccessionNumber="33.2176978" -k StudyInstanceUID
1.2.826.0.1.3680043.2.406.33.1.2176978.1.210415110148


echoscu -ll debug -aet GLM-EXPORT -aec GXD5PARC 192.168.106.183 104

