"""
eeMap.py

eeMap.py was used to demonstrate usage of folium-based tool for showing map data.
It allows creation of multiple layers on the map and controls used for moving and zooming inside of the area
"""

import datetime
import ee
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from PIL import Image
import time
from osgeo import gdal
import numpy
import eeDrive
import folium
import ee
import datetime
import webbrowser

file_id = '0BwwA4oUTeiV1UVNwOHItT0xfa2M'
request = drive_service.files().get_media(fileId=file_id)
fh = io.BytesIO()
downloader = MediaIoBaseDownload(fh, request)
done = False
while done is False:
    status, done = downloader.next_chunk()
    print "Download %d%%." % int(status.progress() * 100)

gdd.download_file_from_google_drive(file_id='1i60BMqt5jJDGk7pspHaTJkcwElUmJzm6',
                                    dest_path='./data/fero.zip',
                                    unzip=False)

img = ee.Image('UMD/hansen/global_forest_change_2019_v1_7')

print(img)

print(img.getInfo())
#imgplot = plt.imshow(img)
#plt.show()

ee.Initialize()

collection = (ee.ImageCollection('LANDSAT/LE07/C01/T1')
              .filterDate(datetime.datetime(2002, 11, 8),
                          datetime.datetime(2002, 11, 9)))
image = collection.mosaic().select('B3', 'B2', 'B1')


elev = ee.Image('CGIAR/SRTM90_V4')
mask1 = elev.mask().eq(0).And(image.mask())
mask2 = elev.eq(0).And(image.mask())

landsat = ee.Image('LANDSAT/LC8_L1T_TOA/LC81230322014135LGN00').select(['B4', 'B3', 'B2']);
llx = 116.2621
lly = 39.8412
urx = 116.4849
ury = 40.01236
geometry = [[llx,lly], [llx,ury], [urx,ury], [urx,lly]]

task_config = {
    'description': 'imageToDriveExample',
    'scale': 30,
    'region': geometry
    }

task = ee.batch.Export.image(landsat,  task_config)

task.start()
ee.Initialize()

class eeMapHack(object):
    def __init__(self,center=[0, 0],zoom=3):
        self._map = folium.Map(location=center,zoom_start=zoom)
        return

    def addToMap(self,img,vizParams,name):
         map_id = ee.Image(img.visualize(**vizParams)).getMapId()
         tile_url_template = "https://earthengine.googleapis.com/map/{mapid}/{{z}}/{{x}}/{{y}}?token={token}"
         mapurl = tile_url_template.format(**map_id)
         folium.WmsTileLayer(mapurl,name=name).add_to(self._map)

         return

    def addLayerControl(self):
         self._map.add_child(folium.map.LayerControl())
         return


eeMap = eeMapHack(center=[18.453,-95.738],zoom=9)

collection = (ee.ImageCollection('LE7_L1T')
          .filterDate(datetime.datetime(2002, 11, 8),
                      datetime.datetime(2002, 11, 9)))
image = collection.mosaic().select('B3', 'B2', 'B1')
eeMap.addToMap(image, {'gain': '1.6, 1.4, 1.1'}, 'Land')

elev = ee.Image('srtm90_v4')
mask1 = elev.mask().eq(0).And(image.mask())
mask2 = elev.eq(0).And(image.mask())

eeMap.addToMap(image.mask(mask1), {'gain': 6.0, 'bias': -200}, 'Water: Masked')
eeMap.addToMap(image.mask(mask2), {'gain': 6.0, 'bias': -200}, 'Water: Elev 0')

# add layer control to map
eeMap.addLayerControl()

outHtml = 'map.html' # temporary file path, change if needed
eeMap._map.save(outHtml)

webbrowser.open('file://'+outHtml)