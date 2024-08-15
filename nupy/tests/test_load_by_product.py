# -*- coding: utf-8 -*-
"""
Created on 15 Aug 2024

@author: Claire Lunch

Unit tests for load_by_product()

"""

# import required packages
from neonutilities import load_by_product

import pytest
import logging
import pandas as pd

def test_load_by_product_IS():
    """
    Test that load_by_product() accesses and stacks the example data correctly.
    """
    tlist = load_by_product(dpid='DP1.00005.001', site=['TOOL','PUUM'],
                            startdate='2022-06', enddate='2022-07',
                            check_size=False, progress=False,
                            release='RELEASE-2024', cloud_mode=True)
    assert list(tlist.keys()) == ['variables_00005', 'readme_00005', 'IRBT_30_minute', 
                                  'IRBT_1_minute', 'sensor_positions', 'science_review_flags', 
                                  'issueLog_00005', 'citation_00005_RELEASE-2024'] is True
    tm = tlist['IRBT_30_minute']
    assert len(tm) == 23424 is True
    assert max(tm['endDateTime']) == pd.Timestamp('2022-08-01 00:00:00+0000', tz='UTC') is True
    assert min(tm['endDateTime']) == pd.Timestamp('2022-06-01 00:30:00+0000', tz='UTC') is True
