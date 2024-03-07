#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 2023
@author: Bridget Hass (bhass@battelleecology.org)

Adapted from R neonUtilities byFileAOP
https://github.com/NEONScience/NEON-utilities/blob/main/neonUtilities/R/byFileAOP.R
written by:
@author: Claire Lunch (clunch@battelleecology.org)
@author: Christine Laney (claney@battelleecology.org)

"""
# TODO: Add provisional/release handling in by_file_aop and by_tile_aop
# TODO: Get shared_flights.csv working properly in package using importlib_resources.files
# TODO: Set user agent
# TODO: Add functionality to get new list of URLs if the old ones expire during the download stream
# TODO: Get DOIs and generate citations (using get_citation function)

import importlib
import importlib_resources
from . import __resources__
from pathlib import Path
# from aop_helpers import get_api
from neonutilities import get_api
import numpy as np
import pandas as pd
import re
# from tdqm import tdqm
from progress.bar import Bar
from time import sleep


# check that token was used
def check_token(response):
    """
    Query the API for AOP data by site, year, and product, and download all
    files found, preserving original folder structure. Downloads serially to
    avoid API rate-limit overload; may take a long time.

    Parameters
    --------
    response:

    Return
    --------
    Warning statement explaining that the API token was not recognized.

    """

    if 'x-ratelimit-limit' in response.headers and response.headers['x-ratelimit-limit'] == '200':
        print('API token was not recognized. Public rate limit applied.\n')


def convert_byte_size(size_bytes):
    """
    Convert the file size in bytes to a more readable format for display.

    Parameters
    --------
    size_bytes: the full file size in bytes

    Return
    --------
    String of converted file size in KB, MB, GB, or TB.
    """

    if 10**3 < size_bytes < 10**6:
        size_kb = round(size_bytes/(10**3), 2)
        size_read = f'{size_kb} KB'
    elif 10**6 < size_bytes < 10**9:
        size_mb = round(size_bytes/(10**6), 1)
        size_read = f'{size_mb} MB'
        # print('Download size:', size_read)
    elif 10**9 < size_bytes < 10**12:
        size_gb = round(size_bytes/(10**9), 1)
        size_read = f'{size_gb} GB'
        # print('Download size:', size_read)
    else:
        size_tb = round(size_bytes/(10**12), 1)
        size_read = f'{size_tb} TB'
        # print('Download size:', size_read)
    return size_read

# %%


def download_file(url, save_path, token=None):
    """
    Function to download a single file from a file's google cloud storage url.

    Parameters
    --------
    url: google cloud storage url where the file is stored
    save_path: the file location (path) where a file will be downloaded
    token: User specific API token (generated within neon.datascience user accounts). Optional.

    Return
    --------
    Downloads the file to the user-specified directory "save_path".

    """
    # print('url:', url)
    file_name = url.split('/')[-1]
    # print(f'downloading {file_name}')
    if 'neon-publication' in url:
        file_path = url.split('/')[-1]
        # print(url)
        # print(file_path)
    else:  # elif 'neon-aop-products' in url:
        file_path = url.split('neon-aop-products/')[1]
    file_fullpath = save_path / file_path
    file_fullpath.parent.mkdir(parents=True, exist_ok=True)
    # print(f'downloading file to {file_fullpath}')
    req = get_api(url, token)
    with open(file_fullpath, 'wb') as f:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    return

# %%


def get_file_urls(urls, token=None):
    """
    Get all the files from a list of urls

    Parameters
    --------
    urls:
    token: User specific API token (generated within neon.datascience user accounts). Optional.

    Return
    --------
    file_url_df:
    release:

    """

    for url in urls:
        req = get_api(api_url=url, token=token)
        if not req:
            print(
                f"Data file retrieval failed. Check NEON data portal for outage alerts.")

        # get release info
        release = req.json()['data']['release']

        file_url_dict = req.json()['data']['files']
        file_url_df = pd.DataFrame(data=file_url_dict)
        # drop md5 and crc32 columns, which are all NaNs
        file_url_df.drop(columns=['md5', 'crc32'], inplace=True)

    return file_url_df, release

# %%


def get_shared_flights(site):
    shared_flights_file = (importlib_resources.files(
        __resources__) / 'shared_flights.csv')

    shared_flights_df = pd.read_csv(shared_flights_file)

    shared_flights_dict = shared_flights_df.set_index(
        ['site'])['flightSite'].to_dict()
    if site in shared_flights_dict:
        flightSite = shared_flights_dict[site]
        if site in ['TREE', 'CHEQ', 'KONA', 'DCFS']:
            print(
                f'{site} is part of the flight box for {flightSite}. Downloading data from {flightSite}.')
        else:
            print(f'{site} is an aquatic site and is sometimes included in the flight box for {flightSite}. Aquatic sites are not always included in the flight coverage every year. \nDownloading data from {flightSite}. Check data to confirm coverage of {site}.')
        site = flightSite
    return site
# %%


def by_file_aop(dpid,
                site,
                year,
                include_provisional=False,
                check_size=True,
                save_path=None,
                token=None):
    """
    Query the API for AOP data by site, year, and product, and download all
    files found, preserving original folder structure. Downloads serially to
    avoid API rate-limit overload; may take a long time.

    Parameters
    --------
    dpid: The identifier of the NEON data product to pull, in the form DPL.PRNUM.REV, e.g. DP3.30001.001. String.
    site: The four-letter code of a single NEON site, e.g. 'CLBJ'. String.
    year: The four-digit year to search for data. String or integer.
    check_size: True or False, should the user approve the total file size before downloading? Defaults to True. When working in batch mode, or other non-interactive workflow, use check.size=False.
    include_provisional: True or False, should provisional data be included in downloaded files? Defaults to F. See https://www.neonscience.org/data-samples/data-management/data-revisions-releases for details on the difference between provisional and released data.
    save_path: The file path to download to. Defaults to None, in which case the working directory is used.
    token: User specific API token (generated within neon.datascience user accounts). Optional.

    Return
    --------
    A folder in the working directory, containing all AOP files meeting query criteria.

    Example
    --------
    Download 2021 CHM data from MCRA:
    byFileAOP(dpid="DP3.30015.001", site="MCRA",
              year="2021",save_path="../../test_download")
    """

    # error message if dpid isn't formatted as expected
    dpid_pattern = "DP[1-4]{1}.[0-9]{5}.00[1-2]{1}"
    if not re.fullmatch(dpid_pattern, dpid):
        print(
            f'{dpid} is not a properly formatted data product ID. The correct format is DP#.#####.00#')
        return

    # error message if field spectra data are attempted
    if dpid == 'DP1.30012.001':
        print(
            'DP1.30012.001 is the Field spectral data product, which is published as tabular data. Use zipsByProduct() or loadByProduct() to download these data.')
        return

    # error message if site is not a 4-letter character
    site = site.upper()  # make site upper case (if it's not already)
    site_pattern = "[A-Z]{4}"
    if not re.fullmatch(site_pattern, site):
        print(
            f'{site} is an invalid site. A four-letter NEON site code is required. NEON sites codes can be found here: https://www.neonscience.org/field-sites/field-sites-map/list.')
        return

    # error message if year input is not valid
    year = str(year)  # cast year to string (if it's not already)
    year_pattern = "20[1-9][0-9]"
    if not re.fullmatch(year_pattern, year):
        print(
            f'{year} is an invalid year. Year is required in the format "2017", eg. Data are available from 2013 to present.')
        return

    # if token is an empty string, set to None
    if token == '':
        token = None

    # query the products endpoint for the product requested
    response = get_api(
        "http://data.neonscience.org/api/v0/products/" + dpid, token)

  # # query the products endpoint for the product requested
  # req <- getAPI(paste("http://data.neonscience.org/api/v0/products/", dpID, sep=""), token)
  # avail <- jsonlite::fromJSON(httr::content(req, as="text", encoding="UTF-8"),
  #                             simplifyDataFrame=TRUE, flatten=TRUE)

# with the way get_api is currently written it returns None for a bad request
# eg. https://data.neonscience.org/api/v0/products/DP3.30050.001
# doesn't seem like this part below is actually doing anything in the R script either?
# not sure what edge case it is handling
# # error message if product not found
#   if(!is.null(avail$error$status)) {
#     stop(paste("No data found for product", dpID, sep=" "))
#   }

#   # check that token was used
    if token and 'x-ratelimit-limit' in response.headers:
        check_token(response)
        # if response.headers['x-ratelimit-limit'] == '200':
        #     print('API token was not recognized. Public rate limit applied.\n')

    # get the request respose dictionary
    response_dict = response.json()
    # error message if dpid is not an AOP data product
    if response_dict['data']['productScienceTeamAbbr'] != 'AOP':
        print(
            f'{dpid} is not a remote sensing product. Use zipsByProduct()')
        return

    # replace collocated site with the site name it's published under
    site = get_shared_flights(site)

    # get the urls for months with data available, and subset to site
    site_info = next(
        item for item in response_dict['data']['siteCodes'] if item["siteCode"] == site)
    site_urls = site_info['availableDataUrls']

    site_year_urls = [url for url in site_urls if str(year) in url]

    # error message if nothing is available
    if len(site_year_urls) == 0:
        print("There are no data available at the selected site and year.")

    # get file url dataframe for the available month urls
    file_url_df, release = get_file_urls(site_year_urls, token=token)

    # get the number of files in the dataframe, if there are no files to download, return
    num_files = len(file_url_df)
    if num_files == 0:
        print("No data files found.")
        return

    # get the total size of all the files found
    download_size_bytes = file_url_df['size'].sum()
    download_size = convert_byte_size(download_size_bytes)

    # report data download size and ask user if they want to proceed
    if check_size:
        if input(f"Continuing will download {num_files} totaling approximately {download_size}. Do you want to proceed? (y/n) ") != "y":
            print("Download halted.")
            return

    # create folder in working directory to put files in
    if save_path:
        download_path = Path.cwd() / Path(save_path)
    else:
        download_path = Path.cwd()
    # print('download path', download_path)
    download_path.mkdir(parents=True, exist_ok=True)

    # serially download all files, with tdqm progress bar
    files = list(file_url_df['url'])
    print(
        f"Downloading {num_files} files totaling approximately {download_size}\n")
    sleep(1)
    # for file in tdqm(files): # if tdqm imports properly, this should work
    with Bar('Download Progress...', max=len(files)) as bar:
        for file in files:
            # try:
            download_file(file, download_path)
            bar.next()
        # except Exception as e:
        #     print(e)
        bar.finish()

    return

# %%


def by_tile_aop(dpid,
                site,
                year,
                easting,
                northing,
                buffer=0,
                include_provisional=False,
                check_size=True,
                save_path=None,
                token=None,
                verbose=False):
    """
    Query the API for AOP data by site, year, product, and UTM coordinates,
    download all files found, preserving original folder structure. Downloads
    serially to avoid API rate-limit overload; may take a long time.

    Parameters
    --------
    dpid: The identifier of the NEON data product to pull, in the form DPL.PRNUM.REV, e.g. DP3.30001.001
    site: The four-letter code of a single NEON site, e.g. 'CLBJ'.
    year: The four-digit year to search for data.
    easting: A number or list containing the easting UTM coordinate(s) of the locations to download.
    northing: A number or list containing the northing UTM coordinate(s) of the locations to download.
    buffer: Size, in meters, of the buffer to be included around the coordinates when determining which tiles to download. Defaults to 0. If easting and northing coordinates are the centroids of NEON TOS plots, use buffer=20.
    include_provisional: True or False, should provisional data be included in downloaded files? Defaults to F. See https://www.neonscience.org/data-samples/data-management/data-revisions-releases for details on the difference between provisional and released data.
    check_size: True or False, should the user approve the total file size before downloading? Defaults to True. When working in batch mode, or other non-interactive workflow, use check.size=False.
    save_path: The file path to download to. Defaults to None, in which case the working directory is used.
    token: User specific API token (generated within neon.datascience user accounts). Optional.

    Return
    --------
    A folder in the working directory, containing all AOP files meeting query criteria.

    Example
    --------
    Download 2021 CHM data from MCRA at a single point:
    by_tile_aop(dpid="DP3.30015.001", site="MCRA",year="2021",save_path="../../test_download")


    """

    # error message if dpid isn't formatted as expected
    dpid_pattern = "DP[1-4]{1}.[0-9]{5}.00[1-2]{1}"
    if not re.fullmatch(dpid_pattern, dpid):
        print(
            f'{dpid} is not a properly formatted data product ID. The correct format is DP#.#####.00#')
        return

    # error message if field spectra data are attempted
    if dpid == 'DP1.30012.001':
        print(
            'DP1.30012.001 is the Field spectral data product, which is published as tabular data. Use zipsByProduct() or loadByProduct() to download these data.')
        return

    # error message if site is not a 4-letter character
    site = site.upper()  # make site upper case (if it's not already)
    site_pattern = "[A-Z]{4}"
    if not re.fullmatch(site_pattern, site):
        print(
            f'{site} is an invalid site. A four-letter NEON site code is required. NEON sites codes can be found here: https://www.neonscience.org/field-sites/field-sites-map/list.')
        return

    # error message if year input is not valid
    year = str(year)  # cast year to string (if it's not already)
    year_pattern = "20[1-9][0-9]"
    if not re.fullmatch(year_pattern, year):
        print(
            f'{year} is an invalid year. Year is required in the format "2017", eg. Data are available from 2013 to present.')
        return

    # convert easting and northing to lists, if they are not already
    if type(easting) is not list:
        easting = [easting]
    if type(northing) is not list:
        northing = [northing]

    # convert to floats, and display error message if easting and northing lists are not numeric
    try:
        easting = [float(e) for e in easting]
    except ValueError as e:
        print(
            f'The easting is invalid, this is required as a number or numeric list format, eg. 732000 or [732000, 733000]')
        print(e)

    try:
        northing = [float(e) for e in northing]
    except ValueError as e:
        print(
            f'The northing is invalid, this is required as a number or numeric list format, eg. 4713000 or [4713000, 4714000]')
        print(e)

    # link easting and northing coordinates - as a list of tuples ?
    #coord_tuples = [(easting[i], northing[i]) for i in range(0, len(easting))]

    # error message if easting and northing vector lengths don't match (also handles empty/NA cases)
    # note there should not be any strings now that we've converted everything to float
    easting = [e for e in easting if not np.isnan(e)]
    northing = [n for n in northing if not np.isnan(n)]

    if len(easting) != len(northing):
        print(
            f'Easting and northing list lengths do not match, and/or contain null values. Cannot identify paired coordinates.')
        return

    # if token is an empty string, set to None
    if token == '':
        token = None

    # query the products endpoint for the product requested
    response = get_api(
        "http://data.neonscience.org/api/v0/products/" + dpid, token)

#   # check that token was used
    if token and 'x-ratelimit-limit' in response.headers:
        check_token(response)
        # if response.headers['x-ratelimit-limit'] == '200':
        #     print('API token was not recognized. Public rate limit applied.\n')

    # get the request respose dictionary
    response_dict = response.json()
    # error message if dpid is not an AOP data product
    if response_dict['data']['productScienceTeamAbbr'] != 'AOP':
        print(
            f'{dpid} is not a remote sensing product. Use zipsByProduct()')
        return

    # replace collocated site with the site name it's published under
    site = get_shared_flights(site)

    # get the urls for months with data available, and subset to site
    site_info = next(
        item for item in response_dict['data']['siteCodes'] if item["siteCode"] == site)
    site_urls = site_info['availableDataUrls']

    # error message if nothing is available
    if len(site_urls) == 0:
        print("There are no data available at the selected site and year.")

    # get file url dataframe for the available month url(s)
    file_url_df, release = get_file_urls(site_urls, token=token)

    # get the number of files in the dataframe, if there are no files to download, return
    num_files = len(file_url_df)
    if num_files == 0:
        print("No data files found.")
        return

    # convert easting & northing coordinates for Blandy (BLAN)
    # Blandy contains plots in 18N and plots in 17N; flight data are all in 17N
    if site == 'BLAN' and any([e > 725000.0 for e in easting]):
        # check that pyproj is installed
        try:
            importlib.import_module('pyproj')
            print("pyproj is installed.")
        except ImportError:
            print(
                "Package pyproj is required for this function to work at the BLAN site. Install and re-try")
            return

        from pyproj import Proj, CRS

        crs17 = CRS.from_epsg(32617)  # utm zone 17N
        crs18 = CRS.from_epsg(32618)  # utm zone 18N

        proj18to17 = Proj.from_crs(crs_from=crs18, crs_to=crs17)

        # add warning if provided an easting > 250000 ?

        # link easting and northing coordinates so it's easier to parse the zone for each
        coord_tuples = [(easting[i], northing[i])
                        for i in range(0, len(easting))]

        coords17 = [(e, n) for (e, n) in coord_tuples if e > 250000.0]
        coords18 = [(e, n) for (e, n) in coord_tuples if e <= 250000.0]

        # apply the projection transformation from 18N to 17N for each coordinate tuple

        coords18_reprojected = [proj18to17.transform(
            coords18[i][0], coords18[i][1]) for i in range(len(coords18))]

        coords17.extend(coords18_reprojected)

        easting = [c[0] for c in coords17]
        northing = [c[1] for c in coords17]

        print('Blandy (BLAN) plots include two UTM zones, flight data are '
              'all in 17N. Coordinates in UTM zone 18N have been converted '
              'to 17N to download the correct tiles. You will need to make '
              'the same conversion to connect airborne to ground data.')

    # function to round down to the nearest 1000, in order to determine lower left coordinate of AOP tile to be downloaded
    def round_down1000(val):
        return int(np.floor(val/1000)*1000)

    # function to get the coordinates of the tiles including the buffer
    def get_buffer_coords(easting, northing, buffer):
        # apply the buffer to the easting and northings
        buffer_min_e = easting - buffer
        buffer_min_n = northing - buffer
        buffer_max_e = easting + buffer
        buffer_max_n = northing + buffer

        new_coords = [(buffer_min_e, buffer_min_n), (buffer_min_e, buffer_max_n),
                      (buffer_max_e, buffer_min_n), (buffer_max_e, buffer_max_n)]

        return new_coords

    # get the tiles corresponding to the new coordinates (mins and maxes)
    # if verbose:
    #     print('getting coordinates of tiles, including the buffer')
    buffer_coords = []
    for e, n in zip(easting, northing):
        buffer_coords.extend(get_buffer_coords(e, n, buffer))

    buffer_coords_rounded = [
        (round_down1000(c[0]), round_down1000(c[1])) for c in buffer_coords]
    # remove duplicate coordinates
    buffer_coords_set = list(set(buffer_coords_rounded))
    buffer_coords_set.sort()

    if verbose:
        print('Easting:', easting)
        print('Northing:', northing)
        print('Buffer:', buffer)
        print('UTM (x, y) lower-left coordinates of tiles to be downloaded:')
        for coord in buffer_coords_set:
            print(coord)

    # create the list of utm "easting_northing" strings that will be used to match to the tile names
    coord_strs = ['_'.join([str(c[0]), str(c[1])])
                  for c in buffer_coords_set]
    # print(coord_strs)

    # round down to get the lower left coordinate of the tile corresponding to the point
    # coord_tuples = [(easting[i], northing[i]) for i in range(0, len(easting))]
    # coord_tuples_floor = [(round_down1000(c[0]),round_down1000(c[1])) for c in coord_tuples]
    # easting_floor = [int(np.floor(e/1000)*1000) for e in easting]
    # northing_floor = [int(np.floor(n/1000)*1000) for n in northing]

    # subset by the tiles in the easting, northing lists
    # first get a list of the coordinate strings (easting_northing) to match
    # coord_strs = ['_'.join([str(e), str(n)])
    #               for e, n in zip(easting_floor, northing_floor)]

    # append the .txt file to include the README
    # coord_strs.append('.txt')
    coord_strs.append('.txt')

    # subset the dataframe to include only the coordinate strings matching coord_strs
    # if verbose:
    #     print('finding the tiles')
    file_url_df_subset = file_url_df[file_url_df['name'].str.contains(
        '|'.join(coord_strs))]

    file_url_df_subset2 = file_url_df_subset[~file_url_df_subset['name'].str.endswith(
        '.txt')]

    # if any coordinates were not included in the data, print a warning message
    # Warning: the following coordinates are outside the bounds of site-year:
    unique_coords_to_download = set(
        file_url_df_subset2['name'].str.extract(r'_(\d+_\d+)_')[0])

    coord_strs.remove('.txt')
    # compare two lists:
    coords_not_found = list(
        set(coord_strs).difference(list(unique_coords_to_download)))
    if len(coords_not_found) > 0:
        print('Warning, the following coordinates fall outside the bounds of the site, so will not be downloaded:')
        for coord in coords_not_found:
            print(','.join(coord.split('_')))

    # get the number of files in the dataframe, if there are no files to download, return
    num_files = len(file_url_df_subset)
    if num_files == 0:
        print("No data files found.")
        return

    # get the total size of all the files found
    download_size_bytes = file_url_df_subset['size'].sum()
    download_size = convert_byte_size(download_size_bytes)

    # ask whether to continue download, depending on size
    if check_size:
        if input(f"Continuing will download {num_files} files totaling approximately {download_size}. Do you want to proceed? (y/n) ") != "y":
            print("Download halted")
            return

    # create folder in working directory to put files in
    if save_path:
        download_path = Path(save_path) / dpid
    else:
        download_path = Path.cwd() / dpid
    # print('download path', download_path)
    download_path.mkdir(parents=True, exist_ok=True)

    # serially download all files, with progress bar
    files = list(file_url_df_subset['url'])
    print(
        f"Downloading {num_files} files totaling approximately {download_size}\n")
    sleep(1)
    # for file in tdqm(files): # if tdqm imports properly, this should work
    with Bar('Download Progress...', max=len(files)) as bar:
        for file in files:
            # try:
            download_file(file, download_path)
            bar.next()
        # except Exception as e:
        #     print(e)
        bar.finish()

    return

# request with suspended data (no data available)
# eg. https://data.neonscience.org/api/v0/products/DP3.30016.001
# suspended biomass data product
# productStatus: FUTURE
# releases: []
# siteCodes: NoneType object
