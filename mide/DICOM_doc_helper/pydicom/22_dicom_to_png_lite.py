
import cv2
import numpy as np
from pydicom import dcmread
from pydicom.pixel_data_handlers.util import apply_modality_lut, apply_voi_lut


image_status = None


def dicom_to_png(ds_dicom):

    img_array = ds_dicom.pixel_array

    # Rescale Slope Intercept
    img_transformed = apply_modality_lut(img_array, ds_dicom)

    # If VOILUTSequence exists => apply_voi_lut 
    if "VOILUTSequence" in ds_dicom:
        img_transformed = img_transformed.astype(np.int) # only accepts int array

    # If no info is available for VOI lut then use auto-windowing
    elif ("WindowCenter" not in ds_dicom) or ("WindowWidth" not in ds_dicom):
        # Init RescaleSlope and RescaleIntercept
        if "RescaleSlope" not in ds_dicom:
            ds_dicom.RescaleSlope = 1.0
        if "RescaleIntercept" not in ds_dicom:
            ds_dicom.RescaleIntercept = 0.0
        ds_dicom.WindowCenter = (
            np.max(img_transformed) + np.min(img_transformed) + 1
        ) / 2 * ds_dicom.RescaleSlope + ds_dicom.RescaleIntercept
        ds_dicom.WindowWidth = (
            np.max(img_transformed) - np.min(img_transformed) + 1
        ) * ds_dicom.RescaleSlope

    if ds_dicom.PhotometricInterpretation in ["MONOCHROME1", "MONOCHROME2"]:
        img_transformed = apply_voi_lut(img_transformed, ds_dicom)


    # 8-bit array conversion => Code from pydicom

    # calculate the correct min/max pixel value 
    if "ModalityLUTSequence" in ds_dicom:
        # Unsigned
        y_min = 0
        bit_depth = ds_dicom.ModalityLUTSequence[0].LUTDescriptor[2]
        y_max = 2 ** bit_depth - 1
    elif ds_dicom.PixelRepresentation == 0:
        # Unsigned
        y_min = 0
        y_max = 2 ** ds_dicom.BitsStored - 1
    else:
        # Signed
        y_min = -(2 ** (ds_dicom.BitsStored - 1))
        y_max = 2 ** (ds_dicom.BitsStored - 1) - 1

    if "RescaleSlope" in ds_dicom and "RescaleIntercept" in ds_dicom:
        # Otherwise its the actual data range
        y_min = y_min * ds_dicom.RescaleSlope + ds_dicom.RescaleIntercept
        y_max = y_max * ds_dicom.RescaleSlope + ds_dicom.RescaleIntercept

    # convert to 8-bit array
    ndarray_img_8bit_float = np.round(255.0 * (img_transformed - y_min) / (y_max - y_min))


    # Inverse image pixel value (contrast) if MONOCHROME1
    if ds_dicom.PhotometricInterpretation in ["MONOCHROME1"]:
        ndarray_img_8bit_float = 255.0 - ndarray_img_8bit_float


    # Convert to rounded int array with 3 channels
    rounded_int = np.round(ndarray_img_8bit_float).astype(np.uint8)

    if len(rounded_int.shape) == 2:
        image_data = np.repeat(rounded_int[:, :, np.newaxis], 3, axis=-1)
    elif (len(rounded_int.shape) == 3) and (rounded_int.shape[-1] == 3):

        image_data = rounded_int

    return image_data




img_file = "data_test/test_dx.dcm"
# img_file = "cochin/n108"


ds_dicom = dcmread(img_file)

png_image = dicom_to_png(ds_dicom)

print(type(png_image))

print(png_image.shape)

# TEST
save_path = "output/png_image.png"
cv2.imwrite(save_path, png_image)
from PIL import Image
# creating a object
im = Image.open(save_path)
im.show()








    