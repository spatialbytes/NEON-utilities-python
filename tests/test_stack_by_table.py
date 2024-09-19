# -*- coding: utf-8 -*-
"""
Created on 14 Aug 2024

@author: Claire Lunch

Unit tests for stack_by_table()

"""

# import required packages
from src.neonutilities.unzip_and_stack import stack_by_table
import pandas as pd


def test_stack_by_table_mini():
    """
    Test that stack_by_table() stacks the example product correctly. Example includes site-date, site-all, and lab-all.
    Test works but leaves unzipped items in the repo. Need to figure out how to remove
    """
    litterlst = stack_by_table("./testdata/NEON_litterfall.zip", savepath="envt", progress=False)
    litterchk = pd.read_csv("./testdata/NEON_litterfall_baseline/stackedFiles/ltr_litterLignin.csv")
    assert all(litterchk == litterlst["ltr_litterLignin"]) is True
