#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
import pyarrow as pa
from pyarrow import dataset
import zipfile
import platform
import glob
import re
import time
import tqdm
import importlib_resources
from datetime import datetime
import shutil
import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

from . import __resources__

# zippath = "C:/Users/nickerson/Downloads/NEON_sediment (6).zip"
# outpath = zippath[:-4]
# level = 'all'
# n_cores = 1

def unzip_zipfile_parallel(zippath,
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
    else:
        outpath=zippath[:-4]
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
               
        # Unzip file and get list of zips within
        zip_ref.extractall(outpath)
        zps = glob.glob(outpath+"/*.zip")
        
        # If there are more zips within parent zip file, unzip those as well
        if type(zps) == list:
            print('need an example to properly code this up.\n')
        else:
            zps = outpath
        
        return zps

def find_datatables(folder,
                    f_names=True):
    """

    Find data tables
    
    Parameters
    --------
    folder: The filepath location of the unzipped NEON download package folder.
    f_names: Full names - if true, then return the full file names including enclosing folders - if false, return only the file names
    
    Return
    --------
    A data frame of file names
    
    Example
    --------
    ZN NOTE: Insert example when function is coded
    
    >>> example
    
    Created on Wed Apr 17 2024
    
    @author: Zachary Nickerson
    """ 
    
    # get all .csv files in the folder and its subfolders
    csv_files = glob.glob(os.path.join(folder, '**', '*.csv'), recursive=True)
    
    # if fnames is True, return the full file paths; otherwise, return the base names
    if f_names:
        return csv_files
    else:
        return [os.path.basename(f) for f in csv_files]

def get_recent_publication(filepaths):
    """

    Returns the most recent files for those that do not need stacking
    
    Parameters
    --------
    in_list: List of file paths
    
    Return
    --------
    The filepath of the file with the most recent publication date
    
    Example
    --------
    ZN NOTE: Insert example when function is coded
    
    >>> example
    
    Created on Wed Apr 17 2024
    
    @author: Zachary Nickerson
    """ 
    
    # extract the publication dates from the file paths
    pub_dates = [re.search(r'20\d{2}\d{2}\d{2}', f) for f in filepaths]
    pub_dates = [m.group(0) for m in pub_dates if m is not None]

    # get the most recent publication date
    recent_pub_date = max(pub_dates)

    # get the file paths that include the most recent publication date
    recent_files = [f for f in filepaths if recent_pub_date in f]

    return recent_files

def get_variables(v):
    """

    Get correct data types
    
    Parameters
    --------
    var_path: A file that contains variable definition
    
    Return
    --------
    A pyarrow schema for data types based on the variables file
    
    Example
    --------
    ZN NOTE: Insert example when function is coded
    
    >>> example
    
    Created on Wed Apr 17 2024
    
    @author: Zachary Nickerson
    """    
    
    # function assumes variables are loaded as a pandas data frame.
    # would be best to move away from pandas
        
    # create pyarrow schema by translating NEON data types to pyarrow types
    # should probably do this with a dictionary instead of if statements
    for i in range(0, len(v)):
        nm = v.fieldName[i]
        if v.dataType[i]=="real":
            typ=pa.float32()
        if v.dataType[i] in ["integer", "unsigned integer", "signed integer"]:
            typ=pa.int32()
        if v.dataType[i] in ["string", "uri"]:
            typ = pa.string()
        if v.dataType[i] == "dateTime":
            if v.pubFormat[i] in ["yyyy-MM-dd'T'HH:mm:ss'Z'(floor)","yyyy-MM-dd'T'HH:mm:ss'Z'(round)"]:
                typ = pa.timestamp("s", tz="UTC")
            else:
                if v.pubFormat[i] in ["yyyy-MM-dd(floor)","yyyy-MM-dd"]:
                    typ = pa.date32()
                else:
                    typ = pa.string()
        if i==0:
            vschema=pa.schema([(nm, typ)])
        else:
            nfield=pa.field(nm, typ)
            vschema=vschema.append(nfield)
        
    return vschema


def table_type_formats(flname):
    """

    Small helper function to define mapping of table types to file name formats
    
    Parameters
    --------
    flname: A file name, split into components
    
    Return
    --------
    A table type
        
    Created on 6 May 2024
    
    @author: Claire Lunch
    """  
    
    flen=len(flname)
    if flen<=6:
        return "lab"
    else:
        ymr=re.compile("[0-9]{4}-[0-9]{2}")
        if any([f for f in flname if ymr.search(f)]):
            return "site-date"
        else:
            return "site-all"


def find_table_types(datatables):
    """

    Find unique data tables and their types
    
    Parameters
    --------
    datatables: A list of data files
    
    Return
    --------
    An array of unique table names and their types
        
    Created on 3 May 2024
    
    @author: Claire Lunch
    """  
    
    dt=[os.path.basename(d) for d in datatables]
    splitnames=[d.split(".") for d in dt]
    td=[]
    for i in range(0, len(splitnames)):
        for j in range(2, len(splitnames[i])):
            s=splitnames[i][j]
            if not s=="sensor_positions" and not s=="science_review_flags":
                if not "_" in s:
                    continue
                else:
                    ss=str.replace(s, "_pub", "")
                    td.append(ss)
                    
    if len(td)==0:
        logging.info("No data tables found, only metadata. Try downloading expanded package, and check availability on the NEON data portal.")
        return
    else:
        tn=list(set(td))
        
    tt={}
    for k in range(0, len(tn)):
        tnk=tn[k]
        tnkr=re.compile(tnk+"|"+tnk+"_pub")
        tnknames=[trnn for trnn in splitnames for tr in trnn if tnkr.search(tr)]
        ttklist=list(map(table_type_formats, tnknames))
        ttk=list(set(ttklist))
        if len(ttk)>1:
            raise ValueError("In files to be stacked, table {tnk} has been published under conflicting schedules. To avoid this problem, either work only with released data, or stack released and provisional data separately.")
            return
        else:
            tt[tnk]=ttk[0]
            
    return tt
    

def find_lab_names(flpths):
    """

    Small helper function to find names of labs from filenames of lap-specific files
    
    Parameters
    --------
    flpths: A list of file paths
    
    Return
    --------
    A list of unique lab names
        
    Created on 5 June 2024
    
    @author: Claire Lunch
    """  
    
    flnms = [os.path.basename(f) for f in flpths]
    splitnames = [f.split(".") for f in flnms]
    labnames = [f[1] for f in splitnames]
    return list(set(labnames))


def find_sites(flpths):
    """

    Small helper function to find sites from file names
    
    Parameters
    --------
    flpths: A list of file paths
    
    Return
    --------
    A list of unique sites
        
    Created on 5 June 2024
    
    @author: Claire Lunch
    """  
    
    flnms = [os.path.basename(f) for f in flpths]
    sr = re.compile("[.][A-Z]{4}[.]")
    sites = [sr.search(f).group(0) for f in flnms]
    sites = list(set(sites))
    sites = [re.sub(pattern="[.]", repl="", string=s) for s in sites]
    return sites


def remove_srf_dups(srftab):
    """

    Small helper function to remove duplicates and updated records from science review flag tables
    
    Parameters
    --------
    srftab: A pandas table of SRF records
    
    Return
    --------
    A de-duplicated pandas table of SRF records
        
    Created on 6 June 2024
    
    @author: Claire Lunch
    """  
    
    idset = list(set(srftab["srfID"]))
    srfsublist = []
    for i in idset:
        srfsubi = srftab[srftab.srfID==i]
        indi = srfsubi.idxmax()["lastUpdateDateTime"]
        srfsublist.append(srfsubi.loc[indi])
    srfsub = pd.DataFrame(srfsublist)
    return srfsub


def stack_data_files_parallel(folder,
                              package,
                              dpID,
                              n_cores=1,
                              progress=True
                              ):
    """

    Join data files in a unzipped NEON data package by table type
    
    Parameters
    --------
    folder: The filepath location of the unzipped NEON download package folder.
    dpID: Data product ID of product to stack.
    n_cores: The number of cores to parallelize the stacking procedure. To automatically use the maximum number of cores on your machine we suggest setting nCores=parallel::detectCores(). By default it is set to a single core. # Need to find python equivalent of parallelizing and update this input variable description.
    progress: Should a progress bar be displayed?
    
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
    
    # folder="C:/Users/nickerson/Downloads/NEON_elev-surfacewater"
    # package="expanded"
    # dpID="DP1.20016.001"
    
    starttime = datetime.now()
    messages = []
    releases = []
    
    dpnum = dpID[4:9]
    
    # Assuming 'folder' is defined
    # Get filenames without full path
    filenames = find_datatables(folder = folder,f_names=False)
    
    # Get filenames with full path
    filepaths = find_datatables(folder = folder,f_names=True)
    
    # Get release file, if it exists
    relfl = [i for i in filepaths if "release_status" in i]
    if len(relfl) == 1:
        reltab = pd.read_csv(relfl[0], encoding='utf-8')
    else:
        reltab = None    
    
    # handle per-sample tables separately ## ZN Note: Need to test specifically
    if dpID in ["DP1.30012.001", "DP1.10081.001", "DP1.20086.001","DP1.20141.001", "DP1.20190.001", "DP1.20193.001"] and len([f for f in filenames if not f.startswith("NEON.")]) > 0:
        framefiles = [f for f in filepaths if not os.path.basename(f).startswith("NEON.")]
        filepaths = [f for f in filepaths if os.path.basename(f).startswith("NEON.")]
        filenames = [f for f in filenames if os.path.basename(f).startswith("NEON.")]
        
        # stack frame files
        print("Stacking per-sample files. These files may be very large; download data in smaller subsets if performance problems are encountered.\n")
        
        stacked_files_folder = os.path.join(folder, "stackedFiles")
        if not os.path.exists(stacked_files_folder):
            os.makedirs(stacked_files_folder)
        
        frm = pd.concat([pd.read_csv(f).assign(fileName=os.path.basename(f)) for f in framefiles], ignore_index=True)
        
        if dpID == "DP1.20190.001":
            frm.to_csv(os.path.join(stacked_files_folder, "rea_conductivityRawData.csv"), index=False)
        elif dpID == "DP1.20193.001":
            frm.to_csv(os.path.join(stacked_files_folder, "sbd_conductivityRawData.csv"), index=False)
        else:
            frm.to_csv(os.path.join(stacked_files_folder, "per_sample.csv"), index=False)
    
    # make a dictionary, where filenames are the keys to the filepath values
    filelist = dict(zip(filenames, filepaths))
    
    datafls = filelist
    
    # if there are no datafiles, exit
    if len(datafls) == 0:
        print("No data files are present in specified file path.\n")
        return None
        
    # if there is one or more than one file, stack files
    n = 0
    m = 0
    if len(datafls) > 1:
        stacked_files_folder = os.path.join(folder, "stackedFiles")
        if not os.path.exists(stacked_files_folder):
            os.makedirs(stacked_files_folder) 
    # if there is just one data file (and thus one table name), copy file into stackedFiles folder
    if len(datafls) == 1:
        shutil.copy(list(datafls.values())[0], stacked_files_folder)
        m = 0
        n = 1   
        
    # get table types
    table_types=find_table_types(filenames)
    if any(re.search("sensor_positions", path) for path in filepaths):
        table_types["sensor_positions"]="site-all"
    if any(re.search("science_review_flags", path) for path in filepaths):
        table_types["science_review_flags"]="site-date"
    tables=list(table_types.keys())
    
    # metadata files
    # copy variables and validation files to /stackedFiles using the most recent publication date
    if any(re.search('variables.20', path) for path in filepaths):
        varpath = get_recent_publication([path for path in filepaths if "variables.20" in path])[0]
        v = pd.read_csv(varpath, sep=',')
        # if science review flags are present but missing from variables file, add variables
        if "science_review_flags" not in v['table']:
            if any("science_review_flags" in path for path in filepaths):
                science_review_file=(importlib_resources.files(__resources__)/"science_review_variables.csv")
                science_review_variables=pd.read_csv(science_review_file, index_col=None)
                v = pd.concat([v, science_review_variables], ignore_index=True)
        # # if sensor positions are present but missing from variables file, add variables
        # if "sensor_positions" not in v['table']:
        #     if any("sensor_positions" in path for path in filepaths):
        #         science_review_file=(importlib_resources.files(__resources__)/"science_review_variables.csv")
        #         science_review_variables=pd.read_csv(science_review_file, index_col=None)
        #         v = pd.concat([v, science_review_variables], ignore_index=True)
        vlist = {k: v for k, v in v.groupby('table')}
        # Write out the variables file
        v.to_csv(f"{folder}/stackedFiles/variables_{dpnum}.csv", index=False)
        varpath = f"{folder}/stackedFiles/variables_{dpnum}.csv"
        
    if any(re.search('validation', path) for path in filepaths):
        valpath = get_recent_publication([path for path in filepaths if "validation" in path])[0]
        shutil.copy(valpath, f"{folder}/stackedFiles/validation_{dpnum}.csv")
        messages.append("Copied the most recent publication of validation file to /stackedFiles")
        m+=1

    # copy categoricalCodes file to /stackedFiles using the most recent publication date
    if any(re.search('categoricalCodes', path) for path in filepaths):
        valpath = get_recent_publication([path for path in filepaths if "categoricalCodes" in path])[0]
        shutil.copy(valpath, f"{folder}/stackedFiles/categoricalCodes_{dpnum}.csv")
        messages.append("Copied the most recent publication of categoricalCodes file to /stackedFiles")
        m+=1
        
        
    # stack tables according to types
    for j in tqdm(tables, disable=not progress): 
        j='ais_maintenance'
        # create schema from variables file, for only this table and package
        # should we include an option to read in without schema if variables file is missing?
        arrowvars = dataset.dataset(source=varpath, format="csv")
        arrowv = arrowvars.to_table()
        vtab = arrowv.filter(pa.compute.field("table") == j)
        
        if package=="basic":
            vtabpkg = vtab.filter(pa.compute.field("downloadPkg") == "basic")
        else:
            vtabpkg = vtab
        
        tablepkgvar = vtabpkg.to_pandas()
        tableschema = get_variables(tablepkgvar)
        
        # subset the list of files to the relevant table
        tabler = re.compile("[.]"+j+"[.]|[.]"+j+"_pub[.]")
        tablepaths = [f for f in filepaths if tabler.search(f)]
        
        # subset the list of files for lab-specific tables:
        # get the most recent file from each lab
        if table_types[j]=="lab":
            labs = find_lab_names(tablepaths)
            labrecent = list()
            for k in labs:
                labr = re.compile(k)
                labpaths = [f for f in tablepaths if labr.search(f)]
                labrecent.append(get_recent_publication(labpaths)[0])
            tablepaths = labrecent
            
        # subset the list of files for site-all tables:
        # get the most recent file from each site
        if table_types[j]=="site-all":
            sites = find_sites(tablepaths)
            siterecent = list()
            for k in sites:
                sr = re.compile(k)
                sitepaths = [f for f in tablepaths if sr.search(f)]
                siterecent.append(get_recent_publication(sitepaths)[0])
            tablepaths = siterecent
        
        # read data and append file names
        dat = dataset.dataset(source=tablepaths,format="csv",schema=tableschema)
        cols = tableschema.names
        cols.append("__filename")
        dattab = dat.to_table(columns=cols)
        pdat = dattab.to_pandas()
        
        # # append publication date
        # pubr = re.compile("20[0-9]{6}T[0-9]{6}Z")
        # pubval = [pubr.search(p).group(0) for p in pdat["__filename"]]
        # pdat = pdat.assign(publicationDate = pubval)
        
        # append publication date and release
        pubrelr = re.compile("20[0-9]{6}T[0-9]{6}Z\\..*\\/")
        pubrelval = [pubrelr.search(p).group(0) for p in pdat["__filename"]]
        pubval = [re.sub("\\..*","",s) for s in pubrelval]
        relval = [re.sub(".*\\.","",s) for s in pubrelval]
        relval = [re.sub("\\/","",s) for s in relval]
        pdat = pdat.assign(publicationDate = pubval,
                           release = relval)
        
        # for IS products, append domainID, siteID, HOR, VER
        if not "siteID" in pdat.columns.to_list():
            
            dr = re.compile("D[0-1]{1}[0-9]{1}")
            domval = [dr.search(d).group(0) for d in pdat["__filename"]]
            pdat.insert(0, "domainID", domval)
            
            sr = re.compile("[.][A-Z]{4}[.]")
            sitel = [sr.search(s).group(0) for s in pdat["__filename"]]
            siteval = [re.sub(pattern="[.]", repl="", string=s) for s in sitel]
            pdat.insert(1, "siteID", siteval)
            
            if j != "sensor_positions":
            
                locr = re.compile("[.][0-9]{3}[.][0-9]{3}[.][0-9]{3}[.][0-9]{3}[.]")
                indxs = [locr.search(l).group(0) for l in pdat["__filename"]]
                hor = [indx[5:8] for indx in indxs]
                ver = [indx[9:12] for indx in indxs]
                pdat.insert(2, "horizontalPosition", hor)
                pdat.insert(3, "verticalPosition", ver)
                
            # also for IS tables, sort the table by site, then HOR/VER, then date, all ascending
            pdat.sort_values(by=['siteID','horizontalPosition','verticalPosition','endDateTime'],
                             ascending=[True,True,True,True],
                             inplace=True)

        # for OS tables, sory by site and activity end date
        ## ZN Question: How can I always identify the activity end date in a table b/c OS tables can have different terms for that variable?
        
        # for SRF files, remove duplicates and modified records
        if j == "science_review_flags":
            pdat = remove_srf_dups(pdat)

    
    
############################    
    
############################


def stack_by_table(filepath,
                   savepath=None, 
                   save_unzipped_files=False, 
                   n_cores=1,
                   progress=True
                   #useFasttime=False # Is there an equivalent in python?
                   ):
    """

    Join data files in a zipped NEON data package by table type.
    
    Parameters
    --------
    filepath: The location of the zip file.
    savepath: The location to save the output files to. (optional)
    save_unzipped_files: Should the unzipped monthly data folders be retained? (true/false)
    n_cores: The number of cores to parallelize the stacking procedure. To automatically use the maximum number of cores on your machine we suggest setting nCores=parallel::detectCores(). By default it is set to a single core. # Need to find python equivalent of parallelizing and update this input variable description.
    progress: Should a progress bar be displayed?
    
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
    
    # determine contents of filepath and unzip as needed
    # Is the filepath input a zip file or an unzipped file?
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
        logging.info('Data files are not present in the specified filepath.')
        return
    
    # Determine dpID
    # this regexpr allows for REV = .001 or .002
    dpID_listlist = []
    for f in range(len(files)):
        dpID_listlist.append(re.findall(re.compile("DP[1-4][.][0-9]{5}[.]00[1-2]{1}"),files[f]))
    dpID = [x for dpID_list in dpID_listlist for x in dpID_list]
    dpID = list(set(dpID))
    if not len(dpID) == 1:
        logging.info("Data product ID could not be determined. Check that filepath contains data files, from a single NEON data product.")
        return
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
        logging.info("This is an AOP data product, files cannot be stacked. Use by_file_aop() or by_tile_aop() to download data.")
        return
        
    # Error messafe for SAE data
    if dpID == 'DP4.00200.001':
        logging.info("This eddy covariance data product is in HDF5 format. Stack using stack_eddy()")
        return
        
    # Exceptions for digital hemispheric photos
    if dpID == 'DP1.10017.001' and package == 'expanded':
        save_unzipped_files = True
        logging.info("Note: Digital hemispheric photos (in NEF format) cannot be stacked; only the CSV metadata files will be stacked.")
        
    # Warning about all sensor soil data
    if dpID in ['DP1.00094.001','DP1.00041.001'] and len(files) > 24:
        logging.info("Warning! Attempting to stack soil sensor data. Note that due to the number of soil sensors at each site, data volume is very high for these data. Consider dividing data processing into chunks, using the nCores= parameter to parallelize stacking, and/or using a high-performance system.")
    
    # If all checks pass, unzip and stack files
    
    # If the filepath is a zip file
    envt = 0
    if not folder:
        if savepath is None:
            savepath = filepath[:-4]
        if savepath == "envt":
            savepath = os.path.join(os.getcwd(), "store" + time.strftime("%Y%m%d%H%M%S"))
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
            savepath = os.path.join(os.getcwd(), "store" + time.strftime("%Y%m%d%H%M%S"))
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
                    

        
        
            
            

  
    
    
    
    #