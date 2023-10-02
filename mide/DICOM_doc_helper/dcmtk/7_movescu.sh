


# C-Move 
# image copy from the SCP:
# movescu -v -S -k QueryRetrieveLevel=STUDY -aet MYSELF -aem MYSELF -aec PACS_NAME PACS_IP PACS_PORT -k StudyInstanceUID="<studyInstanceUID>"

# movescu to vm PACS ORTHANC
# launch storescp service: listen on 10400
storescp +B +xa -dhl -uf -aet DEVICE -od /home/zenbook/Documents/code/python/dicom/dcmtk 10400

movescu -v -S -k QueryRetrieveLevel=STUDY -aet DEVICE -aem DEVICE -aec ORTHANC 192.168.1.100 4242 -k AccessionNumber="2531514838096696"

movescu -v -S -k QueryRetrieveLevel=PATIENT -aet DEVICE -aem DEVICE -aec DICOMSERVER www.dicomserver.co.uk 11112 -k AccessionNumber="123456"

echoscu -ll debug -aet DEVICE -aec DICOMSERVER www.dicomserver.co.uk 11112


storescp +B +xa -dhl -uf -aet DEVICE -od /home/zenbook/Documents/code/python/dicom/dcmtk 10400
movescu -v -S -k QueryRetrieveLevel=STUDY -aet DEVICE -aem DEVICE -aec ORTHANC 192.168.1.100 4242 -k StudyInstanceUID="1.3.6.1.4.1.14519.5.2.1.7777.4012.450770664900019194206481282581"

# IM2P
storescp +B +xa -dhl -uf -aet GLM-EXPORT -od tmp_dicom 1104 -ll info
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k StudyInstanceUID="1.2.826.0.1.3680043.2.406.33.1.2167989.3.210407151928"
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k StudyInstanceUID="1.2.826.0.1.3680043.2.406.33.1.2156725.3.210326142129"
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k StudyInstanceUID="1.2.826.0.1.3680043.2.406.33.1.2149156.2.210319161115"
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k StudyInstanceUID="1.2.826.0.1.3680043.2.406.33.1.2175579.2.210414115730"

movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k StudyInstanceUID="1.2.826.0.1.3680043.2.406.33.1.1521319.1.190601105111"
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k AccessionNumber="33.1521319"


# Find StudyInstanceUID
findscu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k AccessionNumber="A10055481071" -k StudyInstanceUID
# => 1.2.826.0.1.3680043.2.406.33.1.1657004.1.191021081931
# Cmove with the studyUID
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k StudyInstanceUID="1.2.826.0.1.3680043.2.406.33.1.1657004.1.191021081931"
# => DX.1.3.6.1.4.1.19179.1.1027331668225.3.23005.89528
# mail
mail -A DX.1.3.6.1.4.1.19179.1.1027331668225.3.23005.89528 -s "dicom_default" benoit.pont@gleamer.ai

# 33.1838236 => 1.2.826.0.1.3680043.2.406.33.1.1838236.1.200526154023 => CR.1.3.12.2.1107.5.3.33.4191.11.202005261547260562
# + SRd.1.3.12.2.1107.5.3.33.4191.15.20200526154710
# 33.1590868 => 1.2.826.0.1.3680043.2.406.33.1.1590868.1.190819140455 => CR.1.2.392.200036.9125.9.0.487531544.1316622080.2367674633
# 33.1890785 => 1.2.826.0.1.3680043.2.406.33.1.1890785.1.200717100418 => CT.1.2.392.200036.9133.3.1.240203.5.20200717102109600
# CT.1.2.392.200036.9133.3.1.240203.5.20200717102109757
# SC.1.2.826.0.1.3680043.8.676.1.49848.200717101518.1675566.2.1000
# + CR + SC

# 33.1780732 => 1.2.826.0.1.3680043.2.406.33.1.1780732.1.200217084411
findscu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k AccessionNumber="33.1780732" -k StudyInstanceUID
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k StudyInstanceUID="1.2.826.0.1.3680043.2.406.33.1.1780732.1.200217084411"
mail -A CT.1.2.250.1.90.2.3529903314.20200217085445.8780.34.299 -s "dicom_default" benoit.pont@gleamer.ai

findscu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k AccessionNumber="33.1536277" -k StudyInstanceUID
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k StudyInstanceUID="1.2.826.0.1.3680043.2.406.33.1.1536277.1.190617164443"




# no
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k AccessionNumber="33.1526287"
# no
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k AccessionNumber="33.1527013"
# no
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k AccessionNumber="33.1527066"
# no
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k AccessionNumber="33.1532562"
# no
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k AccessionNumber="33.1521935"
# no
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k AccessionNumber="33.1522613"
# no
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k AccessionNumber="33.1524252"

# test 2
# 33.2167989
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k StudyInstanceUID="1.2.826.0.1.3680043.2.406.33.1.2167989.1.210407150251"
# succes => 5 US + 5 DX
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k StudyInstanceUID="1.2.826.0.1.3680043.2.406.33.1.2167989.2.210407150251"
# succes => empty
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k StudyInstanceUID="1.2.826.0.1.3680043.2.406.33.1.2167989.3.210407151928"
# succes => empty
# 33.2156725
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k StudyInstanceUID="1.2.826.0.1.3680043.2.406.33.1.2156725.1.210326142129"
# succes => 3US + 4 SC 
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k StudyInstanceUID="1.2.826.0.1.3680043.2.406.33.1.2156725.2.210326142129"
#  suces empty
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k StudyInstanceUID="1.2.826.0.1.3680043.2.406.33.1.2156725.3.210326142129"
# succes => empty
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k StudyInstanceUID="1.2.826.0.1.3680043.2.406.33.1.2156725.4.210326143329"
# succes => empty

# 33.2149156
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k StudyInstanceUID="1.2.826.0.1.3680043.2.406.33.1.2149156.1.210319155617"
# succes 6 CR
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k StudyInstanceUID="1.2.826.0.1.3680043.2.406.33.1.2149156.2.210319161115"
# succes => empty
# 33.2175579
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k StudyInstanceUID="1.2.826.0.1.3680043.2.406.33.1.2175579.1.210414114414"
# succes 5 CR
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k StudyInstanceUID="1.2.826.0.1.3680043.2.406.33.1.2175579.2.210414115730"
# succes empty







# with image
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k StudyInstanceUID="1.2.826.0.1.3680043.2.406.33.1.2095275.1.210201082120"

# RISF
storescp +B +xa -dhl -uf -aet GLM-EXPORT -od output 10400

movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 192.168.1.110 104 -k StudyInstanceUID="1.2.826.0.1.3680043.2.406.1.2.4056875177.120288.1626166568.10"
# IMPF
storescp +B +xa -dhl -uf -aet GLM-EXPORT -od tmp_dicom 10400
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 172.20.1.205 104 -k StudyInstanceUID="1.2.826.0.1.3680043.2.406.339303.1.7779261.1.210810113717"
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 172.20.1.205 104 -k StudyInstanceUID="1.2.250.1.439.5.7.20210811073337432.1863838845"
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 172.20.1.205 104 -k StudyInstanceUID="DX.1.3.76.6.1.2.5.2.6322.4.44419043699060079"
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 172.20.1.205 104 -k StudyInstanceUID="1.3.76.6.1.2.5.2.5300.4.44419038529023650"
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 172.20.1.205 104 -k StudyInstanceUID="1.2.826.0.1.3680043.2.406.339303.1.7780061.1.210810234359"
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 172.20.1.205 104 -k StudyInstanceUID="339303.6096626"





# RISF
storescp +B +xa -dhl -uf -aet GLM-EXPORT -od output 10400

2.16.840.1.113669.632.20.1524706616.537038478.10000164970,A10027680968
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 192.168.1.110 104 -k StudyInstanceUID="2.16.840.1.113669.632.20.1524706616.537038478.10000164970"

2.16.840.1.113669.632.20.1524706616.537038478.10000168300,A10028499290
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 192.168.1.110 104 -k StudyInstanceUID="2.16.840.1.113669.632.20.1524706616.537038478.10000168300"

2.16.840.1.113669.632.20.1524706616.537038478.10000142386,A10022446226
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 192.168.1.110 104 -k StudyInstanceUID="2.16.840.1.113669.632.20.1524706616.537038478.10000142386"

2.16.840.1.113669.632.20.1524706616.537038478.10000163891,A10027449663
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 192.168.1.110 104 -k StudyInstanceUID="2.16.840.1.113669.632.20.1524706616.537038478.10000163891"

2.16.840.1.113669.632.20.1524706616.537038478.10000127670,A10020080910
2.16.840.1.113669.632.20.1524706616.537038478.10000122563,A10019223168
2.16.840.1.113669.632.20.1524706616.537038478.10000126798,A10019706973
2.16.840.1.113669.632.20.1524706616.537038478.10000135791,A10021008645
2.16.840.1.113669.632.20.1524706616.537038478.10000137284,A10021715927


storescp +B +xa -dhl -uf -aet GLM-EXPORT -od output 10400
findscu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aec DIAM4 192.168.1.110 104 -k AccessionNumber="A10057175158" -k StudyInstanceUID
# => 2.16.840.1.113669.632.20.1524706616.537038478.10000328919
movescu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 192.168.1.110 104 -k StudyInstanceUID="2.16.840.1.113669.632.20.1524706616.537038478.10000328919"
mail -A DX.1.2.392.200046.100.14.181422110893939961618913563530073464142 -s "dicom_default" benoit.pont@gleamer.ai
