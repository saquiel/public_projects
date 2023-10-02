

"aet_title": "GLM-EXPORT",
"aet_ip": "127.0.0.1",
"aet_port": 10400,
"aec_title": "DIAM4",
"aec_ip" : "192.168.1.110",
"aec_port": 104,
"output_folder": ["output"]

echoscu -ll debug -aet GLM-EXPORT -aec DIAM4 192.168.1.110 104


A10016187068
1.2.826.0.1.3680043.2.406.1.2.4056875177.120288.1626166568.10

# FIND SCU
findscu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aec DIAM4 192.168.1.110 104 -k StudyInstanceUID="2.16.840.1.113669.632.20.1524706616.537038478.10000108002"
findscu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aec DIAM4 192.168.1.110 104 -k AccessionNumber="A10016187068"

# C MOVE
storescp --debug +B +xa -dhl -uf -aet GLM-EXPORT -od output 1104
movescu --debug -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 192.168.1.110 104 -k StudyInstanceUID="2.16.840.1.113669.632.20.1524706616.537038478.10000108002" 
movescu --debug -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 192.168.1.110 104 -k AccessionNumber="A10016187068"

# IM2P
1.2.826.0.1.3680043.2.406.33.1.2162074.2.210331173403
movescu --debug -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k StudyInstanceUID="1.2.826.0.1.3680043.2.406.33.1.2160964.1.210331094025" 
movescu --debug -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k StudyInstanceUID="1.2.826.0.1.3680043.2.406.33.1.2162074.2.210331173403" 


33.2179035
findscu -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k AccessionNumber="33.2179035"
movescu --debug -v -S -k QueryRetrieveLevel=STUDY -aet GLM-EXPORT -aem GLM-EXPORT -aec DIAM4 10.40.30.101 104 -k AccessionNumber="33.2179035"


            "aet_title": "GLM-EXPORT",
            "aet_ip": "127.0.0.1",
            "aet_port": 1104,
            "aec_title": "DIAM4",
            "aec_ip" : "10.40.30.101",
            "aec_port": 104,
            "output_folder": ["output"]