#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import zipfile
import platform
import glob
import re


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
        return
    if not level in ['top','all','in']:
        print('Unzipping failed because level must be one of the followin options: all, in, top.\n')
        return
    if not isinstance(n_cores, int):
        print('Unzipping in parellel failed because n_cores must be an integer.\n')
        return
    
    if level == 'all':
        zip_ref = zipfile.ZipFile(zippath,'r')
        tl = zip_ref.namelist()
        
        # Error handling for filepath character lengths
        if any(len(x) > 260 for x in tl) and platform.system() == "Windows":
            print('Longest filepath is ' + str(len(max(tl, key=len))) + ' characters long. Filepaths on Windows are limited to 260 characters. Move files closer to the root directory.')
            return
        if any(len(x) > 255 for x in tl) and platform.system() == "Darwin":
            print('Longest filepath is ' + str(len(max(tl, key=len))) + ' characters long. Filepaths on Mac are limited to 255 characters. Move files closer to the root directory.')
            return
        
        # Unzip file and get list of zips within
        zip_ref.extractall(outpath)
        zps = glob.glob(outpath+"/*.zip")
        
        # If there are more zips within parent zip file, unzip those as well
        if type(zps) == list:
            print('need an example to properly code this up.\n')
        else:
            zps = outpath
        
        return(zps)
        
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
    if folder == False:
        zip_ref = zipfile.ZipFile(filepath,'r')
        files = zip_ref.namelist()
        pattern = re.compile('NEON.D[0-9]{2}.[A-Z]{4}.')
        files = [s for s in files if pattern.match(s)]
    
    
    #
    
    
    
    
    
    
    
    
    
    #