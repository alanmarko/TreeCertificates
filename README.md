# TreeCertificates
A significant problem with forest conservation and tree planting efforts is that there is currently no way to guarantee that a conserved forest or tree planted
would continue to be in existence at some future time. Yet, credit is given at the time of tree planting or when a forest conservation action is taken. 
This sets up a perverse incentive for a tree planter to make no effort to conserve trees after payment has been received.

This project implements interface that creates blockchain-based certificates linked to the existence of
trees, so that, if a tree is damaged or cut down, the certificate is declared void. Specifically,
it links satellite data to per-tree certificates on a blockchain. If a satellite image discovers that a tree is no longer present, then this would be
certified by an independent third-party, such as WCMC and placed on the blockchain, as well. This could trigger either penalty payments or a reduction in the number of carbon
credits available to the tree planter.

The application in its current form allows the user to specify the area of a forest(e.g. Gola Rainforest National Park). The application then downloads data from Hansen dataset
decribing the state of the forest, calculates the amount of carbon stored inside of the area and also checks whether there are no other certificates already in this area.
If not, the application creates new certificate for the forest storing both area information and the amount of carbon. It is then possible to modify the certificate or recalculate
it in case that the amount of carbon stored has changed(for example because some trees were cut).

## Installing
### Step 0.
In order to run the application, you need to have installed Anaconda3 terminal with python 3.7 on a Windows device.

### Step 1.
Recreate the enviroment used by:
```
conda env create -f environment.yml
```
Activate using
```
conda activate gdal_test
```

### Step 2.
As the application uses the earth engine it is necessary to first create an account at 
* https://console.developers.google.com/ 

and also register at 
* https://earthengine.google.com/signup/. 

It should take less then 24 hours to receive the authorisation.
Inside of the develepers console you should create a new Earth Engine API and download client_secrets.json file using the download button as described here:
* https://stackoverflow.com/questions/40136699/using-google-api-for-python-where-do-i-get-the-client-secrets-json-file-from

Finally replace the exisiting client_secrets.json file inside of TreeCertificates with the newly created one.

### Step 3.
In order to upload data to Google drive, the application asks for a file id. It can be any file from your google drive account. You can just select the file and copy the id from the url.

### Step 4.
You nee to download AVITABILE map from 
*http://lucid.wur.nl/storage/downloads/high-carbon-ecosystems/Avitabile_AGB_Map.zip
and put Avitabile_AGB_Map.tif file to into TreeCertificates folder.

### Step 5.
You can then run the application using:
```
python CertificationDemo.py
```
