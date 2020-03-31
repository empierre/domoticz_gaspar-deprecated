//##############################################################################
//  This file is part of domoticz_gaspar - https://github.com/empierre/domoticz_gaspar
//      Copyright (C) 2014-2018 Emmanuel PIERRE (domoticz@e-nef.com)
//
//  domoticz_gaspar is free software: you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation, either version 2 of the License, or
//  (at your option) any later version.
//
//  MyDomoAtHome is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with MyDomoAtHome.  If not, see <http://www.gnu.org/licenses/>.
//##############################################################################

var fs = require('fs');
var winston = require('winston');
global.logger = winston;

const path = require('path');

var devicerowid=process.argv[2];
var dateObj = new Date();
var q_year=dateObj.getUTCFullYear();
var q_month_s=dateObj.getUTCMonth();
var q_month_e=dateObj.getUTCMonth() + 1;
var q_day_s=dateObj.getUTCDate()-1;
var q_day_e=dateObj.getUTCDate();
var q_hour=dateObj.getHours();
var q_minutes=dateObj.getUTCMinutes();

var BASE_DIR = process.env.BASE_DIR || '/home/pi/domoticz/domoticz_gaspar';

function pad(n, width, z) {
  z = z || '0';
  n = n + '';
  return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}

function getTotal() {
        try {
                var fileExport = 'export_months_values.json';
                var filePath = path.resolve(BASE_DIR, fileExport);
                var obj = JSON.parse(fs.readFileSync(filePath, 'utf8'));

                var conso_cumul=0.0;
                for (var i = 0; i < Object.keys(obj).length; ++i) {
                         conso_cumul= conso_cumul+ (obj[i]["conso"]);
                }
                return(conso_cumul);
        } catch (e) {
                // It isn't accessible
                console.warn("-- Exception opening export_months_values.json : "+e);
        }

}
function generateDayHours() {
        var cumul=getCumulBefore(q_year,q_month_s);
        var mth=[ 'Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
        try {
                var fileExport = 'export_hours_values.json';
                var filePath = path.resolve(BASE_DIR, fileExport);
                var obj = JSON.parse(fs.readFileSync(filePath, 'utf8'));

                for (var i = 0; i < Object.keys(obj).length; ++i) {
                        var req_date=''+q_year+'-'+pad(q_month_e,2)+'-'+pad(q_day_s,2)+' '+pad(obj[i]["time"].substr(0, 5),5)+':00';
                        if (obj[i]["conso"]>=0) {
                                console.log('DELETE FROM \'Meter\' WHERE devicerowid='+devicerowid+' and date = \''+req_date+'\'; INSERT INTO \'Meter\' (DeviceRowID,Usage,Value,Date) VALUES ('+devicerowid+', \''+Math.round(obj[i]["conso"]*10000)+'\', \''+Math.round(cumul*1000)+'\', \''+req_date+'\');') ;
                                cumul=cumul+(obj[i]["conso"]);
                        }
                }
        } catch (e) {
                // It isn't accessible
                console.warn("-- Exception opening export_hours_values.json : "+e);
        }
}
function getCumulBefore(year,month) {
        // Bring back the year-month previous total as domoticz expect it
        var mth=[ 'Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
        conso_cumul=0
        try {
                var fileExport = 'export_months_values.json';
                var filePath = path.resolve(BASE_DIR, fileExport);
                var obj = JSON.parse(fs.readFileSync(filePath, 'utf8'));
                for (var i = 0; i < month-1; ++i) {
                         conso_cumul= conso_cumul + Number(obj[i]["conso"]);
                         // console.log(obj[i]["conso"])
                }
                //console.log(year+" "+month+" "+conso_cumul)
                return(conso_cumul);
        } catch (e) {
                // It isn't accessible
                console.log("Exception opening export_months_values.json : "+e);
                return(conso_cumul);
        }
}
function generateMonthDays() {
        var cumul=Number(getCumulBefore(q_year,q_month_s));
        //console.log(cumul)
        var mth=[ 'Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

        try {
                var fileExport = 'export_days_values.json';
                var filePath = path.resolve(BASE_DIR, fileExport);
                var obj = JSON.parse(fs.readFileSync(filePath, 'utf8'));
                for (var i = 0; i < Object.keys(obj).length; ++i) {
                        var req_date=pad(obj[i]["time"].substr(6, 4),4)+'-'+pad(obj[i]["time"].substr(3, 2),2)+'-'+pad(obj[i]["time"].substr(0, 2),2)
                        if (obj[i]["conso"]>=0) {
                                console.log('DELETE FROM \'Meter_Calendar\' WHERE devicerowid='+devicerowid+' and date = \''+req_date+'\'; INSERT INTO \'Meter_Calendar\' (DeviceRowID,Value,Counter,Date) VALUES ('+devicerowid+', \''+Number((obj[i]["conso"]*1000))+'\', \''+Math.round(cumul)+'\', \''+req_date+'\');') ;
                                cumul+=Number(obj[i]["conso"]);
                        }
                }
        } catch (e) {
                // It isn't accessible
                console.warn("-- Exception opening export_months_values.json : "+e);
        }
}


logger.add(winston.transports.File, {filename: './lnk95.log'});
generateMonthDays();
var req_date=''+q_year+'-'+pad(q_month_e,2)+'-'+pad(q_day_s,2)+' '+pad(q_hour,2)+':'+pad(q_minutes,2)+':00';
console.log('UPDATE DeviceStatus SET lastupdate = \''+req_date+'\' WHERE id = '+devicerowid+';');
//generateDayHours();
