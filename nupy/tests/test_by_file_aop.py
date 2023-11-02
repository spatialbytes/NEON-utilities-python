#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: bhass

Created on Thur Nov 2 2023
@author: Bridget Hass (bhass@battelleecology.org)

"""

import pytest
from neonutilities import by_file_aop

# def test_by_file_aop_valid_download():
#     """
#     Test that by_file_aop downloads as expected with all valid inputs.
#     """
#     # test simple download
#     by_file_aop('DP3.30015.001','MCRA','2021',check_size=False,save_path='test_download')

# test print-out messages for incorrect inputs using capsys fixture
def test_by_file_aop_invalid_dpid_format(capsys):
    """
    Test that the by_file_aop() function returns the expected error message when an invalid dpid format is provided
    """
    dpid="DP1.0010"
    by_file_aop(dpid=dpid,site="MCRA",year=2021)
    out, err = capsys.readouterr()
    assert out == f'{dpid} is not a properly formatted data product ID. The correct format is DP#.#####.00#\n'

def test_by_file_aop_invalid_site_format(capsys):
    """
    Test that the by_file_aop() function returns the expected error message when an invalid site format is provided
    """
    site="abc"
    by_file_aop(dpid="DP3.30015.001",site=site,year="2020")
    out, err = capsys.readouterr()
    assert out == f'{site.upper()} is an invalid site. A four-letter NEON site code is required. NEON sites codes can be found here: https://www.neonscience.org/field-sites/field-sites-map/list.\n'

def test_by_file_aop_invalid_year_format(capsys):
    """
    Test that the by_file_aop() function returns the expected error message when an invalid year format is provided
    """
    year="19"
    by_file_aop(dpid="DP3.30015.001",site="MCRA",year=year)
    out, err = capsys.readouterr()
    assert out == f'{year} is an invalid year. Year is required in the format "2017", eg. Data are available from 2013 to present.\n'


# def test_by_file_aop_collocated_site_message(capsys):
#     """
#     Test that the by_file_aop() function returns the expected message when a collocated site is provided
#     """



    # with pytest.raises(Exception) as exception:
    #     response = by_file_aop(dpid="DP3.30015.001",site="MCRA",year=year)
    # assert str(
    #     exception.value) == f'{year} is an invalid year. Year is required in the format "2017", eg. Data are available from 2013 to present.'
    # #    
    # def test_invalid_url():
    #     """
    #     Test that the get_api() function returns None when the URL is invalid.
    #     """
    #     with pytest.raises(Exception) as exception:
    #         response = get_api(api_url=invalid_url, token=None)
    #     assert str(
    #         exception.value) == 'No response. Failed to establish a new connection.'