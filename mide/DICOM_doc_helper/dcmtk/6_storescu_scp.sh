

# send dicom file to PASC (ORTHANC)
storescu localhost 4242 "/home/zenbook/Documents/code/python/theory/dicom/data/cancer_dicom/ID_0000_AGE_0060_CONTRAST_1_CT.dcm" -aec ORTHANC -ll info




# use the command line tools from the dcmtk toolkit in order to play around with DICOM images, setting up a DICOM recipient and how we integrate TLS (encryption) in the whole setup.

# 1/ on first terminal
# storescp
# launch PACS server: PACS listen on 10400
sudo -E storescp +B +xa -dhl -uf -aet CCH-GLMEXPORT -od output 104


# +B: write data exactly as read. Actually, I use this option as it seems to write directly on disk. On a weaker Raspberry Pi I did have issues with large files until I started to use this option. So: recommended.
# +xa: accept all supported transfer syntaxes. That’s what you expect from a test system.
# -dhl: disable hostname lookup. In our test environment, we do not want to complicate things by using DNS and reverse DNS lookups.
# -uf: generate filename from instance UID (default). This means that you will get files names from the instance UID. They are not exactly “telling” filenames, but they refer to some instance UID that comes from your other test systems or from a worklist or from whereever.
# -aet: set my AE title. This is the AE title, an important identifier in the DICOM world. In reality, this would probably be a name referring to the respective hospital owning the PACS or to the manufacturer of the PACS.
# This is not the standardized port for DICOM operation; in fact, in reality you would use port 104. 

# 2/ on second terminal
# send dicom file: storescu
# storescu [options] peer port dcmfile-in...
storescu -ll info -aec CCH-GLMEXPORT localhost 104 "/home/zenbook/Documents/python/gleamer/cochin/n106.dcm"


storescp +B +xa -dhl -uf -aet DEVICE -od /home/zenbook/Documents/code/python/dicom/output 11112

# IMPF
storescp +B +xa -dhl -uf -aet DEVICE -od tmp_dicom 10400 -ll info


nohup sudo -E storescp +B +xa -dhl -uf -aet CCH-GLMEXPORT -od /mnt/data_a 104 -ll info > log_2021