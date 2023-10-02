

# Installation

sudo apt update
sudo apt install orthanc
sudo apt install orthanc-dicomweb
sudo apt install orthanc-gdcm
sudo apt install orthanc-imagej
sudo apt install orthanc-mysql
sudo apt install orthanc-postgresql
sudo apt install orthanc-python
sudo apt install orthanc-webviewer
sudo apt install orthanc-wsi

# Starting/Stopping the service
sudo service orthanc start
sudo service orthanc stop
sudo service orthanc restart


# Accessing the logs
# Logs are available in 
/var/log/orthanc/


# Configuration
# Orthanc reads its configuration file from the 
/etc/orthanc/

#edit orthanc.json:
sudo nano orthanc.json


#   // The DICOM Application Entity Title
    # "DicomAet" : "ORTHANC",

#   // The DICOM port
#   "DicomPort" : 4242,


#   // The list of the known DICOM modalities
# example: DEVICE modality on loopback adresse (127.0.0.0)
"DicomModalities" : {
    "DEVICE" : [ "DEVICE", "127.0.0.0", 104 ]
},


# Opening Orthanc Explorer
# The most straightforward way to use Orthanc consists in opening Orthanc Explorer, 
# the embedded administrative interface of Orthanc, with a Web browser. Once Orthanc is running, open the following URL: 
# http://localhost:8042/app/explorer.html

# start orthanc with trace log
sudo /etc/init.d/orthanc start
sudo /etc/init.d/orthanc start --trace --logfile=orthanc.log