# Medical Imaging Data Exporter

This project is an embedded Medical Imaging Data Extractor (MIDE) focused on security and privacy to satisfy the GDPR and the  strategic data grade requirements.
It extracts selected medical image data from the PACS and sends them to a Cloud storage.


## Installation



tesseract alpha Installation:
```bash
sudo add-apt-repository ppa:alex-p/tesseract-ocr-devel
sudo apt-get update
sudo apt install tesseract-ocr
sudo apt install libtesseract-dev
tesseract --version
```

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install dependency.

```bash
pip install pydicom pynetdicom  pandas numpy datetime pathlib opencv-python 

```

Create a GCP bucket:
https://cloud.google.com/storage/docs/reference/libraries?authuser=1#client-libraries-install-python


Initialize the extractor.json with your setting
```python
"unit_test": {
      "aet_title":"DEVICE", # MIDE network name (aet)
      "aet_ip": "127.0.0.1",
      "aet_port": 10400,
      "aec_title": "UNIT_TEST_PACS", # Target PACS name (aec)
      "aec_ip" : "127.0.0.1",
      "aec_port": 11100,
      "output_folder": ["./output"],
      "cloud_storage": "midedicomstorage", # bucket name
      "modality": ["DX","CR", "US", "CT", "MRI"], # modality selected
      "image_modality_anonymisation": ["DX", "CR"], # modality to anonymize
      "delay": 30 # delay between query (15 to 30 seconds for in load PACS)
},
```

Add needed medical words in word_white_list.csv

## Usage

```bash
python3 main.py path/to/dicom/to/import.csv pacs_name_in_json

python3 main.py pacs_list/dicom_imported_an_x3.csv pacs_orthanc

```

## License
[MIT](https://choosealicense.com/licenses/mit/)
```

