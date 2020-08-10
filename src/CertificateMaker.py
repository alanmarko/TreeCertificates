"""
CertificateMaker.py

CertificateMaker.py implemnts core methods for creation, deletion and modification of Algorand certificates
It also allows possible transactions of certificates between two parties(useful for future implementation of trading of certificates).
"""

import json
import time
import base64
from algosdk import algod
from algosdk import mnemonic
from algosdk import transaction
from Certificate import Certificate
import Algorand

class CertificateMaker:
    def __init__(self):
        self.algod_address = "https://testnet-algorand.api.purestake.io/ps1"
        self.algod_token = ""
        headers = {
            "X-API-Key": "5K5TIs5wJtaqBNHNfOyya2mxDj9mQBEkYAqWgu09",
        }

        self.algod_client = algod.AlgodClient(self.algod_token, self.algod_address, headers)
        self.status = self.algod_client.status()
        #print(json.dumps(self.status, indent=4))

        passphrase = "thunder fun scout myself talk repeat hurry miracle puppy run vocal vicious shove fever idea lens above diesel action pulp before cigar horror above mass"

        self.private_key = mnemonic.to_private_key(passphrase)
        self.my_address = mnemonic.to_public_key(passphrase)
        print("My address: {}".format(self.my_address))

        self.account_info = self.algod_client.account_info(self.my_address)
        print("Account balance: {} microAlgos".format(self.account_info.get('amount')))

    def createCertificate(self,hash):
        c = Certificate("tmp", "tmp", "tmp", "tmp", "tmp", "tmp", "tmp", "tmp", "tmp", "tmp", "tmp", "tmp", "tmp",
                        "tmp", "tmp", "tmp")

        params = self.algod_client.suggested_params()
        first = params.get("lastRound")
        last = first + 1000
        gen = params.get("genesisID")
        gh = params.get("genesishashb64")
        min_fee = params.get("minFee")

        data = {
            "sender": self.my_address,
            "fee": min_fee,
            "first": first,
            "last": last,
            "gh": gh,
            "total": 1000,
            "decimals": 0,
            "default_frozen": False,
            "unit_name": "aa",
            "asset_name": "bb",
            "metadata_hash": bytearray(hash.digest()),
            "manager": self.my_address,
            "reserve": self.my_address,
            "freeze": self.my_address,
            "clawback": self.my_address,
            "url": "https://path/to/my/asset/details",
            "flat_fee": True
        }

        txn = transaction.AssetConfigTxn(**data)


        stxn = txn.sign(self.private_key)

        print("Asset Creation")

        txid = self.algod_client.send_transaction(stxn, headers={'content-type': 'application/x-binary'})

        txinfo = Algorand.wait_for_confirmation(self.algod_client, txid)
        #print(txinfo.keys())
        #print(txinfo)
        asset_id = txinfo["txresults"]["createdasset"]
        account_info = self.algod_client.account_info(self.my_address)
        print("The hash of certificate is: {}".format(hash.hexdigest()))

    def modifyCertificate(self,newhash):
        self.createCertificate(newhash)
        print("Certificate recreated")

    def revokeCertificate(self):
        data = {
            "sender": self.my_address,
            "fee": self.min_fee,
            "first": self.first,
            "last": self.last,
            "gh": self.gh,
            "receiver": self.my_address,
            "amt": 10,
            "index": self.asset_id,
            "revocation_target": self.my_address,
            "flat_fee": True
        }
        print("Asset Revoke")
        txn = transaction.AssetTransferTxn(**data)
        stxn = txn.sign(self.private_key)
        txid = self.algod_client.send_transaction(stxn, headers={'content-type': 'application/x-binary'})
        print(txid)
        Algorand.wait_for_confirmation(self.algod_client, txid)
        account_info = self.algod_client.account_info(self.my_address)
        print(json.dumps(account_info['assets'][str(self.asset_id)], indent=4))
        account_info = self.algod_client.account_info(self.my_address)
        print(json.dumps(account_info['assets'][str(self.asset_id)], indent=4))

    def doTransaction(self):
        data = {
            "sender": self.my_address,
            "fee": self.min_fee,
            "first": self.first,
            "last": self.last,
            "gh": self.gh,
            "receiver": self.my_address,
            "amt": 10,
            "index": self.asset_id,
            "flat_fee": True
        }
        print("Asset Transfer")
        txn = transaction.AssetTransferTxn(**data)
        stxn = txn.sign(self.private_key)
        txid = self.algod_client.send_transaction(stxn, headers={'content-type': 'application/x-binary'})
        print(txid)

        Algorand.wait_for_confirmation(self.algod_client, txid)
        account_info = self.algod_client.account_info(self.my_address)
        print(json.dumps(account_info['assets'][str(self.asset_id)], indent=4))