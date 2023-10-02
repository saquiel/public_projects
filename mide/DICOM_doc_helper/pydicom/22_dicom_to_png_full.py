import os
import cv2
import uuid
import logging
import warnings
import subprocess
import shutil
import numpy as np
from pydicom import dcmread, dcmwrite
from os.path import splitext, dirname, abspath, join, exists


import pydicom
from pydicom.pixel_data_handlers.util import apply_modality_lut, apply_voi_lut




PS_TARGET = float(os.getenv("TARGET_RATIO", 0.12))
PS_TH = float(os.getenv("PS_TH", 0.113))
LOGGER = logging.getLogger(__name__)

image_status = None


class BadPydicomDecoding(Exception):
    pass


def find_min_pixel_spacing(dcm_ds):
    """
    Retrieve minimum pixel spacing. 
    1 "PixelSpacing", 
    2 if failled: "ImagerPixelSpacing",
    3 Else return None

    Returns:
        float or None: minimum pixel spacing

    """

    pixel_spacing_min = None
    list_pixel_spacing = []
    if ("PixelSpacing" in dcm_ds) or ("ImagerPixelSpacing" in dcm_ds):

        # 1 try with PixelSpacing field:
        if dcm_ds.get("PixelSpacing") is not None:
            list_pixel_spacing = list(dcm_ds.get("PixelSpacing"))

        list_pixel_spacing = [float(value) for value in "PixelSpacing"]
        pixel_spacing_min = min(list_pixel_spacing)

        if (len(list_pixel_spacing) != 2) or (pixel_spacing_min <= 0):
        # 2 Abnormal value for ImagerPixelSpacing => try ImagerPixelSpacing 

            if dcm_ds.get("ImagerPixelSpacing") is not None:
                list_pixel_spacing = list(dcm_ds.get("ImagerPixelSpacing"))

            list_pixel_spacing = [float(value) for value in list_pixel_spacing]

            pixel_spacing_min = min(list_pixel_spacing)
            if (len(list_pixel_spacing) != 2) or (pixel_spacing_min <= 0):
            # 2 Abnormal value for ImagerPixelSpacing 
                pixel_spacing_min = None

    return pixel_spacing_min


def rescale_img_with_ps(img_data, min_ps, ps_th=PS_TH, ps_target=PS_TARGET):
    """
    Rescale image with low pixel spacing according to the target
    Args:
        img_data (ndarray): numpy array of image
        min_ps (float): minimum pixelSpacing in dicom's metadata
        ps_th (float): pixelSpacing upper threshold,
                       we only rescale image if pixelSpacing is lower than this threshold
        ps_target (float): pixelSpacing target, the targeted pixelSpacing for rescaled image

    Returns:
        ndarray: scaled image
        float: scale = scaled_image.shape / original_image.shape

    """
    if min_ps is not None and min_ps < ps_th:
        scale = min_ps / ps_target
        height = img_data.shape[0]
        width = img_data.shape[1]
        true_width = int(width * scale + 0.5)
        true_height = int(height * scale + 0.5)

        scaled_img_data = cv2.resize(img_data, (true_width, true_height))

    else:
        scale = 1.0
        scaled_img_data = img_data
    return scaled_img_data, scale


def retrieve_ps_and_rescale_img(image_data, image_file):
    """
    patch investigation: scale image according to lowest PixelSpacing/ImagerPixelSpacing
    Args:
        image_data (ndarray): numpy array of image
        image_file (str): path of dicom image

    Returns:
        ndarray: scaled image
        float: scale = scaled_image.shape / original_image.shape

    """
    ds = dcmread(image_file)
    min_pixel_spacing = find_min_pixel_spacing(ds)
    scaled_image_data, scale = rescale_img_with_ps(
        image_data, min_pixel_spacing, ps_th=PS_TH
    )
    if scale != 1.0:
        LOGGER.warning(
            "image {} with ps={} is resized !".format(image_file, min_pixel_spacing)
        )
    return scaled_image_data, scale


def convert_to_8bit_float(ndarray_img, dcm_ds):
    """
    Use real value of BitsStored to convert to 8-bit array
    Args:
        ndarray_img (ndarray): numpy array of image
        dcm_ds (pydicom.dataset.FileDataset): dicom dataset object of pydicom
        mode (str): conversion mode, can be 'dcm2jpg' to replicate dcm2jpg
            conversion or 'fullrange' to force using full [0-255] range.

    Returns:
        ndarray of type np.float64
    """

    # Same code taken from pydicom, in order to calculate the correct min/max pixel value
    # https://github.com/pydicom/pydicom/blob/14764114/pydicom/pixel_data_handlers/util.py#L370
    if "ModalityLUTSequence" in dcm_ds:
        # Unsigned - see PS3.3 C.11.1.1.1
        y_min = 0
        bit_depth = dcm_ds.ModalityLUTSequence[0].LUTDescriptor[2]
        y_max = 2 ** bit_depth - 1
    elif dcm_ds.PixelRepresentation == 0:
        # Unsigned
        y_min = 0
        y_max = 2 ** dcm_ds.BitsStored - 1
    else:
        # Signed
        y_min = -(2 ** (dcm_ds.BitsStored - 1))
        y_max = 2 ** (dcm_ds.BitsStored - 1) - 1

    if "RescaleSlope" in dcm_ds and "RescaleIntercept" in dcm_ds:
        # Otherwise its the actual data range
        y_min = y_min * dcm_ds.RescaleSlope + dcm_ds.RescaleIntercept
        y_max = y_max * dcm_ds.RescaleSlope + dcm_ds.RescaleIntercept

    ndarray_img_8bit_float = np.round(255.0 * (ndarray_img - y_min) / (y_max - y_min))

    return ndarray_img_8bit_float


def transform_dicom(ds, img_file, convert_ps):

    img_array = ds.pixel_array
    # Step 1: Modality LUT (*Rescale Slope* and *Rescale Intercept*)
    img_transformed = apply_modality_lut(img_array, ds)

    # Step 2: VOI LUT
    # If VOILUTSequence exists, then apply_voi_lut only accepts int as the type of input array
    if "VOILUTSequence" in ds:
        img_transformed = img_transformed.astype(np.int)
    # If no info is available for VOI lut then use auto-windowing
    if ("VOILUTSequence" not in ds) and (
        ("WindowCenter" not in ds) or ("WindowWidth" not in ds)
    ):
        if "RescaleSlope" not in ds:
            ds.RescaleSlope = 1.0
        if "RescaleIntercept" not in ds:
            ds.RescaleIntercept = 0.0
        ds.WindowCenter = (
            np.max(img_transformed) + np.min(img_transformed) + 1
        ) / 2 * ds.RescaleSlope + ds.RescaleIntercept
        ds.WindowWidth = (
            np.max(img_transformed) - np.min(img_transformed) + 1
        ) * ds.RescaleSlope

    if ds.PhotometricInterpretation in ["MONOCHROME1", "MONOCHROME2"]:
        img_transformed = apply_voi_lut(img_transformed, ds)

    # Step 3: Convert to 8-bit
    # We need to update the value of BitsStored
    # since apply_modality_lut/apply_voi_lut changes the pixel values' range
    img_transformed = convert_to_8bit_float(img_transformed, ds)

    # Step 4: Deal with image of inverse-contrast
    # Deal with (0028,0004) Photometric Interpretation (MONOCHROME1, MONOCHROME2)
    if ds.PhotometricInterpretation in ["MONOCHROME1"]:
        img_transformed = 255.0 - img_transformed

    # Step 5: Rescale image according to pixelSpacing
    if convert_ps:
        scaled_img_transformed, scale = retrieve_ps_and_rescale_img(
            img_transformed, img_file
        )
    else:
        scaled_img_transformed, scale = img_transformed, 1.0

    def round_to_uint8(img):
        return np.round(img).astype(np.uint8)

    def convert_2d_to_3d(img):
        if len(img.shape) == 2:
            return np.repeat(img[:, :, np.newaxis], 3, axis=-1)
        else:
            assert len(img.shape) == 3
            assert img.shape[-1] == 3
            return img

    # Convert to int array with 3 channels
    image_data = convert_2d_to_3d(round_to_uint8(img_transformed))
    scaled_image_data = convert_2d_to_3d(round_to_uint8(scaled_img_transformed))
    return image_data, scaled_image_data, scale


if __name__ == '__main__':

    img_file = "data_test/test_dx.dcm"
    img_file = "cochin/n108"


    ds = dcmread(img_file)

    convert_ps = False

    png_image, scaled_image_data, scale = transform_dicom(ds, img_file, convert_ps)



# TEST
    save_path = "output/png_image.png"
    cv2.imwrite(save_path, png_image)
    from PIL import Image
    # creating a object
    im = Image.open(save_path)
    im.show()








    