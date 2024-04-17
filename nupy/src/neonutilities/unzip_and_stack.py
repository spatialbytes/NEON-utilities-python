#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import zipfile
import platform
import glob
import re
import tempfile
import time
import shutil


zippath = "C:/Users/nickerson/Downloads/NEON_sediment (6).zip"
outpath = zippath[:-4]
level = 'all'
n_cores = 1

def unzip_zipfile_parallel(zippath,
                           outpath=zippath[:-4],
                           level='all',
                           n_cores=1):
    """

    Unzip a zip file either at just the top level or recursively through the file.
    
    Parameters
    --------
    zippath: The filepath of the input file.
    outpath: The name of the folder to save unpacked files to. Defaults to a directory with the same path as the input zip file.
    level: Whether the unzipping should occur only for the 'top' zip file, or unzip 'all' recursively, or only files 'in' the folder specified. Defaults to 'all'.
    n_cores: Number of cores to use for parallelization. Defaults to 1.
    
    Return
    --------
    A list of unzipped files to be used in stack_by_table
    
    Example
    --------
    ZN NOTE: Insert example when function is coded
    
    >>> example
    
    Created on Tue Mar 5 2024
    
    @author: Zachary Nickerson
    """    
    
    # Error handling on inputs
    if not zippath[-4:] in ['.zip','.ZIP']:
        print('Zip file read failed because zippath must be a file path to a compressed zip file (file type .zip or .ZIP).\n')
        return None
    if not level in ['top','all','in']:
        print('Unzipping failed because level must be one of the followin options: all, in, top.\n')
        return None
    if not isinstance(n_cores, int):
        print('Unzipping in parellel failed because n_cores must be an integer.\n')
        return None
    
    if level == 'all':
        zip_ref = zipfile.ZipFile(zippath,'r')
        tl = zip_ref.namelist()
        
        # Error handling for filepath character lengths
        if any(len(x) > 260 for x in tl) and platform.system() == "Windows":
            print('Longest filepath is ' + str(len(max(tl, key=len))) + ' characters long. Filepaths on Windows are limited to 260 characters. Move files closer to the root directory.')
            return None
        if any(len(x) > 255 for x in tl) and platform.system() == "Darwin":
            print('Longest filepath is ' + str(len(max(tl, key=len))) + ' characters long. Filepaths on Mac are limited to 255 characters. Move files closer to the root directory.')
            return None
        
        # Unzip file and get list of zips within
        zip_ref.extractall(outpath)
        zps = glob.glob(outpath+"/*.zip")
        
        # If there are more zips within parent zip file, unzip those as well
        if type(zps) == list:
            print('need an example to properly code this up.\n')
        else:
            zps = outpath
        
        return zps
       
def stack_data_files_parallel(folder,
                              n_cores=1,
                              dpID
                              ):
    """

    Join data files in a unzipped NEON data package by table type
    
    Parameters
    --------
    folder: The filepath location of the unzipped NEON download package folder.
    dpID: Data product ID of product to stack. Ignored and determined from data unless input is a vector of files.
    n_cores: The number of cores to parallelize the stacking procedure. To automatically use the maximum number of cores on your machine we suggest setting nCores=parallel::detectCores(). By default it is set to a single core. # Need to find python equivalent of parallelizing and update this input variable description.
    
    Return
    --------
    One file for each table type is created and written.
    
    Example
    --------
    ZN NOTE: Insert example when function is coded
    
    >>> example
    
    Created on Tue Apr 2 2024
    
    @author: Zachary Nickerson
    """  
    
    starttime = time.localtime()
    
############################    
    
############################

# filepath=zps
filepath=zippath
savepath=None
save_unzipped_files=False
dpID=None
package=None 
n_cores=1

def stack_by_table(filepath,
                   savepath=None, 
                   save_unzipped_files=False, 
                   dpID=None, 
                   package=None, 
                   n_cores=1,
                   #useFasttime=False # Is there an equivalent in python?
                   ):
    """

    Join data files in a zipped NEON data package by table type.
    
    Parameters
    --------
    filepath: The location of the zip file.
    savepath: The location to save the output files to. (optional)
    save_unzipped_files: Should the unzipped monthly data folders be retained? (true/false)
    dpID: Data product ID of product to stack. Ignored and determined from data unless input is a vector of files. (optional)
    package: Data download package, either basic or expanded. Ignored and determined from data unless input is a vector of files. (optional)
    n_cores: The number of cores to parallelize the stacking procedure. To automatically use the maximum number of cores on your machine we suggest setting nCores=parallel::detectCores(). By default it is set to a single core. # Need to find python equivalent of parallelizing and update this input variable description.
    
    Return
    --------
    All files are unzipped and one file for each table type is created and written. If savepath="envt" is specified, output is a named list of tables; otherwise, function output is null and files are saved to the location specified.
    
    Example
    --------
    ZN NOTE: Insert example when function is coded
    
    >>> example
    
    Created on Tue Mar 5 2024
    
    @author: Zachary Nickerson
    """  
    
    # Is the filepath input a list, a zip file, or an upzipped file?
    if type(filepath) == list:
        folder = 'ls'
        save_unzipped_files = False
    else:
        if filepath[-4:] in ['.zip','.ZIP']:
            folder = False
        else:
            folder = True
    
    # Check whether data should be stacked
    if not folder:
        zip_ref = zipfile.ZipFile(filepath,'r')
        files = zip_ref.namelist()
    else:
        files = glob.glob(filepath+'/**',recursive=True)
        
    # Error handling if there are no standardized NEON Portal data tables in the list of files
    if not any(re.search(r'NEON.D[0-9]{2}.[A-Z]{4}.',x) for x in files):
        print('Data files are not present in the specified filepath.\n')
        return
    
    # If the input is a list of files
    if folder == 'ls':
        if dpID is None:
            print('dpID must be provided when input is not a single filepath.\n')
            return None
        if package is None:
            print('package (basic or expanded) must be provided when input is not a single filepath.\n')
            return None
        files = filepath
        if len(files) == 0:
            print('Data files are not present in the specified filepath.\n')
            return None
        if not any(os.path.isfile(x) for x in files):
            print("Files not found in specified filepaths. Check that the input list contains the full filepaths.\n")
            return None
    # If the files are in a folder or zipfile
    else:
        # Determine dpID
        # this regexpr allows for REV = .001 or .002
        dpID_listlist = []
        for f in range(len(files)):
            dpID_listlist.append(re.findall(re.compile("DP[1-4][.][0-9]{5}[.]00[1-2]{1}"),files[f]))
        dpID = [x for dpID_list in dpID_listlist for x in dpID_list]
        dpID = list(set(dpID))
        if not len(dpID) == 1:
            print("Data product ID could not be determined. Check that filepath contains data files, from a single NEON data product.\n")
            return None
        else:
            dpID = dpID[0]
        # Determine download package
        package_listlist = []
        for f in range(len(files)):
            package_listlist.append(re.findall(re.compile("basic|expanded"),files[f]))
        package = [x for package_list in package_listlist for x in package_list]
        package = list(set(package))
        if 'expanded' in package:
            package = 'expanded'
        else:
            package = 'basic'
            
    # Error message for AOP data
    if dpID[4] == '3' and not dpID == 'DP1.30012.001':
        print("This is an AOP data product, files cannot be stacked. Use by_file_aop() or by_tile_aop() if you would like to download data.\n")
        
    # # Error messafe for SAE data
    # if dpID == 'DP4.00200.001':
    #     print("This eddy covariance data product is in HDF5 format. Stack using stack_eddy()")
    
    # Code for using fasttime?
    
    # Exceptions for digital hemispheric photos
    if dpID == 'DP1.10017.001' and package == 'expanded':
        save_unzipped_files = True
        print("Note: Digital hemispheric photos (in NEF format) cannot be stacked; only the CSV metadata files will be stacked.\n")
        
    # Warning about all sensor soil data
    if dpID in ['DP1.00094.001','DP1.00041.001'] and len(files) > 24:
        print("Warning! Attempting to stack soil sensor data. Note that due to the number of soil sensors at each site, data volume is very high for these data. Consider dividing data processing into chunks, using the nCores= parameter to parallelize stacking, and/or using a high-performance system.")
    
    # If all checks pass, stack files
    
    # If the filepath is a zip file
    envt = 0
    if not folder:
        if savepath is None:
            savepath = filepath[:-4]
        if savepath == "envt":
            savepath = os.path.join(tempfile.gettempdir(), "store" + time.strftime("%Y%m%d%H%M%S"))
            envt = 1
        if re.search(".zip", files):
            ziplist = unzip_zipfile_parallel(zippath = filepath, outpath = savepath)
        else:
            if not os.path.exists(savepath):
                os.makedirs(savepath)
            if envt == 0:
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    zip_ref.extractall(savepath.parent)
            else:
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    zip_ref.extractall(savepath)
            ziplist = os.listdir(savepath)
            ziplist = [file for file in ziplist if re.search("NEON[.]D[0-9]{2}[.][A-Z]{4}[.]DP[0-4]{1}[.]", file)]
    
    if folder:
        if savepath is None:
            savepath = filepath
        if savepath == "envt":
            savepath = os.path.join(tempfile.gettempdir(), "store" + time.strftime("%Y%m%d%H%M%S"))
            envt = 1
        ziplist = files
        if any(".zip" in file for file in files):
            unzip_zipfile_parallel(zippath=filepath, outpath=savepath, level="in")
        else:
            if filepath != savepath:
                if not os.path.exists(savepath):
                    os.makedirs(savepath)
                for i in files:
                    shutil.copy(os.path.join(filepath, i), savepath)
                    
    if folder == "ls":
        if savepath == "envt":
            envt = 1
        if savepath is None or savepath == "envt":
            finalpath = os.path.dirname(files[0])
        else:
            finalpath = savepath
        if not os.path.exists(finalpath):
            os.makedirs(finalpath)
        
        if all(".zip" in file for file in files):
            fols = [unzip(file, os.path.join(finalpath, os.path.basename(file)[:-4])) for file in files]
            files = [os.path.basename(fol)[:-4] for fol in fols]
        else:
            if sum(".zip" in file for file in files) > len(files) / 5:
                print("There are a large number of zip files in the input list.\nFiles are only unzipped if all input files are zip files.\n")
        if any(".zip" in file for file in files):
            files = [file for file in files if ".zip" not in file]
        savepath = os.path.join(tempfile.gettempdir(), "store" + time.strftime("%Y%m%d%H%M%S"))
        os.makedirs(savepath, exist_ok=True)
        for i in files:
            shutil.copy(i, savepath)

        
        
            
            

  
    
    
    
    #