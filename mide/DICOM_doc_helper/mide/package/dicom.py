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

PS_TARGET = float(os.getenv("TARGET_RATIO", 0.12))
PS_TH = float(os.getenv("PS_TH", 0.113))
LOGGER = logging.getLogger(__name__)


class BadPydicomDecoding(Exception):
    pass


def retrieve_min_ps(dcm_ds):
    """
    Retrieve minimum pixel spacing. First look up "PixelSpacing", if not existing, look up "ImagerPixelSpacing"
    Args:
        dcm_ds (pydicom.dataset.FileDataset): dicom dataset object of pydicom

    Returns:
        float or None: minimum pixel spacing

    """

    def retrieve_min_ps_field(dcm_ds, ps_field):
        """
        ps_field should be either "PixelSpacing" or "ImagerPixelSpacing".
        """
        min_imager_pixel_spacing = None
        assert ps_field in ["PixelSpacing", "ImagerPixelSpacing"]
        if ps_field in dcm_ds:
            # the default null value of PixelSpacing has changed between pydicom1.2 (default='')
            # and pydicom2.0 (default=None).
            ps_read = (
                list(dcm_ds.get(ps_field)) if dcm_ds.get(ps_field) is not None else []
            )
            ps_read = [float(value) for value in ps_read]
            if len(ps_read) != 2:
                warn_message = "Strange {} value encountered: {}. Do not consider the value.".format(
                    ps_field, ps_read
                )
                LOGGER.warning(warn_message)
                warnings.warn(warn_message)
                min_imager_pixel_spacing = None
            else:
                min_imager_pixel_spacing = min(ps_read)
                if min_imager_pixel_spacing <= 0:
                    warn_message = "PixelSpacing <= 0 encountered: {}. Do not consider the value.".format(
                        min_imager_pixel_spacing
                    )
                    LOGGER.warning(warn_message)
                    warnings.warn(warn_message)
                    min_imager_pixel_spacing = None

        return min_imager_pixel_spacing

    min_imager_ps = retrieve_min_ps_field(dcm_ds, "PixelSpacing")
    if min_imager_ps is None:
        min_imager_ps = retrieve_min_ps_field(dcm_ds, "ImagerPixelSpacing")
    return min_imager_ps


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
        new_width = int(width * scale + 0.5)
        new_height = int(height * scale + 0.5)

        scaled_img_data = cv2.resize(img_data, (new_width, new_height))
        LOGGER.info(
            "Resize ({},{}) to ({},{})".format(
                height, width, scaled_img_data.shape[0], scaled_img_data.shape[1]
            )
        )
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
    min_pixel_spacing = retrieve_min_ps(ds)
    scaled_image_data, scale = rescale_img_with_ps(
        image_data, min_pixel_spacing, ps_th=PS_TH
    )
    if scale != 1.0:
        LOGGER.warning(
            "image {} with ps={} is resized !".format(image_file, min_pixel_spacing)
        )
    return scaled_image_data, scale


def convert_to_8bit_float(img_array, dcm_ds, mode="dcm2jpg"):
    """
    Use real value of BitsStored to convert to 8-bit array
    Args:
        img_array (ndarray): numpy array of image
        dcm_ds (pydicom.dataset.FileDataset): dicom dataset object of pydicom
        mode (str): conversion mode, can be 'dcm2jpg' to replicate dcm2jpg
            conversion or 'fullrange' to force using full [0-255] range.

    Returns:
        ndarray of type np.float64
    """
    if mode == "dcm2jpg":
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

        img = np.round(255.0 * (img_array - y_min) / (y_max - y_min))
        return img

    elif mode == "fullrange":

        max_pixel, min_pixel = float(np.max(img_array)), float(np.min(img_array))
        range_pixel = max_pixel - min_pixel

        if range_pixel == 0.0:
            LOGGER.error(
                "Image array can not be converted to 8-bit because all pixels have the same value !"
            )
            return np.zeros_like(img_array, dtype=np.float64)

        return np.asarray((img_array - min_pixel) / range_pixel * 255.0, np.float64)
    else:
        raise ValueError(f"mode {mode} is not known.")


def transform_dicom(ds, img_file, convert_ps):
    from pydicom.pixel_data_handlers.util import apply_modality_lut, apply_voi_lut

    img_array = ds.pixel_array
    # Step 1: Modality LUT (*Rescale Slope* and *Rescale Intercept*)
    img_transformed = apply_modality_lut(img_array, ds)

    # Step 2: VOI LUT
    # If VOILUTSequence exists, then apply_voi_lut only accepts int as the type of input array
    if "VOILUTSequence" in ds:
        img_transformed = img_transformed.astype(np.int)
    # If no info is available for VOI lut then use auto-windowing
    # https://github.com/dcm4che/dcm4che/blob/adfdac56092e711ac51ba77245dc6f5e6736a4da/dcm4che-image/src/main/java/org/dcm4che3/image/LookupTableFactory.java#L232
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
    img_transformed = convert_to_8bit_float(img_transformed, ds, mode="dcm2jpg")

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


def read_dicom_with_pydicom(img_file, convert_ps=False):
    """
    Read dicom file with pydicom 2.0
    Args:
        img_file (str): dicom file path
        convert_ps (bool): whether to rescale image according to its pixelSpacing

    Returns:
        ndarray of int: (H, W, 3), original image array before pixelSpacing rescale
        ndarray of int: (H', W', 3) rescaled image array after pixelSpacing rescale
        float: scale factor, scaled_dcm_data.shape = scale * original_dcm_data.shape
    """
    assert splitext(img_file)[-1] == ".dcm"

    try:
        ds = dcmread(img_file)
        return transform_dicom(ds, img_file, convert_ps)
    except RuntimeError as e:
        raise BadPydicomDecoding(f"pydicom error when decoding dicom: {e}")


def read_dicom_with_dcm2jpg(img_file, dcm2jpg_dir=None, convert_ps=False):
    """
    Read dicom file and returns image as array
    Args:
        img_file (str): path to dicom image
        dcm2jpg_dir (str): path to dcm2jpg dir
        convert_ps (bool): whether to check pixel spacing & rescale image array according to ps
    Returns:
        ndarray of int: original image array before pixelSpacing rescale
        ndarray of int: rescaled image array after pixelSpacing rescale
        float: scale factor, scaled_dcm_data.shape = scale * original_dcm_data.shape
    """
    assert splitext(img_file)[-1] == ".dcm"

    package_dir = dirname(dirname(abspath(__file__)))
    tmp_png_dir = abspath(join(package_dir, f"tmp_png_{uuid.uuid4().hex[:5]}"))
    os.makedirs(tmp_png_dir, exist_ok=True)
    if dcm2jpg_dir is None:
        dcm2jpg_dir = abspath(join(package_dir, "data", "dcm2jpg"))
        if not exists(dcm2jpg_dir):
            raise ValueError("dcm2jpg not found at {} !".format(dcm2jpg_dir))

    img_file = abspath(img_file)
    tmp_png = join(tmp_png_dir, f"_tmp_{uuid.uuid4().hex[:5]}.png")

    convert_dicom_to_png_dcm2jpg(img_file, tmp_png, dcm2jpg_dir)

    assert os.path.exists(tmp_png), f"Notfound {tmp_png}"

    try:
        image_data = cv2.imread(tmp_png)
        assert image_data is not None, "Can not read png image {} with opencv.".format(
            tmp_png
        )

        if convert_ps:
            scaled_image_data, scale = retrieve_ps_and_rescale_img(image_data, img_file)
        else:
            scaled_image_data, scale = image_data, 1.0

        image_data = image_data.astype(np.uint8)
        scaled_image_data = scaled_image_data.astype(np.uint8)
        return image_data, scaled_image_data, scale
    finally:
        # Clean up
        if os.path.exists(tmp_png):
            os.remove(tmp_png)
        if os.path.exists(tmp_png_dir):
            shutil.rmtree(tmp_png_dir)


def convert_dicom_to_png_dcm2jpg(dicom_file, output_png_path, dcm2jpg_dir):
    """
    Args:
        dicom_file: (str) path to dicom image
        output_png_path: (str) path to converted image
        dcm2jpg_dir: (str) path to dir of dcm2jpg jar
    Returns:
        None
    """
    assert os.path.splitext(dicom_file)[-1] == ".dcm"

    # check encoding metadata
    src_dir = dirname(dirname(abspath(__file__)))
    tmp_dcm_dir = abspath(join(src_dir, f"tmp_dcm_{uuid.uuid4().hex[:5]}"))
    os.makedirs(tmp_dcm_dir, exist_ok=True)
    tmp_dcm = None

    try:
        ds = dcmread(dicom_file)
        max_pix = ds.pixel_array.max()

        if max_pix > 2 ** int(ds.BitsStored) - 1:
            max_bit = np.floor(np.log2(max_pix)).astype(int)
            LOGGER.warning(
                f"Found incoherent BitsStored value {ds.BitsStored} for pydicom pixel_array "
                f"with highest value {max_pix} ({max_bit + 1} bits).\n"
                f"Writing temporary corrected dicom and using it for conversion.\n"
                f"Note: If some overlay was stored in the pixel data: it will be burned into the converted image."
            )
            ds.BitsStored = max_bit + 1
            ds.HighBit = max_bit
            tmp_dcm = join(tmp_dcm_dir, f"_tmp_{uuid.uuid4().hex[:5]}.dcm")
            dcmwrite(tmp_dcm, ds)

        # read dicom
        LOGGER.debug(
            f"Converting dicom {dicom_file if tmp_dcm is None else tmp_dcm} to png {output_png_path}..."
        )
        bash_command = "cd {dcm2jpg_dir} && ./dcm2jpg -F PNG {dcm} {png}".format(
            dcm2jpg_dir=dcm2jpg_dir,
            dcm=dicom_file if tmp_dcm is None else tmp_dcm,
            png=output_png_path,
        )

        process = subprocess.Popen(
            bash_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
        )
        (stdout, stderr) = process.communicate()
        LOGGER.debug(f"dcm2jpg conversion\nstdout:{stdout}\nstderr:{stderr}")
        if process.returncode != 0:
            raise ChildProcessError(stderr)
    finally:
        # Clean up
        if tmp_dcm is not None and os.path.exists(tmp_dcm):
            os.remove(tmp_dcm)
        if os.path.exists(tmp_dcm_dir):
            shutil.rmtree(tmp_dcm_dir)


def get_dcm2jpg_folder():
    # import inside function, since circular import of test.__init__ make the code break.
    # TODO: fix this issue
    from glmcommons.tests.data import maybe_download

    dcm2jpg_folder = maybe_download("dcm2jpg")
    if oct(os.stat(dcm2jpg_folder).st_mode & 0o777) != "0o755":
        os.chmod(
            join(dcm2jpg_folder, "dcm2jpg"), 0o755
        )  # add executable mode for all users
    return dcm2jpg_folder
