

# echo Orthanc
echoscu -ll debug -aet mydevice -aec ORTHANC localhost 4242


# send dicom file to PASC (ORTHANC)
storescu localhost 4242 "/home/zenbook/Documents/code/python/dicom/data/cancer_dicom/ID_0004_AGE_0056_CONTRAST_1_CT.dcm" -aec ORTHANC -ll info
storescu localhost 4242 "/home/zenbook/Documents/code/python/dicom/data/ca2f3d21af8e47e50f654dea3fc8105c2bdcb97077ba4d42458f9c5a9cd7b352" -aec ORTHANC -ll info

# store to VM PACS
storescu -ll info -aec ORTHANC 192.168.1.2 4242 "/home/zenbook/Documents/code/python/dicom/data/cancer_dicom/ID_0004_AGE_0056_CONTRAST_1_CT.dcm"

dcmsend -v -ll info -aec ORTHANC localhost 4242 --scan-directories --recurse "/home/zenbook/Documents/code/python/dicom/data/ca2f3d21af8e47e50f654dea3fc8105c2bdcb97077ba4d42458f9c5a9cd7b352"


storescu -ll info -aec ORTHANC 192.168.1.100 4242 "/home/zenbook/Documents/gleamer/venv_exporter/glm-export-data/tmp_dicom/1.3.76.6.1.2.5.2.5888.4.44289039866118638.dcm"
