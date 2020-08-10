"""
Example.py

Example.py shows example usage of classes such as CertificationInterface, CertificateMaker and CertificateIndexer in an application
that allows user to input area of a forest, downloads data from the Hansen dataset, calculates the amount of stored carbon and
also creates a new certificate if the input was valid. It is possible to later modify or recalculate the certificate.
"""

import hashlib

from CertificateIndexer import CertificateIndexer
from CertificateMaker import CertificateMaker
from CertificationInterface import CertificationInterface
import ProgressBar

import time
from time import sleep

import sys


ce=CertificateIndexer()
lr=CertificationInterface()
cm=CertificateMaker()

def makeCertificate(res):
    print('The total amount of carbon stored in the selected area is ' + str(res[1]) + ' Mg')
    h = hashlib.sha256(str(res).encode())
    # h = hashlib.sha256(str("gd").encode())
    print()
    pb = ProgressBar.ProgressBar()
    print("Checking whether there are no conflicting certificates inside of the selected area: ")
    for i in range(100):
        pb.printProgress(i, 100)
        sleep(0.1)
    pb.printProgress(100, 100)
    print()
    if ce.checkMarkingCorrectness(res):
        print("No conflicting certificates found.")
        print("Recording the new hash value.")
        ce.writeHashValue(bytearray(h.digest()), res)
        print()
        cm.modifyCertificate(h)
        print()
    else:
        print("Conflicting certificates found.")



print("Welcome to Blockchain Certificates for Trees!")
print()
res=lr.getArea()
#print(str(res))

makeCertificate(res)

while True:
    print("Do you want to change or recalculate the certificate for this forest?")
    ans=input("Y=Yes Q=Quit: ")
    if ans == "Y":
        res=lr.readSelectedArea(lr.file_name,lr.x1,lr.y1,lr.x2,lr.y2)
        makeCertificate(res)
    else:
        sys.exit()