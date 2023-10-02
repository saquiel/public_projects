#! /usr/bin/env python3
# coding = utf-8



from pydicom import dcmread
from pydicom.data import get_testdata_file
from pydicom.fileset import FileSet


# To load an existing File-set just pass a DICOMDIR Dataset or the path to the DICOMDIR file to FileSet:
path = get_testdata_file("DICOMDIR")
ds = dcmread(path)
fs = FileSet(ds)  # or FileSet(path)


# The FileSet class treats a File-set as a flat collection of SOP Instances, 
# abstracting away the need to dig down into the hierarchy like you would with a DICOMDIR dataset. 
print(fs)

# For example, iterating over the FileSet yields a FileInstance object for each of the managed instances.

for instance in fs:
    print("\nIterating over the fileset, patient name:")
    print(instance.PatientName)
    break


# A list of unique element values within the File-set can be found using the find_values() method, 
# which by default searches the corresponding DICOMDIR records:
print("\nExtract StudyDescription values:")
print(fs.find_values("StudyDescription"))


# The search can be expanded to the File-set’s managed instances by supplying the load parameter, 
# at the cost of a longer search time due to having to read and decode the corresponding files:
print("\nfind_value without load")
print(fs.find_values("PhotometricInterpretation"))

print("\nfind_value with load")
print(fs.find_values("PhotometricInterpretation", load=True))


# the File-set can be searched to find instances matching a query using the find() method,
# which returns a list of FileInstance. 
# The corresponding file can then be read and decoded using FileInstance.load(), returning it as a FileDataset:

for instance in fs.find(PatientID='77654033'):
    ds = instance.load()
    print(ds.PhotometricInterpretation)

# find() also supports the use of the load parameter:
print(len(fs.find(PatientID='77654033', PhotometricInterpretation='MONOCHROME1')))

print(len(fs.find(PatientID='77654033', PhotometricInterpretation='MONOCHROME1', load=True)))