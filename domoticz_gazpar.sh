#!/bin/sh

#Change below to your parameters
export GAZPAR_USERNAME="your@mail.com"
export GAZPAR_PASSWORD="yourpass"
BASE_DIR="/home/pi/domoticz//domoticz_gazpar"
DOMOTICZ_ID=547

#DO NOT TOUCH BELOW
export BASE_DIR
cd $BASE_DIR
python3 $BASE_DIR/gazpar_json.py -o "$BASE_DIR" >> $BASE_DIR/gazpar.log 2>&1

exit

node $BASE_DIR/domoticz_gazpar.js $DOMOTICZ_ID > req.sql
cat $BASE_DIR/req.sql | sqlite3 /home/pi/domoticz/domoticz.db
