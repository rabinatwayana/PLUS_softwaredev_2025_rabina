"""Preprocessing Sentinel1 Data

The main purpose of this scripts is to allow user to load sentinel 1 GRD data using rioxarry, 
perform "thermal_noise_remove" and "radiometric calibration" preprocessing steps.

This allows the user to load sentinel 1 GRD data, 
perform thermal noise removal and radiometric calibration preprocessing steps.

This tool accepts .SAFE format file.

This script requires that `rioxarray`, 'numpy' and 'xarray' be installed within the Python
environment you are running this script in.

This file can also be imported as a module and contains the following functions:
    Major: 
        * load_sentinel1_data - returns the 
        * remove_thermal_noise - returbs the 
        * radiometric_calibration - 
    Supporting:
        *  parse_thermal_noise_removal_lut
        *  parse_radiometric_calibration_lut
"""

import os
import rioxarray #https://pypi.org/project/rioxarray/
import xarray as xr
import numpy as np
import xml.etree.ElementTree as ET #To read and parse XML files

def load_sentinel1_data(safe_folder_path):
    """
    Loads Sentinel-1 GRD SAR data from a SAFE format directory.

    This function reads GeoTIFF files from the 'measurement' folder within the
    provided SAFE directory path, identifies available polarizations (e.g., VV, VH),
    and returns an xarray.Dataset with each polarization as a separate data variable.

    Arguments:
        safe_folder_path (str): Path to the root directory of the Sentinel-1 SAFE format product.

    Returns:
        xarray.Dataset: A dataset containing the loaded SAR bands as data variables 
        (e.g., 'VV', 'VH'). Each variable is a 2D DataArray with geospatial metadata.

    Raises Exception:
        FileNotFoundError: If the 'measurement' folder or required GeoTIFF files are missing,
        or if polarization type cannot be determined from the file names.
    """
    measurement_path = os.path.join(safe_folder_path, "measurement")
    if not os.path.exists(measurement_path):
        raise FileNotFoundError(f"'measurement' folder not found inside {safe_folder_path}")

    # Getting all GeoTIFF files in measurement folder
    tiff_files = [f for f in os.listdir(measurement_path) if f.endswith(".tiff") or f.endswith(".tif")]
    if not tiff_files:
        raise FileNotFoundError("No GeoTIFF files found in 'measurement' folder")

    data_vars = {} #empty dict

    #Extracting polarization from the file name
    for tiff in tiff_files:
        polarizations = ["vv", "vh", "hh", "hv"]
        band_name = None
        for pol in polarizations:
            if pol in tiff.lower():
                band_name = pol.upper()
                break

        if not band_name:
            raise FileNotFoundError(f"Polarization type not found in file name: {tiff}")
        
        tiff_path = os.path.join(measurement_path, tiff)
        print(f"Reading {band_name} band")
        
        # Reading tiff file using rioxarray
        da = rioxarray.open_rasterio(tiff_path)
        # print(da.dims,"da dims")
        # print(len(da.band) )

        # Since single band is available in tiff file, removing the extra dimention for simplicity
        if 'band' in da.dims and len(da.band) == 1:
            da = da.squeeze('band', drop=True)
        data_vars[band_name.upper()] = da

    # Combining bands into a single xarray_datasets
    ds = xr.Dataset(data_vars)
    # print(list(ds.keys()))
    print("Data loaded successfully")
    return ds

def parse_thermal_noise_removal_lut(safe_folder_path):
    """
    Parsing Lookup Table (LUT) for thermal noise removal raeding the noise xml file.

    This function reads noise related XML files within the 'annotation/calibration' folder in the
    provided SAFE directory path,
    and returns an xarray.Dataset with LUT for available polarizations

    Arguments:
        safe_folder_path (str): Path to the root directory of the Sentinel-1 SAFE format product.

    Returns:
        xarray.Dataset: A dataset containing the LUT for noise removal for available polarizations
        (e.g., 'VV', 'VH')

    Raises Exception:
        FileNotFoundError: If the 'calibration' folder or required XML files are missing,
    """

    calibration_path = os.path.join(safe_folder_path, "annotation/calibration/")
    if not os.path.exists(calibration_path):
        raise FileNotFoundError(f"'calibration' folder not found inside {safe_folder_path}")

    # Find XML files starting with 's1a-iw-grd' (case insensitive)
    xml_files = [f for f in os.listdir(calibration_path) if f.lower().startswith('noise') and f.lower().endswith('.xml')]
    if not xml_files:
        raise FileNotFoundError("No suitable calibration XML files found in 'calibration' folder")
    lut_dict={}
    for xml_file in xml_files:
        polarizations = ["vv", "vh", "hh", "hv"]
        band_name = None
        for pol in polarizations:
            if pol in xml_file.lower():
                band_name = pol.upper()
                break

        if not band_name:
            raise FileNotFoundError(f"Polarization type not found in file name: {xml_file}")

        print(f"Reading xml for {band_name} band")

        xml_path = os.path.join(calibration_path, xml_file)
        tree = ET.parse(xml_path)
        root = tree.getroot()

        lines = []
        pixels = None
        noise_values = []

        for calib_vec in root.findall('.//noiseRangeVector'):
            line = int(calib_vec.find('line').text)
            pixel_str = calib_vec.find('pixel').text.strip()
            noise_range_str = calib_vec.find("noiseRangeLut").text.strip()

            pixels = [int(x) for x in pixel_str.split()]
            noise = [float(x) for x in noise_range_str.split()]

            lines.append(line)
            noise_values.append(noise)
        noise_array = np.array(noise_values)
        lut = xr.DataArray(noise_array, coords={"line": lines, "pixel": pixels}, dims=["line", "pixel"])
        lut_dict[band_name]= lut    
    lut_ds = xr.Dataset(lut_dict)
    print("Thermal noise removal LUT created successfully")
    return lut_ds

def parse_radiometric_calibration_lut(safe_folder_path, representation_type="sigmaNought"):
    """
    Parsing LUT for radiometric calibration bt reading the calibration xml files.

    This function reads calibration related XML files within the 'annotation/calibration' folder in the
    provided SAFE directory path,
    and returns an xarray.Dataset with LUT for available polarizations based on the representation type as required.

    Arguments:
        safe_folder_path (str): Path to the root directory of the Sentinel-1 SAFE format product.
        representation_type (str, optional): Type of backscatter representation to be used. 
        Options are:
            - 'sigmaNought' (default)
            - 'betaNought'
            - 'gamma'

    Returns:
        xarray.Dataset: A dataset containing the LUT for radiometric calibration for available polarizations
        (e.g., 'VV', 'VH')

    Raises Exception:
        Exception: representation_type is not valid
        FileNotFoundError: If the 'calibration' folder or required XML files are missing,
    """

    supporting_representation_types=["sigmaNought","betaNought","gamma"]
    if representation_type not in supporting_representation_types:
        raise Exception(f"representation_type {representation_type} is not supported. Supporting types are {supporting_representation_types}")

    calibration_path = os.path.join(safe_folder_path, "annotation/calibration/")
    if not os.path.exists(calibration_path):
        raise FileNotFoundError(f"'calibration' folder not found inside {safe_folder_path}")

    # Find XML files starting with 's1a-iw-grd' (case insensitive)
    xml_files = [f for f in os.listdir(calibration_path) if f.lower().startswith('calibration') and f.lower().endswith('.xml')]
    if not xml_files:
        raise FileNotFoundError("No suitable calibration XML files found in 'calibration' folder")
    lut_dict={}
    for xml_file in xml_files:

        polarizations = ["vv", "vh", "hh", "hv"]
        band_name = None
        for pol in polarizations:
            if pol in xml_file.lower():
                band_name = pol.upper()
                break

        if not band_name:
            raise FileNotFoundError(f"Polarization type not found in file name: {xml_file}")

        print(f"Reading calibration for {band_name} band")

        xml_path = os.path.join(calibration_path, xml_file)
        tree = ET.parse(xml_path)
        root = tree.getroot()

        lines = []
        pixels = None
        correction_values = []

        for calib_vec in root.findall('.//calibrationVector'):
            line = int(calib_vec.find('line').text)
            pixel_str = calib_vec.find('pixel').text.strip()
            value_str = calib_vec.find(representation_type).text.strip()

            pixels = [int(x) for x in pixel_str.split()]
            values = [float(x) for x in value_str.split()]

            lines.append(line)
            correction_values.append(values)

        beta_array = np.array(correction_values)
        lut = xr.DataArray(beta_array, coords={"line": lines, "pixel": pixels}, dims=["line", "pixel"])
        lut_dict[band_name]= lut    
    lut_ds = xr.Dataset(lut_dict)
    print("Radiometric calibration LUT created successfully")
    return lut_ds

def apply_correction(type, ds, lut_ds):
    """
    This is the common function to apply thermal noise removal and raduometric correction

    Arguments:
        type (str): Type of correction
        Options are:
            - 'thermal_noise_removal'
            - 'radiometric_calibration'
        representation_type (str, optional): Type of backscatter representation to be used. 
        Options are:
            - 'sigmaNought' (default)
            - 'betaNought'
            - 'gamma'
    
    Returns:
        xarray.Dataset: A dataset containing corrected backscatter values for available polarizations
    """
    corrected_dict={}
    for pol in list(ds.keys()):
        da= ds[pol]
        lut=lut_ds[pol]

        # Creating full image grid
        image_lines = np.arange(da.shape[0])   
        image_pixels = np.arange(da.shape[1])  

        # Interpolate the LUT on these coordinates (numeric interpolation):
        lut_interp = lut.interp(
            line=image_lines,
            pixel=image_pixels,
            method='linear',
            kwargs={"fill_value": "extrapolate"}  # to extrapolate near edges if needed
        )

        if da.dims != lut_interp.dims:
            da = da.rename({'y': 'line', 'x': 'pixel'}) 

        # Apply correction using respective formula
        if type=="thermal_noise_removal":
            # source: https://sentinels.copernicus.eu/documents/247904/2142675/Thermal-Denoising-of-Products-Generated-by-Sentinel-1-IPF.pdf#page=18.10
            corrected_dict[pol] = xr.where(da**2 - lut_interp > 0, da**2 - lut_interp, 0)
        elif type=="radiometric_calibration":
            #SOURCE: https://sentinels.copernicus.eu/documents/247904/685163/S1-Radiometric-Calibration-V1.0.pdf
            corrected_dict[pol] = da / (lut_interp**2) # Since da is thermally corrected, no need of da**2
        
    calibrated_ds= xr.Dataset(corrected_dict)
    return calibrated_ds


def remove_thermal_noise(ds, lut_ds):

    """
    Removes thermal noise from Sentinel-1 SAR GRD data using a provided lookup table (LUT).

    This function applies thermal noise correction to each band in the input dataset
    using the specified LUT dataset. 
    
    It relies on a function "apply_correction" with the correction type set to "thermal_noise_removal".

    Args:
        ds (xarray.Dataset): The input dataset containing one or more polarization bands 
            (e.g., 'VV', 'VH') as data variables which is result of function "load_sentinel1_data".
        lut_ds (xarray.Dataset or dict): The thermal noise lookup table used for correction, 
            which is the result of function "parse_thermal_noise_removal_lut".

    Returns:
        xarray.Dataset: A dataset with thermal noise removed from each polarization band.
    """

    result=apply_correction("thermal_noise_removal",ds, lut_ds)
    print("Thermal noise removed successfully")
    return result


def radiometric_calibration(ds, lut_ds):
    """
    Perform radiometric calibration of Sentinel-1 SAR GRD data using a provided lookup table (LUT).

    This function applies radiometric calibration to each band in the input dataset
    using the specified LUT dataset. 
    
    It relies on a function "apply_correction" with the correction type set to "radiometric_calibration".

    Args:
        ds (xarray.Dataset): The input dataset containing one or more polarization bands 
            (e.g., 'VV', 'VH') as data variables which is result of function "load_sentinel1_data".
        lut_ds (xarray.Dataset or dict): The thermal noise lookup table used for correction, 
            which is the result of function "parse_radiometric_calibration_lut".

    Returns:
        xarray.Dataset: A dataset with thermal noise removed from each polarization band.
    """

    result= apply_correction("radiometric_calibration", ds, lut_ds)
    print("Radiometric calibration completed successfully")
    return result

    