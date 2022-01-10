# domoticz_gaspar
Get Gazpar smart meter data and push it to domoticz

If you appreciate this software, please show it off ! [![PayPal donate button](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=epierre@e-nef.com&currency_code=EUR&amount=&item_name=thanks "Donate once-off to this project using Paypal")

This module has been deprecated, please use : https://github.com/Scrat95220/DomoticzGazpar

If you want to migrate your history from a General KwH to a Managed counter, you can use the migrate.pl script here:

Usage:
./migrate.pl old_device_id new_device_id

Output:
req.sql

how to integrate it:
cat req.sql | sqlite3 domoticz.db
 
