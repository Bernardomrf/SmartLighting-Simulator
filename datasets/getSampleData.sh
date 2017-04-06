#!/bin/bash
: '
Data retrieved from https://trynthink.github.io/buildingsdatasets/
'

echo "Getting 'One year occupant behavior/environment data for medium U.S. office'..."
mkdir office_data
cd office_data
wget http://en.openei.org/datasets/dataset/e6bf2859-8e99-472d-a25d-3ada18e72c6d/resource/fbb6f8ee-daeb-457b-9468-2d8377b424bc/download/langevindata.txt.zip
wget http://en.openei.org/datasets/dataset/e6bf2859-8e99-472d-a25d-3ada18e72c6d/resource/08595a7f-600d-469b-beb7-392cb3491e49/download/langevincodebook.xlsx
echo "Unzipping"
unzip langevindata.txt.zip
rm -f langevindata.txt.zip
rm -rf __MACOSX
cd ..

echo "Getting 'Multifamily Programmable Thermostat Data'..."
mkdir hvac_temp_humidity
cd hvac_temp_humidity 
wget http://en.openei.org/datasets/dataset/a5ecab98-bd30-4450-a6e3-ebdec09360b6/resource/ffe69522-56e0-478f-8e4f-ed16bcb42060/download/multifamilyprogrammablethermostatdata.zip
echo "Unzipping"
unzip multifamilyprogrammablethermostatdata.zip
rm -f multifamilyprogrammablethermostatdata.zip
cd ..