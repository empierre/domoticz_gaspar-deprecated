
# pre-requisite: activate load curve recording on GrDf website
enable your GrDf account (https://monespace.grdf.fr/monespace/particulier/accueil) and the data collection ("Consommation" > "Gérer ma courbe de charge" > "Activer ma courbe de charge")

# domoticz_gaspar
get Gazpar smart meter data and push it to domoticz

# create a device in Domoticz
- In Domoticz, go to hardware, create a virtual "rfx meter counter".
- Then in Devices, add it to the devices. (mark down the id for later).
- When in Utility, edit the device and change it to Electricity type.

## modules to install

    sudo apt-get install sqlite3
    sudo apt-get install python3 python3-numpy python3-dateutil python3-requests
    npm install winston 
    git clone https://github.com/empierre/domoticz_gaspar.git

## change login and pass, base dir of this script and domoticz path

    nano domoticz_gazpar.sh

and change:

    export GAZPAR_USERNAME="nom.prenom@mail.com"
    export GAZPAR_PASSWORD="password"
    BASE_DIR="/home/pi/domoticz/domoticz_gaspar"
    DOMOTICZ_ID=547


## testing before launch

Manually launch

    ./domoticz_gazpar.sh

N.B. If login is not ok, you'll get a nodejs error on console for data will be missing (will be changed).

Then check the login credential if they are ok:

    gazpar.log

If this is good, you'll get several json files in the directory

## Add to your cron tab (with crontab -e):

    30 7,17 * * * /home/pi/domoticz/domoticz_gaspar/domoticz_gazpar.sh
