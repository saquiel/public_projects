#! /usr/bin/env python3
# coding = utf-8


from pydicom.dataset import Dataset

from pynetdicom import AE, debug_logger
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind, StudyRootQueryRetrieveInformationModelFind

# debug_logger()

ae = AE(ae_title=b'DEVICE')

# Presentation abstract context initialization
# verification SOP class service
# Study Root Query/Retrieve Information Model – FIND
ae.add_requested_context('1.2.840.10008.5.1.4.1.2.1.1')

# Create our Identifier (query) dataset
ds = Dataset()
# Add query retrieve level
ds.QueryRetrieveLevel = 'STUDY'
# add assession number

ds.AccessionNumber="33.2165191"

ds.StudyInstanceUID = "" #please return Study UID


assoc = ae.associate('192.168.1.100', 4242, ae_title=b'ORTHANC')

if assoc.is_established:
    # Send the C-FIND request
    responses = assoc.send_c_find(ds, PatientRootQueryRetrieveInformationModelFind)
    for (status, identifier) in responses:
        if status:
            print(f"C-FIND query status: {status.Status}")
            if identifier:
                study_instance_uid = str(identifier[0x0020, 0x000d].value)
        else:
            print('Connection timed out, was aborted or received invalid response')

    # Release the association
    assoc.release()
else:
    print('Association rejected, aborted or never connected')

print(study_instance_uid)

print(type(study_instance_uid))
# # or
# ae = AE(ae_title=b'DEVICE')

# ae.add_requested_context(StudyRootQueryRetrieveInformationModelFind)
# assoc = ae.associate('192.168.1.100', 4242, ae_title=b'ORTHANC')
# if assoc.is_established:
#     ds = Dataset()
#     ds.QueryRetrieveLevel = 'STUDY'
#     ds.AccessionNumber="33.2176324"
#     ds.StudyInstanceUID = "" #please return Study UID
#     responses = assoc.send_c_find(ds, PatientRootQueryRetrieveInformationModelFind)

#     for (status, identifier) in responses:
#         # If `Pending` status, print response
#         if status and status.Status in [0xff00, 0xff01]:
#             print(identifier)

#     assoc.release()

















# .NET Version
# The method needed is DicomQuery.Find. You can generate a query dataset using the QueryDataSet method and add more query parameters to it.

#  DicomQuery q = new DicomQuery();
#  q.Node = "DicomServer.co.uk";
#  q.Port = 104;
#  q.CallingAE = "scu";
#  q.CalledAE = "DicomServer";

#  q.Root = QueryRoot.Study;
#  q.Level = QueryLevel.STUDY;
            
#  DicomDataSet queryDS = q.QueryDataSet();
#  queryDS.Add(Keyword.AccessionNumber, "12345");
#  queryDS.StudyUID = ""; // please return Study UID

#  DicomDataSetCollection results = q.Find(queryDS);

#  foreach (DicomDataSet result in results)
#  {
# 	string studyUID = result.StudyUID;
# 	// with Study UID obtained, you can either do further C-FIND queries to get Series/Instance UIDs
# 	// or you can go ahead and retrieve the entire Study via C-GET or C-MOVE
#  }
# COM Version
# The method needed is DicomQuery.DoRawQuery, You can generate a default query dataset as a starting point, using the QueryDataSet method, and then add more query parameters to it:

#  Dim q As New DicomQuery
#  q.Node = "DicomServer.co.uk"
#  q.Port = 104
#  q.CallingAE = "scu"
#  q.CalledAE = "DicomServer"

#  q.Root = "STUDY"
#  q.level = "STUDY"

#  Dim queryDS As DicomDataSet
#  Set queryDS = q.QueryDataSet
#  queryDS.Attributes.Add &H8, &H50, "12345" 
#  queryDS.studyUID = "" ' please return STUDY UID
#  Dim results As DicomDataSets
#  Set results = q.DoRawQuery(queryDS)
#  Dim result As DicomDataSet
#  For Each result In results
# 	Dim studyUID As String
# 	studyUID = result.studyUID