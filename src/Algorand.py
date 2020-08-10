"""
Algorand.py

Algorand.py was used to demonstrate the usage of Algorand blockchain,
creation, deletion and transaction of certificates via Algorand assets.
The demo log-ins to pre-created account specified by the 25 word passphrase.
"""

import json
import time
import base64
from algosdk import algod
from algosdk import mnemonic
from algosdk import transaction


def wait_for_confirmation(algod_client, txid):
    while True:
        txinfo = algod_client.pending_transaction_info(txid)
        if txinfo.get('round') and txinfo.get('round') > 0:
            print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('round')))
            break
        else:
            print("Waiting for confirmation...")
            algod_client.status_after_block(algod_client.status().get('lastRound') + 1)
    return txinfo


def algorandSequence():
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

    params = algod_client.suggested_params()
    note = "Hello World".encode()
    receiver = "GD64YIY3TWGDMCNPP553DZPPR6LDUSFQOIJVFDPPXWEG3FVOJCCDBBHU5A"

    data = {
        "sender": my_address,
        "receiver": receiver,
        "fee": params.get('minFee'),
        "flat_fee": True,
        "amt": 20,
        "first": params.get('lastRound'),
        "last": params.get('lastRound') + 1000,
        "note": note,
        "gen": params.get('genesisID'),
        "gh": params.get('genesishashb64')
    }

    txn = transaction.PaymentTxn(**data)
    signed_txn = txn.sign(private_key)
    txid = signed_txn.transaction.get_txid()
    print("Signed transaction with txID: {}".format(txid))

    algod_client.send_transaction(signed_txn, headers={'content-type': 'application/x-binary'})

    wait_for_confirmation(algod_client, txid)

    try:
        confirmed_txn = algod_client.transaction_info(my_address, txid)
    except Exception as err:
        print(err)
    print("Transaction information: {}".format(json.dumps(confirmed_txn, indent=4)))
    print("Decoded note: {}".format(base64.b64decode(confirmed_txn.get('noteb64')).decode()))


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

    def hashuj(self):
        h=bytearray(abs(hash(str(self))).to_bytes(32,byteorder="big"))
        return h

def certifacateDeletionDemo(hash):
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

    c = Certificate("tmp", "tmp", "tmp", "tmp", "tmp", "tmp", "tmp", "tmp", "tmp", "tmp","tmp", "tmp", "tmp","tmp", "tmp", "tmp")

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
        "metadata_hash": hash,
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


    txinfo = wait_for_confirmation(algod_client, txid)
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

        wait_for_confirmation(txid)

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
    print("Asset Transfer")
    txn = transaction.AssetTransferTxn(**data)
    stxn = txn.sign(private_key)
    txid = algod_client.send_transaction(stxn, headers={'content-type': 'application/x-binary'})
    print(txid)
    wait_for_confirmation(algod_client, txid)
    account_info = algod_client.account_info(my_address)
    print(json.dumps(account_info['assets'][str(asset_id)], indent=4))

    # Revoking an Asset
    data = {
        "sender": my_address,
        "fee": min_fee,
        "first": first,
        "last": last,
        "gh": gh,
        "receiver": my_address,
        "amt": 10,
        "index": asset_id,
        "revocation_target": my_address,
        "flat_fee": True
    }
    print("Asset Revoke")
    txn = transaction.AssetTransferTxn(**data)
    stxn = txn.sign(private_key)
    txid = algod_client.send_transaction(stxn, headers={'content-type': 'application/x-binary'})
    print(txid)
    wait_for_confirmation(algod_client, txid)
    account_info = algod_client.account_info(my_address)
    print(json.dumps(account_info['assets'][str(asset_id)], indent=4))
    account_info = algod_client.account_info(my_address)
    print(json.dumps(account_info['assets'][str(asset_id)], indent=4))


#createAsset()
