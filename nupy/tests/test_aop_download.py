# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 17:00:19 2024

@author: bhass
"""
import os
import shutil
from pathlib import Path
import glob
import pandas as pd
from shapely.geometry import Point
import geopandas as gpd
from neonutilities import by_file_aop, by_tile_aop

import pytest
from unittest import mock


# test print-out messages for incorrect inputs using capsys fixture
def test_by_file_aop_invalid_dpid_format(capsys):
    """
    Test that the by_file_aop() function returns the expected error message when an invalid dpid format is provided
    """
    dpid = "DP1.0010"
    by_file_aop(dpid=dpid, site="MCRA", year=2021)
    out, err = capsys.readouterr()
    assert out == f'{dpid} is not a properly formatted data product ID. The correct format is DP#.#####.00#\n'


def test_by_file_aop_invalid_site_format(capsys):
    """
    Test that the by_file_aop() function returns the expected error message when an invalid site format is provided
    """
    site = "abc"
    by_file_aop(dpid="DP3.30015.001", site=site, year="2020")
    out, err = capsys.readouterr()
    assert out == f'{site.upper()} is an invalid site. A four-letter NEON site code is required. NEON sites codes can be found here: https://www.neonscience.org/field-sites/field-sites-map/list.\n'


def test_by_file_aop_invalid_year_format(capsys):
    """
    Test that the by_file_aop() function returns the expected error message when an invalid year format is provided
    """
    year = "19"
    by_file_aop(dpid="DP3.30015.001", site="MCRA", year=year)
    out, err = capsys.readouterr()
    assert out == f'{year} is an invalid year. Year is required in the format "2017", eg. Data are available from 2013 to present.\n'


def test_collocated_site_message(capsys, monkeypatch):
    site = "CHEQ"
    monkeypatch.setattr('builtins.input', lambda _: "n")
    by_file_aop(dpid="DP3.30015.001", site=site, year="2022")
    out, err = capsys.readouterr()
    assert out == f'CHEQ is part of the flight box for STEI. Downloading data from STEI.\nDownload halted.\n'


# token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJhdWQiOiJodHRwczovL2RhdGEubmVvbnNjaWVuY2Uub3JnL2FwaS92MC8iLCJzdWIiOiJuaWNrZXJzb25AYmF0dGVsbGVlY29sb2d5Lm9yZyIsInNjb3BlIjoicmF0ZTp1bmxpbWl0ZWQgcmVhZDpyZWxlYXNlcyByZWFkOnJlbGVhc2VzLWxhdGVzdCIsImlzcyI6Imh0dHBzOi8vZGF0YS5uZW9uc2NpZW5jZS5vcmcvIiwiZXhwIjoxNzkzNjQ2MTUyLCJpYXQiOjE2MzU5NjYxNTIsImVtYWlsIjoibmlja2Vyc29uQGJhdHRlbGxlZWNvbG9neS5vcmcifQ.dUyan8p2z42DWimkrRcxBUOBrbwL5dqPpF_55GqKbLnqZAFwcg6pjPu-ByugkaixeQqL7LL_BCny-GNjh7vlWw'
# savepath = r'C:\Users\bhass\Documents\GitHubRepos\nupy-data-temp'

# clear out path first to start with a clean slate
# if os.path.exists(savepath):
#     shutil.rmtree(savepath)

# test by_file_aop

# terrestrial site

# terrestrial collocated site

# aquatic collocated site


# test by_tile_aop

# 1 tile, no buffer

# 2 tiles (list), no buffer

# 3 points, buffer = 5

# test BLAN coordinate conversion
# BLAN plots 20, 15 (UTM 18N), 57 (UTM 17N)
# easting = [242141.81, 244446.18, 753149.65]
# northing = [4332291.08, 4330648.08, 4327233.78]

# these are the eastings and northings from Claire's manual test
# easting = [753209.10714, 753210.39029, 753301.31442, 753302.08723,
#            753360.67602, 753001.78397, 753300.65182, 753149.62305,
#            753241.48637, 753242.02638, 753171.90744, 753150.69495,
#            753000.77807, 242947.57093, 243025.74806, 242767.63602,
#            243866.95531, 243172.00059, 244121.70221, 243743.00946,
#            243256.83693, 244173.0213, 244446.13783, 243758.81054]

# northing = [4327205.26166, 4327294.53028, 4327387.24247, 4327446.60415,
#             4327445.82548, 4327654.94513, 4327625.56833, 4327233.79211,
#             4327353.86862, 4327686.68298, 4327685.09089, 4327595.9582,
#             4327594.68720, 4330687.21691, 4330562.09017, 4330669.43982,
#             4330056.00872, 4330460.85162, 4330700.31990, 4330002.60182,
#             4329943.13784, 4330576.9702, 4330648.08463, 4330667.37104]

# by_tile_aop('DP3.30015.001', 'BLAN', '2021', easting, northing,
#             buffer=5, token=token, save_path=savepath, verbose=True)

# %%

# veg <- loadByProduct(dpID='DP1.10098.001', site='BLAN', check.size=F)
# veg.loc <- geoNEON::getLocTOS(veg$vst_mappingandtagging, 'vst_mappingandtagging')
# veg.temp <- geoNEON::getLocByName(veg$vst_mappingandtagging, locCol='namedLocation', locOnly=T)
# ea <- veg.loc$adjEasting[which(!is.na(veg.loc$adjEasting))]
# no <- veg.loc$adjNorthing[which(!is.na(veg.loc$adjNorthing))]
# ea <- veg.temp$easting
# no <- veg.temp$northing
# byTileAOP(dpID='DP3.30015.001', site='BLAN', year=2017,
#           easting=ea, northing=no, buffer=10, savepath='/Users/clunch/Desktop')

# test warning messages for invalid inputs

# geometric buffer checks
# first visually check
# then can use geopandas covered_by - need to ensure the points provided are actually in the site, and the shapefiles actually exist
# add a notification if tiles are outside the boundaries of the site??

# https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoSeries.covered_by.html

# set up - actually runs the download

# tear down - deletes downloaded data

# edge of tile coordinates, with buffer
# dpid = 'DP3.30015.001'
# site = 'HARV'
# year = '2022'
# easting = [724005.0, 724005.0, 723999.0]
# northing = [4707005.0, 4707995.0, 4707001.0]
# buffer = 2

# by_tile_aop(dpid, site, year, easting, northing,
#             buffer=5, token=token, save_path=savepath, verbose=True)

# files = glob.iglob(os.path.join(savepath,))
# # FullSite\D01\2022_HARV_7\Metadata\DiscreteLidar\TileBoundary\shps
# gdfs = (gpd.read_file(file) for file in files)

# folder = Path(savepath) / year / 'FullSite' / 'D01' / '2022_HARV_7' / \
# 'Metadata' / 'DiscreteLidar' / 'TileBoundary' / 'shps'
# %%
# folder = Path(savepath) / dpid / year / 'FullSite' / 'D01' / \
#     '2022_HARV_7' / 'Metadata' / 'DiscreteLidar' / 'TileBoundary' / 'shps'

# gdf = pd.concat([gpd.read_file(shp)
#                 for shp in folder.glob("*.shp")]).pipe(gpd.GeoDataFrame)

# gdf.plot()

# point_geom = [Point((easting[i], northing[i])) for i in range(len(easting))]
# gdf2 = gpd.GeoDataFrame(df, geometry=point_geom)

# gdf2['geometry'] = gdf2.geometry.buffer(buffer)
# # %%
# for i in range(len(easting)):
#     f, ax = plt.subplots()
#     gdf.plot(ax=ax, alpha=0.75)
#     gdf2.plot(ax=ax, color='red', alpha=0.5)
#     minx = easting[i]-buffer*4
#     maxx = easting[i]+buffer*4
#     miny = northing[i]-buffer*4
#     maxy = northing[i]+buffer*4
#     ax.set_xlim(minx, maxx)
#     ax.set_ylim(miny, maxy)


# R manual tests for byTileAOP

# # 2 legit tiles, 1 garbage coordinate pair
# byTileAOP(dpID = "DP3.30015.001", site = "WREF", year = "2017",
#           easting = c(571000,743000,578000),
#           northing = c(5079000,3984000,5080000),
#           savepath='/Users/clunch/Desktop', check.size = FALSE,
#           token=Sys.getenv('NEON_TOKEN'))

# # multiple months per year
# byFileAOP(dpID='DP3.30015.001', site='KONZ', year=2019,
#           savepath='/Users/clunch/Desktop', token=Sys.getenv('NEON_TOKEN'))

# # multiple months per year
# byTileAOP(dpID='DP3.30015.001', site='CPER', year=2020,
#           easting = c(523300,519700),
#           northing = c(4513400,4518400),
#           savepath='/Users/clunch/Desktop', token=Sys.getenv('NEON_TOKEN'))

# # test for Blandy UTM zones
# veg <- loadByProduct(dpID='DP1.10098.001', site='BLAN', check.size=F)
# veg.loc <- geoNEON::getLocTOS(veg$vst_mappingandtagging, 'vst_mappingandtagging')
# veg.temp <- geoNEON::getLocByName(veg$vst_mappingandtagging, locCol='namedLocation', locOnly=T)
# ea <- veg.loc$adjEasting[which(!is.na(veg.loc$adjEasting))]
# no <- veg.loc$adjNorthing[which(!is.na(veg.loc$adjNorthing))]
# ea <- veg.temp$easting
# no <- veg.temp$northing
# byTileAOP(dpID='DP3.30015.001', site='BLAN', year=2017,
#           easting=ea, northing=no, buffer=10, savepath='/Users/clunch/Desktop')
# # I got 5 tiles. Is that right??
# blan1 <- terra::rast('/Users/clunch/Desktop/DP3.30015.001/neon-aop-products/2017/FullSite/D02/2017_BLAN_2/L3/DiscreteLidar/CanopyHeightModelGtif/NEON_D02_BLAN_DP3_752000_4327000_CHM.tif')
# blan2 <- terra::rast('/Users/clunch/Desktop/DP3.30015.001/neon-aop-products/2017/FullSite/D02/2017_BLAN_2/L3/DiscreteLidar/CanopyHeightModelGtif/NEON_D02_BLAN_DP3_753000_4327000_CHM.tif')
# blan3 <- terra::rast('/Users/clunch/Desktop/DP3.30015.001/neon-aop-products/2017/FullSite/D02/2017_BLAN_2/L3/DiscreteLidar/CanopyHeightModelGtif/NEON_D02_BLAN_DP3_761000_4330000_CHM.tif')
# blan4 <- terra::rast('/Users/clunch/Desktop/DP3.30015.001/neon-aop-products/2017/FullSite/D02/2017_BLAN_2/L3/DiscreteLidar/CanopyHeightModelGtif/NEON_D02_BLAN_DP3_762000_4330000_CHM.tif')
# blan5 <- terra::rast('/Users/clunch/Desktop/DP3.30015.001/neon-aop-products/2017/FullSite/D02/2017_BLAN_2/L3/DiscreteLidar/CanopyHeightModelGtif/NEON_D02_BLAN_DP3_763000_4330000_CHM.tif')
# blan <- terra::merge(blan1, blan2, blan3, blan4, blan5)
# terra::plot(blan)
# # yes, this is right
