#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
import pyarrow as pa
from pyarrow import dataset
from pyarrow import fs
import zipfile
import platform
import glob
import re
import importlib_resources
from tqdm import tqdm
from .tabular_download import zips_by_product
from .get_issue_log import get_issue_log
from .citation import get_citation
from .helper_mods.api_helpers import readme_url
import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

from . import __resources__

varschema = pa.schema([
    ('table', pa.string()),
    ('fieldName', pa.string()),
    ('description', pa.string()),
    ('dataType', pa.string()),
    ('units', pa.string()),
    ('sampleCode', pa.string()),
    ('downloadPkg', pa.string()),
    ('pubFormat', pa.string()),
    ('primaryKey', pa.string()),
    ('categoricalCodeName', pa.string())
])


def unzip_zipfile_parallel(zippath,
                           n_cores=1):
    """

    Unzip a zip file either at just the top level or recursively through the file.
    
    Parameters
    --------
    zippath: The filepath of the input file.
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
    if zippath[-4:] in ['.zip','.ZIP']:
        outpath = os.path.dirname(zippath)
        level = "all"
    else:
        outpath = zippath
        level = "in"
    if not isinstance(n_cores, int):
        n_cores = 1
    
    if level == "all":
        zip_ref = zipfile.ZipFile(zippath,'r')
        tl = zip_ref.namelist()
        
        # Error handling for filepath character lengths
        if any(len(x) > 260 for x in tl) and platform.system() == "Windows":
            print('Longest filepath is ' + str(len(max(tl, key=len))) + ' characters long. Filepaths on Windows are limited to 260 characters. Move files closer to the root directory.')
            return None
               
        # Unzip file and get list of zips within
        zip_ref.extractall(path=outpath)
        zps = glob.glob(zippath[:-4]+"/*.zip")
        
        # If there are more zips within parent zip file, unzip those as well
        # does this happen anymore? this might be deprecated.
        # level as an input might also be deprecated
        if len(zps) > 0:
            print('need an example to properly code this up.\n')
        
    if level == "in":
        zps = glob.glob(outpath+"/*.zip")
        
        for i in range(0, len(zps)):
            zip_refi = zipfile.ZipFile(zps[i],'r')
            outpathi = zps[i][:-4]
            zip_refi.extractall(path=outpathi)
            os.remove(path=zps[i])
        
    return None

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
    pub_dates = [re.search(r'20\d{2}\d{2}\d{2}', os.path.basename(f)) for f in filepaths]
    pub_dates = [m.group(0) for m in pub_dates if m is not None]

    # get the most recent publication date
    recent_pub_date = max(pub_dates)

    # get the file paths that include the most recent publication date
    recent_files = [f for f in filepaths if recent_pub_date in os.path.basename(f)]

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
        
    # create pyarrow schema by translating NEON data types to pyarrow types
    for i in range(0, len(v)):
        nm = v.fieldName[i]
        typ = pa.string()
        if v.dataType[i]=="real":
            typ = pa.float32()
        if v.dataType[i] in ["integer", "unsigned integer", "signed integer"]:
            typ = pa.int32()
        if v.dataType[i] in ["string", "uri"]:
            typ = pa.string()
        if v.dataType[i] == "dateTime":
            if v.pubFormat[i] in ["yyyy-MM-dd'T'HH:mm:ss'Z'(floor)","yyyy-MM-dd'T'HH:mm:ss'Z'","yyyy-MM-dd'T'HH:mm:ss'Z'(round)"]:
                typ = pa.timestamp("s", tz="UTC")
            else:
                if v.pubFormat[i] in ["yyyy-MM-dd(floor)","yyyy-MM-dd"]:
                    typ = pa.date32()
                else:
                    if v.pubFormat[i] in ["yyyy(floor)", "yyyy(round)"]:
                        typ=pa.int32()
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

def format_readme(readmetab,
                  tables):
    """

    Remove site-specific information from the most recently published readme file in the download, and add generic information about the neonutilities download.
    
    Parameters
    --------
    readmetab:  A readme document as a pandas table
    tables: A list of data tables included in download
    
    Return
    --------
    A modified readme file formatted to remove site-specific information and include standard information about the neonutilities download
    
    Example
    --------
    ZN NOTE: Insert example when function is coded
    
    >>> example
    
    Created on Fri Jul 12 2024
    
    @author: Zachary Nickerson
    """  
    
    rd = readmetab
    if len(tables) > 0:
        # replace query specific text
        dpackind = rd[0].str.contains('CONTENTS').idxmax()
        rd.loc[dpackind + 2, 0] = f"This data product contains up to {len(tables)} data tables:"
        rd.loc[dpackind + 3: dpackind + 3 + len(tables)-1, 0] = tables
        rd.loc[dpackind + 3 + len(tables), 0] = "If data are unavailable for the particular sites and dates queried, some tables may be absent."
        qind = rd[0].str.contains('QUERY').idxmax()
        downpackind = rd[0].str.contains('Basic download package').idxmax()
        
        # Remove specific rows
        remove_indices = list(range(qind, dpackind)) + list(range(dpackind + 4 + len(tables), downpackind)) + rd.index[rd[0].str.contains("Date-Time")].tolist()
        remove_indices = [index for index in remove_indices if index in list(rd.index)]
        rd = rd.drop(remove_indices)
        
        # add disclaimer
        disclaimer = pd.DataFrame({0:["###################################",
                                      "########### Disclaimer ############",
                                      "This is the most recent readme publication based on all site-date combinations used during stackByTable.",
                                      "Information specific to the query, including sites and dates, has been removed. The remaining content reflects general metadata for the data product.",
                                      "##################################"]})
        rd = pd.concat([disclaimer,rd], ignore_index=True)
    return(rd)

def stack_data_files_parallel(folder,
                              package,
                              dpid,
                              n_cores=1,
                              progress=True,
                              cloud_mode=False
                              ):
    """

    Join data files in a unzipped NEON data package by table type
    
    Parameters
    --------
    folder: The filepath location of the unzipped NEON download package folder.
    dpid: Data product ID of product to stack.
    n_cores: The number of cores to parallelize the stacking procedure. To automatically use the maximum number of cores on your machine we suggest setting nCores=parallel::detectCores(). By default it is set to a single core. # Need to find python equivalent of parallelizing and update this input variable description.
    progress: Should a progress bar be displayed?
    cloud_mode: cloud_mode: Use cloud mode to transfer files cloud-to-cloud? If used, stack_by_table() expects a list of file urls as input. Defaults to False.
    
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
        
    releases = []
    
    dpnum = dpid[4:9]
    
    if cloud_mode:
        filenames = [os.path.basename(f) for f in folder]
        filepaths = folder
        gcs = fs.GcsFileSystem(anonymous=True)
    else:
        # Get filenames without full path
        filenames = find_datatables(folder = folder,f_names=False)
        
        # Get filenames with full path
        filepaths = find_datatables(folder = folder,f_names=True)
            
    # dictionary for outputs
    stacklist = {}

    
    # handle per-sample (data frame) tables separately
    if dpid in ["DP1.30012.001", "DP1.10081.001", "DP1.20086.001","DP1.20141.001", "DP1.20190.001", "DP1.20193.001"] and len([f for f in filenames if not f.startswith("NEON.")]) > 0:
        framefiles = [f for f in filepaths if not os.path.basename(f).startswith("NEON.")]
        filepaths = [f for f in filepaths if os.path.basename(f).startswith("NEON.")]
        filenames = [f for f in filenames if os.path.basename(f).startswith("NEON.")]
        
        # stack frame files
        logging.info("Stacking per-sample files. These files may be very large; download data in smaller subsets if performance problems are encountered.\n")
        
        # no variables files for these, have to let arrow infer. problem?
        fdat = dataset.dataset(source=framefiles,format="csv")
        fdattab = fdat.to_table()
        fpdat = fdattab.to_pandas()
                
        if dpid == "DP1.20190.001":
            stacklist["rea_conductivityRawData"] = fpdat
        elif dpid == "DP1.20193.001":
            stacklist["sbd_conductivityRawData"] = fpdat
        else:
            stacklist["per_sample"] = fpdat
    
    
    # make a dictionary, where filenames are the keys to the filepath values
    filelist = dict(zip(filenames, filepaths))
    
    datafls = filelist
    
    # if there are no datafiles, exit
    if len(datafls) == 0:
        print("No data files are present in specified file path.\n")
        return None
        
    # if there is one or more than one file, stack files
        
    # get table types
    table_types=find_table_types(filenames)
    if any(re.search("sensor_positions", path) for path in filepaths):
        table_types["sensor_positions"]="site-all"
    if any(re.search("science_review_flags", path) for path in filepaths):
        table_types["science_review_flags"]="site-date"
    tables=list(table_types.keys())
    
    # metadata files
    # get variables and validation files using the most recent publication date
    if any(re.search('variables.20', path) for path in filepaths):
        varpath = get_recent_publication([path for path in filepaths if "variables.20" in path])[0]
        if cloud_mode:
            vp = dataset.dataset(source=re.sub("https://storage.googleapis.com/", "", varpath),
                                 filesystem=gcs, format="csv", schema=varschema)
            va = vp.to_table()
            v = va.to_pandas()
        else:
            v = pd.read_csv(varpath, sep=',')

        # if science review flags are present but missing from variables file, add variables
        if "science_review_flags" not in list(v["table"]):
            if any("science_review_flags" in path for path in filepaths):
                science_review_file=(importlib_resources.files(__resources__)/"science_review_variables.csv")
                science_review_variables=pd.read_csv(science_review_file, index_col=None)
                v = pd.concat([v, science_review_variables], ignore_index=True)

        # if sensor positions are present but missing from variables file, add variables
        if "sensor_positions" not in list(v["table"]):
            if any("sensor_positions" in path for path in filepaths):
                sensor_positions_file=(importlib_resources.files(__resources__)/"sensor_positions_variables.csv")
                sensor_positions_variables=pd.read_csv(sensor_positions_file, index_col=None)
                v = pd.concat([v, sensor_positions_variables], ignore_index=True)

        # save the variables file
        vlist = {k: v for k, v in v.groupby("table")}
        stacklist[f"variables_{dpnum}"] = v
        
    # get validation file
    if any(re.search('validation', path) for path in filepaths):
        valpath = get_recent_publication([path for path in filepaths if "validation" in path])[0]
        if cloud_mode:
            vp = dataset.dataset(source=re.sub("https://storage.googleapis.com/", "", valpath),
                                 filesystem=gcs, format="csv", schema=None)
            va = vp.to_table()
            val = va.to_pandas()
        else:
            val = pd.read_csv(valpath, sep=',')
        stacklist[f"validation_{dpnum}"] = val

    # get categoricalCodes file
    if any(re.search('categoricalCodes', path) for path in filepaths):
        ccpath = get_recent_publication([path for path in filepaths if "categoricalCodes" in path])[0]
        if cloud_mode:
            cp = dataset.dataset(source=re.sub("https://storage.googleapis.com/", "", ccpath),
                                 filesystem=gcs, format="csv", schema=None)
            ca = cp.to_table()
            cc = ca.to_pandas()
        else:
            cc = pd.read_csv(ccpath, sep=',')
        stacklist[f"categoricalCodes_{dpnum}"] = cc
        
    # get readme file
    if any(re.search('readme.20', path) for path in filepaths):
        readmepath = get_recent_publication([path for path in filepaths if "readme.20" in path])[0]
        if cloud_mode:
            rd = readme_url(readmepath)
        else:
            rd = pd.read_table(readmepath, delimiter='\t', header=None)
        rd = format_readme(rd,tables)      
        # save the readme
        stacklist[f"readme_{dpnum}"] = rd
        
    # stack tables according to types
    if progress:
        logging.info("Stacking data files")
    arrowvars = pa.Table.from_pandas(stacklist[f"variables_{dpnum}"])
    for j in tqdm(tables, disable=not progress): 

        # create schema from variables file, for only this table and package
        # should we include an option to read in without schema if variables file is missing?
        vtab = arrowvars.filter(pa.compute.field("table") == j)
        
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
        if cloud_mode:
            tablebuckets = [re.sub(pattern="https://storage.googleapis.com/", 
                                   repl="", string=b) for b in tablepaths]
            dat = dataset.dataset(source=tablebuckets, filesystem=gcs, 
                                  format="csv", schema=tableschema)

        else:
            dat = dataset.dataset(source=tablepaths,
                                  format="csv", schema=tableschema)
            
        cols = tableschema.names
        cols.append("__filename")
        dattab = dat.to_table(columns=cols)
        pdat = dattab.to_pandas()
                
        # append publication date
        pubr = re.compile("20[0-9]{6}T[0-9]{6}Z")
        pubval = [pubr.search(os.path.basename(p)).group(0) for p in pdat["__filename"]]
        pdat = pdat.assign(publicationDate = pubval)
        
        # append release tag
        if not cloud_mode:
            pubrelr = re.compile("20[0-9]{6}T[0-9]{6}Z\\..*\\/")
            pubrelval = [pubrelr.search(p).group(0) for p in pdat["__filename"]]
            relval = [re.sub(".*\\.","",s) for s in pubrelval]
            relval = [re.sub("\\/","",s) for s in relval]
            pdat = pdat.assign(release = relval)
            releases.append(list(set(relval)))
        
        # append fields to variables file
        if f"variables_{dpnum}" in stacklist.keys():
            added_fields_file = (importlib_resources.files(__resources__)/"added_fields.csv")
            added_fields = pd.read_csv(added_fields_file, index_col=None)
            added_fields_all = added_fields[-2:]
            added_fields_all.insert(0,"table",j)
            vlist[j] = pd.concat([vlist[j], added_fields_all], ignore_index=True)
        
        # for IS products, append domainID, siteID, HOR, VER
        if not "siteID" in pdat.columns.to_list() and not table_types[j]=="lab":
            
            dr = re.compile("D[0-2]{1}[0-9]{1}")
            domval = [dr.search(d).group(0) for d in pdat["__filename"]]
            pdat.insert(0, "domainID", domval)
            
            sr = re.compile("D[0-9]{2}[.][A-Z]{4}[.]")
            sitel = [sr.search(s).group(0) for s in pdat["__filename"]]
            siteval = [re.sub(pattern="D[0-9]{2}[.]|[.]", repl="", string=s) for s in sitel]
            pdat.insert(1, "siteID", siteval)
            
            if j != "sensor_positions":
            
                locr = re.compile("[.][0-9]{3}[.][0-9]{3}[.][0-9]{3}[.][0-9]{3}[.]")
                indxs = [locr.search(l).group(0) for l in pdat["__filename"]]
                hor = [indx[5:8] for indx in indxs]
                ver = [indx[9:12] for indx in indxs]
                pdat.insert(2, "horizontalPosition", hor)
                pdat.insert(3, "verticalPosition", ver)
                
                # sort the table by site, then HOR/VER, then date, all ascending
                pdat.sort_values(by=['siteID','horizontalPosition','verticalPosition','endDateTime'],
                                 ascending=[True,True,True,True],
                                 inplace=True, ignore_index=True)
                
                # append fields to variables file
                if f"variables_{dpnum}" in stacklist.keys():
                    added_fields_IS = added_fields[0:4]
                    added_fields_IS.insert(0,"table",j)
                    vlist[j] = pd.concat([added_fields_IS, vlist[j]], ignore_index=True)
                    
        else:
            # for OS tables, sort by site and date
            pcols = pdat.columns.to_list()
            datevar = None
            if 'collectDate' in pcols:
                datevar = 'collectDate'
            else:
                if 'endDate' in pcols:
                    datevar = 'endDate'
                else:
                    if 'startDate' in pcols:
                        datevar = 'startDate'
                    else:
                        if 'date' in pcols:
                            datevar = 'date'
                        else:
                            if 'startDateTime' in pcols:
                                datevar = 'startDateTime'
            # sort the table by site then date, all ascending
            try:
                if datevar is None:
                    pdat.sort_values(by=['siteID'],
                                     ascending=[True],
                                     inplace=True, ignore_index=True)
                else:
                    pdat.sort_values(by=['siteID',datevar],
                                     ascending=[True,True],
                                     inplace=True, ignore_index=True)
            except:
                pass
        
        # for SRF files, remove duplicates and modified records
        if j == "science_review_flags":
            pdat = remove_srf_dups(pdat)
            
        # remove filename column
        pdat = pdat.drop(columns=["__filename"])

        # add table to list
        stacklist[j] = pdat
        
    # final variables file
    stacklist[f"variables_{dpnum}"] = pd.concat(vlist, ignore_index=True)
        
    # get issue log table
    # token omitted here since it's not otherwise used in stacking functions
    # consider a runLocal option, like in R stackEddy()
    stacklist[f"issueLog_{dpnum}"] = get_issue_log(dpid=dpid, token=None)
    
    # get relevant citation(s)
    try:
        releases = sum(releases, [])
        releases = list(set(releases))
        if "PROVISIONAL" in releases:
            try:
                stacklist[f"citation_{dpnum}_PROVISIONAL"] = get_citation(dpid=dpid, release="PROVISIONAL")
            except:
                pass
        relr = re.compile("RELEASE-20[0-9]{2}")
        rs = [relr.search(r).group(0) for r in releases if relr.search(r)]
        if len(rs)==1:
            stacklist[f"citation_{dpnum}_{rs[0]}"] = get_citation(dpid=dpid, release=rs[0])
        if len(rs)>1:
            logging.info("Multiple data releases were stacked together. This is not appropriate, check your input data.")
    except:
        pass
    
    return stacklist
    
############################    
    
############################


def stack_by_table(filepath,
                   savepath=None, 
                   save_unzipped_files=False, 
                   n_cores=1,
                   progress=True,
                   cloud_mode=False
                   ):
    """

    Join data files in a zipped or unzipped NEON data package by table type.
    
    Parameters
    --------
    filepath: The location of the zip file or downloaded files.
    savepath: The location to save the output files to. (optional)
    save_unzipped_files: Should the unzipped monthly data folders be retained? (true/false)
    n_cores: The number of cores to parallelize the stacking procedure. To automatically use the maximum number of cores on your machine we suggest setting nCores=parallel::detectCores(). By default it is set to a single core. # Need to find python equivalent of parallelizing and update this input variable description.
    progress: Should a progress bar be displayed?
    cloud_mode: Use cloud mode to transfer files cloud-to-cloud? If used, stack_by_table() expects a list of file urls as input. Defaults to False.
    
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
    if cloud_mode:
        files = filepath
    else:
        # Is the filepath input a zip file or an unzipped file?
        if filepath[-4:] in ['.zip','.ZIP']:
            folder = False
        else:
            folder = True
        
        # Get list of files nested (and/or zipped) in filepath
        if not folder:
            zip_ref = zipfile.ZipFile(filepath,'r')
            files = zip_ref.namelist()
        else:
            files = glob.glob(filepath+'/**',recursive=True)
        
    # Error handling if there are no standardized NEON Portal data tables in the list of files
    if not any(re.search(r'NEON.D[0-9]{2}.[A-Z]{4}.',x) for x in files):
        logging.info('Data files are not present in the specified filepath.')
        return
    
    # Determine dpid
    # this regexpr allows for REV = .001 or .002
    dpid_listlist = []
    for f in range(len(files)):
        dpid_listlist.append(re.findall(re.compile("DP[1-4][.][0-9]{5}[.]00[1-2]{1}"),files[f]))
    dpid = [x for dpid_list in dpid_listlist for x in dpid_list]
    dpid = list(set(dpid))
    if not len(dpid) == 1:
        logging.info("Data product ID could not be determined. Check that filepath contains data files, from a single NEON data product.")
        return
    else:
        dpid = dpid[0]
        
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
    if dpid[4] == '3' and not dpid == 'DP1.30012.001':
        logging.info("This is an AOP data product, files cannot be stacked. Use by_file_aop() or by_tile_aop() to download data.")
        return
        
    # Error messafe for SAE data
    if dpid == 'DP4.00200.001':
        logging.info("This eddy covariance data product is in HDF5 format. Stack using the stackEddy() function in the R package version of neonUtilities.")
        return
        
    # Exceptions for digital hemispheric photos
    if dpid == 'DP1.10017.001' and package == 'expanded':
        save_unzipped_files = True
        logging.info("Note: Digital hemispheric photos (in NEF format) cannot be stacked; only the CSV metadata files will be stacked.")
        
    # Warning about all sensor soil data
    # Test and modify the file length for the alert, this should be a lot better with arrow
    if dpid in ['DP1.00094.001','DP1.00041.001'] and len(files) > 24:
        logging.info("Warning! Attempting to stack soil sensor data. Note that due to the number of soil sensors at each site, data volume is very high for these data. Consider dividing data processing into chunks and/or using a high-performance system.")
    
    # If all checks pass, unzip and stack files
    if cloud_mode:
        stackedlist = stack_data_files_parallel(folder=files, package=package, 
                                                dpid=dpid, progress=progress,
                                                cloud_mode=True)
    
    else:
    
        # If the filepath is a zip file
        if not folder:
            unzip_zipfile_parallel(zippath = filepath)
            stackpath = filepath[:-4]
                
        # If the filepath is a directory
        if folder:
            if any(".zip" in file for file in files):
                unzip_zipfile_parallel(zippath = filepath)
            stackpath = filepath
                    
        # Stack the files
        stackedlist = stack_data_files_parallel(folder=stackpath, 
                                                package=package, 
                                                dpid=dpid,
                                                progress=progress)
            
        # delete input files
        if not save_unzipped_files:
            ufl = glob.glob(stackpath+"/**.*/*", recursive=True)
            for fl in ufl:
                try:
                    os.remove(fl)
                except:
                    pass
            dirlist = glob.glob(stackpath+"/*",recursive=True)
            for d in dirlist:
                try:
                    os.rmdir(d)
                except:
                    pass
            if os.listdir(stackpath) == []:
                os.rmdir(stackpath)
    
    # write files to path if requested
    if savepath == "envt":
        return stackedlist
    else:
        if savepath is None:
            stacked_files_dir = os.path.join(stackpath, "stackedFiles")
            
        elif savepath != "envt":
            stacked_files_dir = os.path.join(savepath, "stackedFiles")
        
        if not os.path.exists(stacked_files_dir):
            os.makedirs(stacked_files_dir)

        for k in stackedlist.keys():
            tk = stackedlist[k]
            if "citation" in k:
                with open(f"{stacked_files_dir}/{k}.txt", 
                          mode="w+", encoding="utf-8") as f:
                    f.write(tk)
            else:
                tk.to_csv(f"{stacked_files_dir}/{k}.csv", index=False)

        return None
        

def load_by_product(dpid, site="all", startdate=None, enddate=None, 
                    package="basic", release="current", 
                    timeindex="all", tabl="all", check_size=True,
                    include_provisional=False, cloud_mode=False,
                    progress=True, token=None):
    """
    Download product-site-month data package files from NEON, stack, and load to the environment.
    
    Parameters
    --------
    dpid: Data product identifier in the form DP#.#####.###
    site: One or more 4-letter NEON site codes
    package: Download package to access, either basic or expanded
    startdate: Earliest date of data to download, in the form YYYY-MM
    enddate: Latest date of data to download, in the form YYYY-MM
    release: Data release to download. Defaults to the most recent release.
    include_provisional: Should Provisional data be returned in the download? Defaults to False.
    cloud_mode: Use cloud mode to transfer files cloud-to-cloud? Should only be used if the destination location is in the cloud. Defaults to False.
    progress: Should the function display progress bars as it runs? Defaults to True
    token: User specific API token (generated within neon.datascience user accounts). If omitted, download uses the public rate limit.

    Return
    --------
    A folder on the local drive containing the set of data package files meeting the input criteria.

    Example
    --------
    Download water quality data from COMO (Como Creek) in 2018

    >>> load_by_product(dpid="DP1.20288.001",site="COMO",
                        startdate="2018-01", enddate="2018-12",
                        token=None)
    
    Created on June 12 2024

    @author: Claire Lunch
    """  
    
    savepath = os.getcwd()
    
    if cloud_mode:
        flist = zips_by_product(dpid=dpid, site=site, 
                        startdate=startdate, enddate=enddate,
                        package=package, release=release,
                        timeindex=timeindex, tabl=tabl,
                        check_size=check_size, 
                        include_provisional=include_provisional,
                        cloud_mode=True,
                        progress=progress, token=token,
                        savepath=savepath)
        
        outlist = stack_by_table(filepath=flist, savepath="envt",
                                 cloud_mode=True,
                                 save_unzipped_files=False, 
                                 progress=progress)
        
    else:
    
        zips_by_product(dpid=dpid, site=site, 
                        startdate=startdate, enddate=enddate,
                        package=package, release=release,
                        timeindex=timeindex, tabl=tabl,
                        check_size=check_size, 
                        include_provisional=include_provisional,
                        progress=progress, token=token,
                        savepath=savepath)
        
        stackpath = savepath+"/filesToStack"+dpid[4:9]+"/"
        
        outlist = stack_by_table(filepath=stackpath, savepath="envt",
                                 save_unzipped_files=False, progress=progress)
    
    return outlist

