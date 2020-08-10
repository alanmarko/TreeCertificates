"""
Certificate.py

Certificate.py describes what information is supposed to be stored inside of a certificate
"""

import sys
import time
import numpy

class Certificate:
    def __init__(self, status, facilityName, description, images, files, address, region, province, country,
                 operationalSince, capacityInW, gpsLatitude, gpsLongtitude, timezone, deviceType, gridOperator):
        self.status = status
        self.facilityName = facilityName
        self.description = description
        self.images = images
        self.files = files
        self.address = address
        self.region = region
        self.province = province
        self.country = country
        self.operationalSince = operationalSince
        self.capacityInW = capacityInW
        self.gpsLatitude = gpsLatitude
        self.gpsLongtitude = gpsLongtitude
        self.timezone = timezone
        self.deviceType = deviceType
        self.gridOperator = gridOperator

    def hash(self):
        h=bytearray(abs(hash(str(self))).to_bytes(32,byteorder="big"))
        return h