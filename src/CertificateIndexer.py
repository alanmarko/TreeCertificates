"""
CertificateIndexer.py

CertificateIndexer.py desciribes a class used in order to search for data in the current state of the blockchain
It provides methods for finding all certificate hashes inside of the Algorand blockchain,
finding the value that belongs to the hash, and checking correctness of potential new certificate( prevents double-selling)
There is a file called "hashes" that used for storing values belonging to a particular hash
"""

import json
from algosdk.v2client import indexer

import json
import time
import base64
from algosdk import algod
from algosdk import mnemonic
from algosdk import transaction
import hashlib
import Algorand
import numpy as np
import pickle

class SavedHash(object):
    def __init__(self,bytehash,value):
        self.bytehash=bytehash
        self.value=value

class CertificateIndexer:
    def __init__(self):
        self.myindexer = indexer.IndexerClient(indexer_token="", indexer_address="https://testnet-algorand.api.purestake.io/idx2")
        self.savedHashes=[]
        self.getHashValues()

    def getAllCertificateHashes(self):
        nexttoken = ""
        numtx = 1

        hashes=[]

        while (numtx > 0):
            response = self.myindexer.search_transactions_by_address(
                    address="XIU7HGGAJ3QOTATPDSIIHPFVKMICXKHMOR2FJKHTVLII4FAOA3CYZQDLG4",
                    start_time="2020-07-07T10:00:00-05:00",
                    next_page=nexttoken)
            transactions = response['transactions']
            numtx = len(transactions)
            if (numtx > 0):
                nexttoken = response['next-token']
                hash=response['metadata_hash']
                hashes.append(hash)

        return hashes

    def getAllHashes(self):
        #print("getAllHashes")
        input=open("hashes","rb")
        savedHashes=[]
        while True:
            try:
                sh=pickle.load(input)
                savedHashes.append(sh.bytehash)
                #print(sh.bytehash)
                #print(sh.value)
            except EOFError:
                break
        return savedHashes

    def writeHashValue(self,hash,data):
        output=open('hashes', 'ab')
        sh=SavedHash(hash,data)
        pickle.dump(sh,output,pickle.HIGHEST_PROTOCOL)

    def getHashValues(self):
        #print("getHashesDebug")
        input=open("hashes","rb")
        self.savedHashes=[]
        while True:
            try:
                sh=pickle.load(input)
                self.savedHashes.append(sh)
                #print(sh.bytehash)
                #print(sh.value)
            except EOFError:
                break
        return self.savedHashes

    def valueOfHash(self, hash):
        #self.savedHashes=self.getHashValues()

        for sh in self.savedHashes:
            if sh.bytehash == hash:
                #print("found")
                return sh.value
        #print("not foung")
        return None

    def getListOfSquares(self,tuple):
        bitmask=tuple[0]
        x1=tuple[2]
        y1=tuple[3]
        height=bitmask.shape[0]
        width=bitmask.shape[1]
        real_cell_size=0.027016

        cells=[]

        for i in range(height):
            for j in range(width):
                if bitmask[i][j] == 0:
                    continue
                x=x1+real_cell_size*j+real_cell_size/2
                y=y1+real_cell_size*i+real_cell_size/2

                countx=int(round(x/real_cell_size))
                county=int(round(y/real_cell_size))

                cells.append((countx,county))

        return cells

    def hasIntersection(self,a,b):
        if len(list(set(a)&set(b))) > 0:
            print(list(set(a)&set(b)))
            return True
        return False

    def checkMarkingCorrectness(self,marking):
        self.getHashValues()
        certificateHashes=self.getAllHashes()#self.getAllCertificateHashes()
        savedHashes=self.getAllHashes()
        squareLists=[]
        for cerHash in certificateHashes:
            value=self.valueOfHash(cerHash)
            squareLists.append(self.getListOfSquares(value))

        newSquares=self.getListOfSquares(marking)

        for squares in squareLists:
            if self.hasIntersection(squares,newSquares):
                return False

        return True

#Example

"""
ce=CertificateIndexer()

bitmask=np.zeros((2,2),np.int)
bitmask[0][0]=0
bitmask[1][0]=1
bitmask[0][1]=1
bitmask[1][1]=1
res=(bitmask,5.0,14.0,12.0)
#ce.writeHashValue(bytearray(hashlib.sha256(str(res).encode()).digest()),res)
ba=bytearray(hashlib.sha256(str(res).encode()).digest())
if ce.checkMarkingCorrectness(res):
    print("No conflicts")
else:
    print("Conflicts found")
"""
#ce.writeHashValue(bytearray(hashlib.sha256("fdsdfs".encode()).digest()),"ssss")
#ce.writeHashValue(bytearray(hashlib.sha256("rggg".encode()).digest()),"Nice!")
#ce.getHashValues()
#print(ce.valueOfHash(bytearray(hashlib.sha256("rggg".encode()).digest())))