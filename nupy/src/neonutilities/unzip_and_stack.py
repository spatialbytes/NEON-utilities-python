#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def unzip_zipfile_parallel(zippath,
                           outpath,# substr(zippath, 1, nchar(zippath)-4) << convert R code
                           level='all',
                           n_cores=1):
    """

    Unzip a zip file either at just the top level or recursively through the file.
    
    Parameters
    --------
    zip_path: The filepath of the input file.
    out_path: The name of the folder to save unpacked files to.
    level: Whether the unzipping should occur only for the 'top' zip file, or unzip 'all' recursively, or only files 'in' the folder specified.
    n_cores: Number of cores to use for parallelization.
    
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
    
    
    
