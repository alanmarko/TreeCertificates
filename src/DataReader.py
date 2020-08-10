"""
DataReader.py

DataReader.py implements methods for reading map data from GeoTiff files (e.g. treecover data downloaded from Google Earth Engine),
detection whether a point belongs to the map, and reading value at a particular (latitude,longtitude) coordinates
"""

import datetime
import ee
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from PIL import Image
import time
from osgeo import gdal
import numpy as np

class DataReader:
    def __init__(self,name):
        driver = gdal.GetDriverByName('GTiff')
        filename = name+".tif"
        dataset = gdal.Open(filename)
        band = dataset.GetRasterBand(1)
        self.cols = dataset.RasterXSize
        self.rows = dataset.RasterYSize
        transform = dataset.GetGeoTransform()
        self.xOrigin = transform[0]
        self.yOrigin = transform[3]
        self.pixelWidth = transform[1]
        self.pixelHeight = -transform[5]
        self.data = band.ReadAsArray(0, 0, self.cols, self.rows)

    def isInside(self,latitude,longtitude):
        if longtitude < self.xOrigin:
            return False
        if self.yOrigin<latitude:
            return False
        col = int((longtitude - self.xOrigin) / self.pixelWidth)
        row = int((self.yOrigin - latitude) / self.pixelHeight)
        if self.cols < col or self.rows < row:
            return False
        return True

    def getValue(self,latitude,longtitude):
        col = int((longtitude - self.xOrigin) / self.pixelWidth)
        row = int((self.yOrigin - latitude) / self.pixelHeight)
        return self.data[row][col]