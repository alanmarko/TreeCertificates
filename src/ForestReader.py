"""
ForestReader.py

ForestReader.py was used for demonstration of downloading data from the Hansen data set and then
reading of the values from GeoTiff files via gdal library
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

import json
import time
import base64
from algosdk import algod
from algosdk import mnemonic
from algosdk import transaction
import Certificate
import xarray as xr
import exifread
import DataReader


class ForestReader:
    def __init__(self):
        ee.Authenticate()
        ee.Initialize()
        self.loss=ee.Image("UMD/hansen/global_forest_change_2019_v1_7").select(['loss'])
        self.treecover=ee.Image("UMD/hansen/global_forest_change_2019_v1_7").select(['treecover2000'])

        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        self.drive = GoogleDrive(gauth)

        ds = gdal.Open('america_carbon_1km.tif')
        self.width = ds.RasterXSize
        self.height = ds.RasterYSize
        gt = ds.GetGeoTransform()
        self.minx = gt[0]
        self.miny = gt[3] + self.width * gt[4] + self.height * gt[5]
        self.maxx = gt[0] + self.width * gt[1] + self.height * gt[2]
        self.maxy = gt[3]
        File_Name = "america_carbon_1km"
        imCarbon = Image.open(File_Name + '.tif')
        self.carbonArray = numpy.array(imCarbon)

    def downloadFromDrive(self, file_name):
        local_download_path = ''
        try:
            os.makedirs(local_download_path)
        except:
            pass

        file_list = self.drive.ListFile(
            {'q': "'1i60BMqt5jJDGk7pspHaTJkcwElUmJzm6' in parents and trashed=false"}).GetList()

        for f in file_list:
            print('title: %s, id: %s' % (f['title'], f['id']))
            fname = f['title']
            if fname == (file_name+'.tif'):
                print('downloading to {}'.format(fname))
                f_ = self.drive.CreateFile({'id': f['id']})
                f_.GetContentFile(fname)

        options_list = [
            '-ot Byte',
            '-of JPEG',
            '-b 1',
            '-scale'
        ]
        options_string = " ".join(options_list)
        gdal.Translate(file_name + '.jpg',
                       file_name + '.tif',
                       options=options_string)

        im = Image.open(file_name + '.jpg')
        im.show()

    def uploadToDrive(self,File_Name,population,latitude,longtitude):
        geometry = ee.Geometry.Rectangle( [longtitude, latitude, longtitude + 1,latitude  + 1])

        task_config = {
            'region': geometry.coordinates().getInfo(),
            'scale': 20,
            'description': File_Name,
            'folder': 'fero'
        }

        task = ee.batch.Export.image.toDrive(population, **task_config)
        task.start()

        while task.status()['state'] in ['READY', 'RUNNING']:
            print(task.status())
            time.sleep(10)
        else:
            print(task.status())

    def getValue(self,file_name,latitude,longtitude,population):
        File_Name = file_name + str(latitude) + str(longtitude)
        self.uploadToDrive(File_Name,population,latitude,longtitude)
        self.downloadFromDrive(File_Name)
        im = Image.open(File_Name + '.jpg')
        imarray = numpy.array(im)
        return imarray[0][0]

    def isForest(self,latitude,longtitude):
        lossValue=self.getValue("loss",latitude,longtitude,self.loss)
        treeCoverValue= self.getValue("treeCoverValue", latitude, longtitude, self.treecover)

        print(f"loss: {lossValue}")
        print(f"treeCover: {treeCoverValue}")

        if lossValue<100 and treeCoverValue >0:
            return True
        return False

    def getBenchmarkMapValue(self,latitude,longtitude):
        return self.carbonArray[(latitude-self.miny)*(self.maxy-self.miny)/self.height][(longtitude-self.minx)*(self.maxx-self.minx)/self.width]

    def wait_for_confirmation(self,algod_client, txid):
        while True:
            txinfo = algod_client.pending_transaction_info(txid)
            if txinfo.get('round') and txinfo.get('round') > 0:
                print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('round')))
                break
            else:
                print("Waiting for confirmation...")
                algod_client.status_after_block(algod_client.status().get('lastRound') + 1)
        return txinfo

    def createCertificate(self,latitude,longtitude):
        algod_address = "https://testnet-algorand.api.purestake.io/ps1"
        algod_token = ""
        headers = {
            "X-API-Key": "5K5TIs5wJtaqBNHNfOyya2mxDj9mQBEkYAqWgu09",
        }

        algod_client = algod.AlgodClient(algod_token, algod_address, headers)
        status = algod_client.status()
        print(json.dumps(status, indent=4))

        passphrase = "thunder fun scout myself talk repeat hurry miracle puppy run vocal vicious shove fever idea lens above diesel action pulp before cigar horror above mass"

        private_key = mnemonic.to_private_key(passphrase)
        my_address = mnemonic.to_public_key(passphrase)
        print("My address: {}".format(my_address))

        account_info = algod_client.account_info(my_address)
        print("Account balance: {} microAlgos".format(account_info.get('amount')))

        c = Certificate("tmp", "tmp", "tmp", "tmp", "tmp", "tmp", "tmp", "tmp", "tmp", "tmp", "tmp", "tmp", "tmp",
                        "tmp", "tmp", "tmp")

        params = algod_client.suggested_params()
        first = params.get("lastRound")
        last = first + 1000
        gen = params.get("genesisID")
        gh = params.get("genesishashb64")
        min_fee = params.get("minFee")

        data = {
            "sender": my_address,
            "fee": min_fee,
            "first": first,
            "last": last,
            "gh": gh,
            "total": 1000,
            "decimals": 0,
            "default_frozen": False,
            "unit_name": "aa",
            "asset_name": "bb",
            "metadata_hash": c.hashuj(),
            "manager": my_address,
            "reserve": my_address,
            "freeze": my_address,
            "clawback": my_address,
            "url": "https://path/to/my/asset/details",
            "flat_fee": True
        }

        txn = transaction.AssetConfigTxn(**data)

        stxn = txn.sign(private_key)

        print("Asset Creation")
        txid = algod_client.send_transaction(stxn, headers={'content-type': 'application/x-binary'})


        txinfo = self.wait_for_confirmation(algod_client, txid)
        print(txinfo.keys())
        print(txinfo)
        asset_id = txinfo["txresults"]["createdasset"]
        account_info = algod_client.account_info(my_address)

        account_info = algod_client.account_info(my_address)
        holding = None
        if 'assets' in account_info:
            holding = account_info['assets'].get(str(asset_id))

        if not holding:
            data = {
                "sender": my_address,
                "fee": min_fee,
                "first": first,
                "last": last,
                "gh": gh,
                "receiver": my_address,
                "amt": 0,
                "index": asset_id,
                "flat_fee": True
            }
            print("Asset Option In")
            txn = transaction.AssetTransferTxn(**data)
            stxn = txn.sign(private_key)
            txid = algod_client.send_transaction(stxn, headers={'content-type': 'application/x-binary'})
            print(txid)
            self.wait_for_confirmation(txid)
            account_info = algod_client.account_info(my_address)
            print(json.dumps(account_info['assets'][str(asset_id)], indent=4))

        data = {
            "sender": my_address,
            "fee": min_fee,
            "first": first,
            "last": last,
            "gh": gh,
            "receiver": my_address,
            "amt": 10,
            "index": asset_id,
            "flat_fee": True
        }

maps=[]
maps.append(DataReader("Avitabile_AGB_Map"))

while True:
    latitude = float(input("latitude: "))
    longtitude = float(input("longtitude: "))

    ok=False
    for mapa in maps:
        if mapa.isInside(latitude,longtitude):
            print('Value is: {}'.format(mapa.getValue(latitude,longtitude)))
            ok=True

    if not ok:
        print("Coordinates are not supported")

tb=TreeBlockchain()
tb.createCertificate(7,50)
while True:
    latitude=float(input("latitude: "))
    longtitude=float(input("longtitude: "))
    if not tb.isForest(latitude,longtitude):
        print("There is forest")
        print("Creating certificate...")
        print(tb.getBenchmarkMapValue(latitude,longtitude))
        print("Certificate created")
    else:
        print("There is not a forest")


f = open('america_carbon_1km.tif', 'rb')

tags = exifread.process_file(f)

for tag in tags.keys():
    if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
        print("Key: %s, value %s" % (tag, tags[tag]))

ds = xr.open_rasterio("america_carbon_1km.tif")

ds.sel(lat=5, lon=-70, method='nearest').values
file_name="america_carbon_1km"
options_list = [
            '-ot Byte',
            '-of JPEG',
            '-b 1',
            '-scale'
        ]
options_string = " ".join(options_list)
gdal.Translate(file_name + '.jpg',
                file_name + '.tif',
                options=options_string)