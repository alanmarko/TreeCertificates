"""
CertificationInterface.py

CertificationInterface.py implements core methods for log-in to Google Earth Engine, receiving user input,
and calculating requested properties of selected forest such as the total amount of carbon stored and

In order to log-in to the Google Earth Engine it is necessary to create an account at console.developers.google and change client_secrets.json file

In order to see an example usage, please see CertificationDemo.py
"""

import datetime
import ee
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from PIL import Image
from osgeo import gdal
import numpy as np
import datetime

import json
import time
import base64
from algosdk import algod
from algosdk import mnemonic
from algosdk import transaction
import hashlib
import Algorand
import Editor
import sys
from time import sleep
import ProgressBar
from DataReader import DataReader
from CertificateMaker import CertificateMaker
from CertificateIndexer import CertificateIndexer
from CertificateIndexer import SavedHash

from constants import cell_size
from  constants import real_cell_size


class CertificationInterface:
    def __init__(self):
        print("Please log in to your google earth engine account.")
        ee.Authenticate()
        ee.Initialize()
        self.mapa=ee.Image("UMD/hansen/global_forest_change_2019_v1_7").select(['treecover2000'])
        self.loss=ee.Image("UMD/hansen/global_forest_change_2019_v1_7").select(['loss'])

        print("Please log in to your google drive account.")
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        self.drive = GoogleDrive(gauth)

        self.folder=input("Please enter google drive folder id for storing data (1i60BMqt5jJDGk7pspHaTJkcwElUmJzm6 for default): ")

    def downloadFromDrive(self, file_name):
        local_download_path = ''
        try:
            os.makedirs(local_download_path)
        except:
            pass

        # file iterator
        file_list = self.drive.ListFile(
            {'q': "'"+self.folder+"' in parents and trashed=false"}).GetList()

        for f in file_list:
            # by id.
            #print('title: %s, id: %s' % (f['title'], f['id']))
            fname = f['title']
            if fname == (file_name+'.tif'):
                #print('downloading to {}'.format(fname))
                f_ = self.drive.CreateFile({'id': f['id']})
                f_.GetContentFile(fname)

        options_list = [
            '-ot Byte',
            '-of JPEG',
            '-b 1',
            '-scale'
        ]
        options_string = " ".join(options_list)
        gdal.Translate(file_name + '.png',
                       file_name + '.tif',
                       options=options_string)

        im = Image.open(file_name + '.png')
        im.show()

    def uploadToDrive(self,population,File_Name,x1,y1,x2,y2):
        geometry = ee.Geometry.Rectangle( [x1,y1,x2,y2])

        task_config = {
            'region': geometry.coordinates().getInfo(),
            'scale': 50,
            'description': File_Name,
            'folder': 'fero'
        }

        task = ee.batch.Export.image.toDrive(population, **task_config)
        task.start()

        counter=0
        pb=ProgressBar.ProgressBar()
        while task.status()['state'] in ['READY', 'RUNNING']:
            #print(task.status())
            pb.printProgress(min(counter,66),66)
            time.sleep(1)
            counter+=1
        else:
            #print(task.status())
            pb.printProgress(100,100)
            print("")
            return


    def readSelectedArea(self,file_name,x1,y1,x2,y2):
        print()
        print("Please mark your forest.")
        e=Editor.Editor(file_name)

        im = Image.open(file_name+"bitmask" + '.png')
        imarray = np.array(im)
        height=imarray.shape[0]
        width=imarray.shape[1]
        #print(height)
        #print(width)
        bitmask=np.zeros((height//cell_size,width//cell_size),np.int)
        print("Reading bitmask:")
        pb=ProgressBar.ProgressBar()
        for i in range(5,bitmask.shape[0]*cell_size,cell_size):
            for j in range(5,bitmask.shape[1]*cell_size,cell_size):
                y=i//cell_size
                x=j//cell_size
                if (imarray[i][j] == [255,0,0]).all():
                    bitmask[y][x]=1
                elif (imarray[i][j] == [255,255,0]).all():
                    bitmask[y][x]=2
                elif (imarray[i][j] == [0,128,0]).all():
                    bitmask[y][x]=3
                else:
                    bitmask[y][x]=0
            pb.printProgress(i,height//cell_size)
        pb.printProgress(100,100)
        print()
        for i in range(0, bitmask.shape[0]):
            for j in range(0, bitmask.shape[1]):
                if bitmask[i][j] == 1:
                    print("R", end=" ")
                elif bitmask[i][j] == 2:
                    print("Y", end=" ")
                elif bitmask[i][j] == 3:
                    print("G", end=" ")
                else:
                    print(".", end=" ")
            print()

        total_carbon=self.calculateCarbon(file_name,bitmask,x1,y1)
        return (bitmask,total_carbon,x1,y1,datetime.datetime.now())

    def calculateCarbon(self,file_name,bitmask,x1,y1,x2,y2,width,height):
        imLoss = Image.open(file_name + "loss" + '.png')
        imarrayLoss = np.array(imLoss)
        total_loss = 0
        total_carbon = 0
        dr = DataReader("Avitabile_AGB_Map")
        print("Calculating the total amount of carbon:")
        pb = ProgressBar.ProgressBar()
        for i in range(0, bitmask.shape[0]):
            for j in range(0, bitmask.shape[1]):
                if not bitmask[i][j] > 0:
                    continue
                lossSum = 0
                cellCarbon = 0
                for k in range(0, cell_size):
                    for l in range(0, cell_size):
                        y = i * cell_size + k
                        x = j * cell_size + l
                        lossSum += (imarrayLoss[y][x] // 255)
                        longtitude = (x2 - x1) * (x / width) + x1
                        latitude = (y2 - y1) * (y / height) + y1

                        carbonValue = dr.getValue(latitude, longtitude) * (1 - (imarrayLoss[y][x] // 255))

                        if carbonValue < 0:
                            carbonValue = 0

                        cellCarbon += carbonValue

                cellCarbon /= cell_size * cell_size

                aliveCells = cell_size * cell_size - lossSum
                total_loss += lossSum
                total_carbon += cellCarbon
            pb.printProgress(i, bitmask.shape[0])
        pb.printProgress(100, 100)
        total_carbon *= 900
        return total_carbon

    def tidyCoordinate(self,x):
        count=int(round(x/real_cell_size))
        res=count*real_cell_size
        return res

    def getArea(self):
        print()
        print("Please enter the bounding rectangle of your forest.")
        print("Gola Rainforest National Park has coordinates (7.997,-11.535,7.2,-10.387).")
        self.y1 = float(input("Top-Left latitude:"))
        self.x1 = float(input("Top-Left longtitude:"))
        self.y2 = float(input("Bottom-Right longtitude:"))
        self.x2 = float(input("Bottom-Right longtitude:"))

        self.y1= self.tidyCoordinate(self.y1)
        self.x1 = self.tidyCoordinate(self.x1)
        self.y2 = self.tidyCoordinate(self.y2)
        self.x2 = self.tidyCoordinate(self.x2)

        print()
        self.file_name="img"+str(self.y1)+str(self.x1)
        print("Downloading tree cover data:")
        self.uploadToDrive(self.mapa,self.file_name,self.x1,self.y1,self.x2,self.y2)
        self.downloadFromDrive(self.file_name)

        print("Downloading forest loss data:")
        self.uploadToDrive(self.loss,self.file_name+"loss",self.x1,self.y1,self.x2,self.y2)
        self.downloadFromDrive(self.file_name+"loss")

        #input("Please select area to work with")

        return self.readSelectedArea(self.file_name,self.x1,self.y1,self.x2,self.y2)



