# C-Echo:
# echoscu -v -aet <GLM_AET> -aec ${PACS_AET} ${PACS_IP} ${PACS_PORT}

# echo Orthanc

# ping
echoscu -v localhost 4242
# ping + details
echoscu -ll debug localhost 4242
# or
echoscu -ll debug 127.0.0.1 4242


# NORMAL PACS: AEC CHECKING ON

# ORPHANC Activate AEC checking (like a noral PACS server)
# /etc/orthanc/orthanc.json

# Change DicomCheckCalledAet to true
  /**
   * Configuration of the DICOM server
   **/

  // Enable the DICOM server. If this parameter is set to "false",
  // Orthanc acts as a pure REST server. It will not be possible to
  // receive files or to do query/retrieve through the DICOM protocol.
  "DicomServerEnabled" : true,

  // The DICOM Application Entity Title
  "DicomAet" : "ORTHANC",

  // Check whether the called AET corresponds to the AET of Orthanc
  // during an incoming DICOM SCU request
  "DicomCheckCalledAet" : true,


echoscu -ll debug localhost 4242  # => NOW WILL fail
# need to add the calling application name:
# Application Entity Calling(AEC):
echoscu -ll debug localhost 4242  -aec ORTHANC

# with a calling name:
# Application Entity Title (AET):
echoscu localhost 4242 -ll debug -aet DEVICE -aec ORTHANC

echoscu -ll debug -aet DEVICE -aec ORTHANC localhost 4242

# echo to vm
echoscu -ll debug -aet DEVICE -aec ORTHANC 192.168.1.3 4242

echoscu -ll debug -aet GLM-EXPORT -aec DIAM4 10.40.30.101 104


echoscu -ll debug -aet DEVICE -aec DEVICE 192.168.1.11 10400


echoscu -ll debug -aet GLM-EXPORT -aec GXD5SUD 10.0.214.216 104

# parc
echoscu -ll debug -aet GLM-EXPORT -aec GXD5PARC 192.168.106.183 104

