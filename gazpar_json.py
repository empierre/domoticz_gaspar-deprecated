#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Adapted to gazpar (C) 2018 epierre
"""Generates energy consumption JSON files from GrDf consumption data
collected via their  website (API).
"""

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import datetime
import logging
import sys
import json
import gazpar
from dateutil.relativedelta import relativedelta
from lxml import etree
import xml.etree.ElementTree as ElementTree

USERNAME = os.environ['GAZPAR_USERNAME']
PASSWORD = os.environ['GAZPAR_PASSWORD']
BASEDIR = os.environ['BASE_DIR']

# Generate y axis (consumption values) 
def generate_y_axis(res):
    y_values = []

    # Extract data points from the source dictionary into a list
    for ordre, datapoint in enumerate(res['graphe']['data']):
        value = datapoint['valeur']

        # Remove any invalid values
        # (they're error codes on the API side, but useless here)
        if value < 0:
            value = 0

        y_values.insert(ordre, value)

    return y_values

# Generate x axis (time values)  
def generate_x_axis(res, time_delta_unit, time_format, inc):
    x_values = []

    # Extract start date and parse it
    start_date_queried_str = res['graphe']['periode']['dateDebut']
    start_date_queried = datetime.datetime.strptime(start_date_queried_str, "%d/%m/%Y").date()

    # Calculate final start date using the "offset" attribute returned by the API
    kwargs = {}
    kwargs[time_delta_unit] = res['graphe']['decalage'] * inc
    start_date = start_date_queried - relativedelta(**kwargs)

    # Generate X axis time labels for every data point
    for ordre, _ in enumerate(res['graphe']['data']):
        kwargs = {}
        kwargs[time_delta_unit] = ordre * inc
        x_values.insert(ordre, (start_date + relativedelta(**kwargs)).strftime(time_format))

    return x_values

# Date formatting 
def dtostr(date):
    return date.strftime("%d/%m/%Y")


# Export the JSON file for half-hours power measure (for the last pas day)
def export_hours_values(res):
    with open(BASEDIR+"/export_hours_values.json", 'w+') as outfile:
        json.dump(res, outfile)

# Export the JSON file for weekly consumption 
def export_weeks_values(res):
    with open(BASEDIR+"/export_weeks_values.json", 'w+') as outfile:
        json.dump(res, outfile)

# Export the JSON file for daily consumption (for the past rolling 30 days)
def export_days_values(res):
    with open(BASEDIR+"/export_days_values.json", 'w+') as outfile:
        json.dump(res, outfile)


# Export the JSON file for monthly consumption (for the current year, starting 12 months from today)
def export_months_values(res):
    with open(BASEDIR+"/export_months_values.json", 'w+') as outfile:
        json.dump(res, outfile)

# Export the JSON file for yearly consumption
def export_years_values(res):
    with open(BASEDIR+"/export_years_values.json", 'w+') as outfile:
        json.dump(res, outfile)




# Main script 
def main():
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

    try:
        logging.info("logging in as %s...", USERNAME)
        token = gazpar.login(USERNAME, PASSWORD)
        logging.info("logged in successfully!")

        logging.info("retrieving data...")
        today = datetime.date.today()
        
        # Years
        res_year = gazpar.get_data_per_year(token)

        # 12 months ago - today
        res_month = gazpar.get_data_per_month(token, dtostr(today - relativedelta(months=11)), \
                                             dtostr(today))

        # Weeks
        res_week = gazpar.get_data_per_week(token, dtostr(today - relativedelta(months=11)), \
                                             dtostr(today))

        # One month ago - yesterday
        res_day = gazpar.get_data_per_day(token, dtostr(today - relativedelta(days=1, months=1)), \
                                         dtostr(today - relativedelta(days=1)))


        # Yesterday 
        #res_hour = gazpar.get_data_per_hour(token, dtostr(today - relativedelta(days=2)), \
        #                                   dtostr(today - relativedelta(days=1)))
        

        logging.info("got data!")
############################################
		# Export of the JSON files, with exception handling as Enedis website is not robust and return empty data often
#        try:
#            export_hours_values(res_hour)
#        except Exception as exc:
#        	# logging.info("hours values non exported")
#            logging.error(exc)

        try:
            export_days_values(res_day)
        except Exception:
            logging.info("days values non exported")
            sys.exit(70)

        try:
            export_weeks_values(res_week)
        except Exception:
            logging.info("weeks values non exported")

        try:
            export_months_values(res_month)
        except Exception:
            logging.info("months values non exported")

        try:
            export_years_values(res_year)
        except Exception:
        	logging.info("years values non exported")

############################################
 
    except gazpar.LinkyLoginException as exc:
        logging.error(exc)
        sys.exit(1)



if __name__ == "__main__":
    main()
