# -*- coding: utf-8 -*-
"""
Created on 14 Mar 2024

@author: Claire Lunch

Unit tests for zips_by_product()

Mocking is not used here, tests access API resources. Tests here primarily test for error handling.

"""

# import required packages
import os
from neonutilities import zips_by_product

import pytest
import logging

# read in token from os.environ
token = os.environ.get("NEON_TOKEN")

def test_zips_by_product_dpid():
    """
    Test that the zips_by_product() function errors correctly for an invalid DPID
    """
    with pytest.raises(ValueError) as exc_info:
        zips_by_product(dpid='DP1.444.001', site='NIWO',
                        startdate='2012-01', enddate='2022-12')
    assert str(exc_info.value)=="DP1.444.001 is not a properly formatted data product ID. The correct format is DP#.#####.00#"

def test_zips_by_product_site(caplog):
    """
    Test that the zips_by_product() function returns correct message for no data at particular site
    """
    caplog.set_level(logging.INFO)

    zips_by_product(dpid='DP1.10003.001', site=['OKSR','ARIK'],
                    startdate='2012-01', enddate='2022-12')

    assert any("There are no data at the selected sites." in record.message for record in caplog.records)
    
    