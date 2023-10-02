# reccup modalité SH pour une date

* C-Echo:
```
echoscu -v -aet <GLM_AET> -aec ${PACS_AET} ${PACS_IP} ${PACS_PORT}
``` 
# * C-Find at image level:
```
findscu -v -S -k QueryRetrieveLevel=IMAGE -aet ${GLM_AET} -aec ${PACS_AET} ${PACS_IP} ${PACS_PORT} -k StudyInstanceUID="<studyInstanceUID>"
```
# * C-Find at series level: 
```
findscu -v -S -k QueryRetrieveLevel=SERIES -aet ${GLM_AET} -aec ${PACS_AET} ${PACS_IP} ${PACS_PORT} -k StudyInstanceUID="<studyInstanceUID>"
```
# * C-Find at study level:
```
findscu -v -S -k QueryRetrieveLevel=STUDY -aet moi -aec ORTHANC localhost 4242 -k StudyInstanceUID

# -k + nom du champ => afficher reponse
# -k + nom du champ=xxx => bonne study
#study instance UID 123 + list accession number
-k StudyInstanceUID=123 -k AccessionNumber 

findscu -v -S -k QueryRetrieveLevel=STUDY -aet moi -aec ORTHANC localhost 4242 -k AccessionNumber="2819497684894126"
findscu -v -S -k QueryRetrieveLevel=STUDY -aet ${GLM_AET} -aec ${PACS_AET} ${PACS_IP} ${PACS_PORT} -k StudyInstanceUID="<studyInstanceUID>"
```
To find study by modality add ```-k Modality=<modality>``` (CR or DX for example).
To find study by date add ```-k StudyDate=<date>``` (specific day YYYYMMDD or range YYYYMMDD-YYYYMMDD)
# * C-Move (This command performs an image copy (no images will be deleted from the SCP)):
```
movescu -v -S -k QueryRetrieveLevel=STUDY -aet ${GLM_AET} -aem ${GLM_AET} -aec ${PACS_AET} ${PACS_IP} ${PACS_PORT} -k StudyInstanceUID="<studyInstanceUID>"
```
# * C-Store:
```
storescu -aet ${GLM_AET} -aec ${PACS_AET} ${PACS_IP} ${PACS_PORT} <dicom_file>