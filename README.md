# domoticz_gaspar
Get Gazpar smart meter data and push it to domoticz
!!!Experimental!!! Not all is working, work in progress


If you appreciate this software, please show it off ! [![PayPal donate button](http://img.shields.io/paypal/donate.png?color=yellow)](https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=epierre@e-nef.com&currency_code=EUR&amount=&item_name=thanks "Donate once-off to this project using Paypal")

# create a device in Domoticz
- In Domoticz, go to hardware, create a virtual "rfx meter counter" or "Dummy".
- Then in Devices, add it to the devices. (mark down the id for later).
- When in Utility, edit the device and change it to Electric (instant+counter) type.

## modules to install

    sudo apt-get install sqlite3 node npm
    sudo apt-get install python3 python3-numpy python3-dateutil python3-requests
    npm install winston 
    git clone https://github.com/empierre/domoticz_gaspar.git

## rename configuration file, change login/pass/id

    cp _domoticz_gaspar.cfg domoticz_gaspar.cfg
    nano domoticz_gaspar.cfg

and change:

    GASPAR_USERNAME="nom.prenom@mail.com"
    GASPAR_PASSWORD="password"
    DOMOTICZ_ID=547

Where DOMOTICZ_ID is id device on domoticz. 

Configuration file will not be deleted in future updates.


## testing before launch

Manually launch

    ./domoticz_gaspar.sh

N.B. If login is not ok, you'll get a nodejs error on console for data will be missing (will be changed).

Then check the login credential if they are ok:

    domoticz_gaspar.log

If this is good, you'll get several json files in the directory

## Add to your cron tab (with crontab -e):

    30 7,17 * * * /home/pi/domoticz/domoticz_gaspar/domoticz_gaspar.sh
