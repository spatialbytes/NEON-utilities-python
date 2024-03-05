#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

def read_table_neon(data_file,
                    var_file#,
                    #use_fast_time # Equivalent in Python?
                    ):
    """

    Read a NEON data table with correct data types for each variable.
    
    Parameters
    --------
    data_file: A data frame containing a NEON data table, or the filepath to a data table to load.
    var_file: A data frame containing the corresponding NEON variables file, or the filepath to the variables file.
    
    Return
    --------
    A data frame of a NEON data table, with column classes assigned by data type.
    
    Example
    --------
    ZN NOTE: Insert example when function is coded
    
    >>> example
    
    Created on Thu Feb 1 2024
    
    @author: Zachary Nickerson
    """    
    # Read in variables file and check type
    if isinstance(var_file,str):
        try:
            v = pd.read_csv(var_file)
        except:
            print("Table read failed because var_file must be either a NEON variables table or a file path to a NEON variables table.\n")
            return
    else:
        try:
            v = pd.DataFrame(var_file)
        except:
            print("Table read failed because var_file must be either a NEON variables table or a file path to a NEON variables table.\n")
            return
        
    # Check this is a valid variables file
    if any(x in ['category','system','stat'] for x in list(v.columns)):
        print('var_file appears to match DP4.00200.001. Automated matching of data types to variables is not available for this data product; we hope to add this in a future release.\n')
        return
    else:
        if not any(x in ['table','fieldName','dataType'] for x in list(v.columns)):
            print('var_file is not a variables file, or is missing critical values.\n')
            return
    
    # Make a new colClass column defaulting to numeric
    # Modify to character for strings and urls
    v['colClass'] = np.nan
    v['colClass'][v.dataType == "real"] = "float"
    v['colClass'][v.dataType == "integer"] = "int"
    v['colClass'][v.dataType == "unsigned integer"] = "int"
    v['colClass'][v.dataType == "signed integer"] = "int"
    v['colClass'][v.dataType == "string"] = "str"
    v['colClass'][v.dataType == "uri"] = "str"
    v['colClass'][v.dataType == "dateTime"] = "datetime"
    v = v[['table','fieldName','colClass']]
    
    # Read in data file and check type
    if isinstance(data_file,str):
        try:
            d = pd.read_csv(data_file)
        except:
            print("Table read failed because data_file must be either a NEON variables table or a file path to a NEON variables table.\n")
            return
    else:
        try:
            d = pd.DataFrame(data_file)
        except:
            print("Table read failed because data_file must be either a NEON variables table or a file path to a NEON variables table.\n")
            return    
    
    # Check that most fields have a corrsponding value in variables
    m = len(set(list(d.columns)) - set(list(v.fieldName)))
    if m == len(d.columns):
        print("Cannot correct data types because the variables file does not match the data file.\n")
        return
    if m > 4:
        print(m,"fieldNames are present in data files but not in variables file. Unknown fields are read as character strings.\n")
        
    # fieldNames each have a unique dataType - don't need to match table    
    for i in list(d.columns):
        if i not in list(v.fieldName):
            d[i] = d[i].astype("string")
        else:
            type = np.unique(v.colClass[v.fieldName == i])[0]
            if type == 'str':
                d[i] = d[i].astype("string")
            if type == 'datetime':
                d[i] = pd.to_datetime(d[i], format = '%Y-%m-%dT%H:%MZ')# Is there a use_fast_time equivalent in python?
            if type in ['int','float']:
                d[i] = pd.to_numeric(d[i])
                
    return d

# Set inputs locally
# data_file=pd.read_csv("C:/Users/nickerson/Downloads/NEON.D13.COMO.DP1.20194.001.asc_externalLabData.2023-09.expanded.20240115T155827Z.csv") 
# var_file=pd.read_csv("C:/Users/nickerson/Downloads/NEON.D13.COMO.DP1.20194.001.variables.20240115T155827Z.csv")

# # Test with csv
# output_df = read_table_neon(data_file=pd.read_csv("C:/Users/nickerson/Downloads/NEON.D13.COMO.DP1.20194.001.asc_externalLabData.2023-09.expanded.20240115T155827Z.csv"), 
#                             var_file=pd.read_csv("C:/Users/nickerson/Downloads/NEON.D13.COMO.DP1.20194.001.variables.20240115T155827Z.csv"))
            
# # Test with txt
# output_df = read_table_neon(data_file=pd.read_csv("C:/Users/nickerson/Downloads/NEON.D13.COMO.DP1.20194.001.asc_externalLabData.2023-09.expanded.20240115T155827Z.csv"), 
#                             var_file=pd.read_csv("C:/Users/nickerson/Downloads/NEON.D13.COMO.DP1.20194.001.variables.20240115T155827Z.csv"))

# # Test with file path
# output_df = read_table_neon(data_file="C:/Users/nickerson/Downloads/NEON.D13.COMO.DP1.20194.001.asc_externalLabData.2023-09.expanded.20240115T155827Z.csv", 
#                             var_file="C:/Users/nickerson/Downloads/NEON.D13.COMO.DP1.20194.001.variables.20240115T155827Z.csv")

# # Test with typo in file path
# output_df = read_table_neon(data_file="C:/Users/mickerson/Downloads/NEON.D13.COMO.DP1.20194.001.asc_externalLabData.2023-09.expanded.20240115T155827Z.csv", 
#                             var_file="C:/Users/mickerson/Downloads/NEON.D13.COMO.DP1.20194.001.variables.20240115T155827Z.csv")
    

    
    
        

