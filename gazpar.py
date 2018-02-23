#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Retrieves energy consumption data from your GrDf account.
"""
# Linkindle - Linky energy consumption curves on a Kindle display.
# Copyright (C) 2016 Baptiste Candellier
# Adapted to gazpar (C) 2018 epierre
#
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

import base64
import requests
import html
import sys
import os
import re
import logging
from lxml import etree
import xml.etree.ElementTree as ElementTree
import io


LOGIN_BASE_URI = 'https://monespace.grdf.fr/web/guest/monespace'
API_BASE_URI = 'https://monespace.grdf.fr/monespace/particulier'
JAVAVXS = ''

API_ENDPOINT_LOGIN = '?p_p_id=EspacePerso_WAR_EPportlet&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_cacheability=cacheLevelPage&p_p_col_id=column-2&p_p_col_count=1&_EspacePerso_WAR_EPportlet__jsfBridgeAjax=true&_EspacePerso_WAR_EPportlet__facesViewIdResource=%2Fviews%2FespacePerso%2FseconnecterEspaceViewMode.xhtml'
API_ENDPOINT_HOME = '/accueil'
API_ENDPOINT_DATA = '/consommation/tableau-de-bord'

DATA_NOT_REQUESTED = -1
DATA_NOT_AVAILABLE = -2

class LinkyLoginException(Exception):
    """Thrown if an error was encountered while retrieving energy consumption data."""
    pass

class GazparServiceException(Exception):
    """Thrown when the webservice threw an exception."""
    pass


def parse_lxml(c):
    root = etree.fromstring(c)
    log=root.xpath("//update[@id = 'javax.faces.ViewState']")
    return(log[0].text)

def login(username, password):
    """Logs the user into the Linky API.
    """
    session = requests.Session()

    payload = {
               'javax.faces.partial.ajax': 'true',
               'javax.faces.source': '_EspacePerso_WAR_EPportlet_:seConnecterForm:meConnecter',
               'javax.faces.partial.execute': '_EspacePerso_WAR_EPportlet_:seConnecterForm',
               'javax.faces.partial.render': 'EspacePerso_WAR_EPportlet_:global _EspacePerso_WAR_EPportlet_:groupTitre',
               'javax.faces.behavior.event': 'click',
               'javax.faces.partial.event': 'click',
               '_EspacePerso_WAR_EPportlet_:seConnecterForm': '_EspacePerso_WAR_EPportlet_:seConnecterForm',
               'javax.faces.encodedURL': 'https://monespace.grdf.fr/web/guest/monespace?p_p_id=EspacePerso_WAR_EPportlet&amp;p_p_lifecycle=2&amp;p_p_state=normal&amp;p_p_mode=view&amp;p_p_cacheability=cacheLevelPage&amp;p_p_col_id=column-2&amp;p_p_col_count=1&amp;_EspacePerso_WAR_EPportlet__jsfBridgeAjax=true&amp;_EspacePerso_WAR_EPportlet__facesViewIdResource=%2Fviews%2FespacePerso%2FseconnecterEspaceViewMode.xhtml',
               '_EspacePerso_WAR_EPportlet_:seConnecterForm:email': username,
               '_EspacePerso_WAR_EPportlet_:seConnecterForm:passwordSecretSeConnecter': password
               }

    session.headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Mobile Safari/537.36',
                'Accept-Language':'fr,fr-FR;q=0.8,en;q=0.6',
                'Accept-Encoding':'gzip, deflate, br', 
                'Accept':'application/xml, application/json, text/javascript, */*; q=0.01',
                'Faces-Request':'partial/ajax',
                'Origin':'https://monespace.grdf.fr',
                'Referer':'https://monespace.grdf.fr/monespace/connexion'}

    session.cookies['KPISavedRef'] ='https://monespace.grdf.fr/monespace/connexion'

    session.get(LOGIN_BASE_URI + API_ENDPOINT_LOGIN, data=payload, allow_redirects=False)
    
    req = session.post(LOGIN_BASE_URI + API_ENDPOINT_LOGIN, data=payload, allow_redirects=False)

    javaxvs=parse_lxml(req.text)

    global JAVAVXS

    JAVAVXS=javaxvs

#    print(session.cookies.get_dict())

    #2nd request
    payload = {
               'javax.faces.partial.ajax': 'true',
               'javax.faces.source': '_EspacePerso_WAR_EPportlet_:seConnecterForm:meConnecter',
               'javax.faces.partial.execute': '_EspacePerso_WAR_EPportlet_:seConnecterForm',
               'javax.faces.partial.render': 'EspacePerso_WAR_EPportlet_:global _EspacePerso_WAR_EPportlet_:groupTitre',
               'javax.faces.behavior.event': 'click',
               'javax.faces.partial.event': 'click',
               'javax.faces.ViewState': javaxvs,
               '_EspacePerso_WAR_EPportlet_:seConnecterForm': '_EspacePerso_WAR_EPportlet_:seConnecterForm',
               'javax.faces.encodedURL': 'https://monespace.grdf.fr/web/guest/monespace?p_p_id=EspacePerso_WAR_EPportlet&amp;p_p_lifecycle=2&amp;p_p_state=normal&amp;p_p_mode=view&amp;p_p_cacheability=cacheLevelPage&amp;p_p_col_id=column-2&amp;p_p_col_count=1&amp;_EspacePerso_WAR_EPportlet__jsfBridgeAjax=true&amp;_EspacePerso_WAR_EPportlet__facesViewIdResource=%2Fviews%2FespacePerso%2FseconnecterEspaceViewMode.xhtml',
               '_EspacePerso_WAR_EPportlet_:seConnecterForm:email': username,
               '_EspacePerso_WAR_EPportlet_:seConnecterForm:passwordSecretSeConnecter': password
	}


    req = session.post(LOGIN_BASE_URI + API_ENDPOINT_LOGIN, data=payload, allow_redirects=False)
    #print(payload)
    session_cookie = req.cookies.get('GRDF_EP')
    #print(session_cookie)

    if not 'GRDF_EP' in session.cookies:
        raise LinkyLoginException("Login unsuccessful. Check your credentials.")

    return session


def get_data_per_hour(session, start_date, end_date):
    """Retreives hourly energy consumption data."""
    return _get_data(session, 'urlCdcHeure', start_date, end_date)

def get_data_per_day(session, start_date, end_date):
    """Retreives daily energy consumption data."""
    return _get_data(session, 'urlCdcJour', start_date, end_date)

def get_data_per_month(session, start_date, end_date):
    """Retreives monthly energy consumption data."""
    return _get_data(session, 'urlCdcMois', start_date, end_date)

def get_data_per_year(session):
    """Retreives yearly energy consumption data."""
    return _get_data(session, 'urlCdcAn')

def _get_data(session, resource_id, start_date=None, end_date=None):

    session.headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Mobile Safari/537.36',
                'Accept-Language':'fr,fr-FR;q=0.8,en;q=0.6',
                'Accept-Encoding':'gzip, deflate, br', 
                'Accept':'application/xml, application/json, text/javascript, */*; q=0.01',
                'Faces-Request':'partial/ajax',
                'Origin':'https://monespace.grdf.fr',
                'Referer':'https://monespace.grdf.fr/monespace/particulier/consommation/tableau-de-bord',
                'X-Requested-With':'XMLHttpRequest'}

    payload = {
                'javax.faces.partial.ajax':'true',
                'javax.faces.source':'_eConsosynthese_WAR_eConsoportlet_:j_idt5:j_idt121',
                'javax.faces.partial.execute':'_eConsosynthese_WAR_eConsoportlet_:j_idt5:j_idt121',
                'javax.faces.partial.render':'_eConsosynthese_WAR_eConsoportlet_:j_idt5',
                'javax.faces.behavior.event':'click',
                'javax.faces.partial.event':'click',
                '_eConsosynthese_WAR_eConsoportlet_':'j_idt5:_eConsosynthese_WAR_eConsoportlet_:j_idt5',
                'javax.faces.encodedURL':'https://monespace.grdf.fr/web/guest/monespace/particulier/consommation/tableau-de-bord?p_p_id=eConsosynthese_WAR_eConsoportlet&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_cacheability=cacheLevelPage&p_p_col_id=column-3&p_p_col_count=5&p_p_col_pos=1&_eConsosynthese_WAR_eConsoportlet__jsfBridgeAjax=true&_eConsosynthese_WAR_eConsoportlet__facesViewIdResource=%2Fviews%2Fcompteur%2Fsynthese%2FsyntheseViewMode.xhtml',
               'javax.faces.ViewState': JAVAVXS }


    params = {
               'p_p_id':'eConsosynthese_WAR_eConsoportlet',
               'p_p_lifecycle':'2',
               'p_p_state':'normal',
               'p_p_mode':'view',
               'p_p_cacheability':'cacheLevelPage',
               'p_p_col_id':'column-3',
               'p_p_col_count':'5',
               'p_p_col_pos':'1',
               '_eConsosynthese_WAR_eConsoportlet__jsfBridgeAjax':'true',
               '_eConsosynthese_WAR_eConsoportlet__facesViewIdResource':'/views/compteur/synthese/syntheseViewMode.xhtml' }

    r=session.get('https://monespace.grdf.fr/monespace/particulier/consommation/tableau-de-bord', allow_redirects=False)

    #m = re.search("ViewState\" +value=\"(.*?)\"", r.text)
    #value = m.group(1)
    parser = etree.HTMLParser()
    tree   = etree.parse(io.StringIO(r.text), parser)
    value=tree.xpath("//div[@id='_eConsosynthese_WAR_eConsoportlet_']/form[@id='_eConsosynthese_WAR_eConsoportlet_:j_idt5']/input[@id='javax.faces.ViewState']/@value")


    print(value)
    global JAVAVXS
    JAVAVXS=value

    payload = {
                'javax.faces.partial.ajax':'true',
                'javax.faces.source':'_eConsosynthese_WAR_eConsoportlet_:j_idt5:j_idt121',
                'javax.faces.partial.execute':'_eConsosynthese_WAR_eConsoportlet_:j_idt5:j_idt121',
                'javax.faces.partial.render':'_eConsosynthese_WAR_eConsoportlet_:j_idt5',
                'javax.faces.behavior.event':'click',
                'javax.faces.partial.event':'click',
                '_eConsosynthese_WAR_eConsoportlet_':'j_idt5:_eConsosynthese_WAR_eConsoportlet_:j_idt5',
                'javax.faces.encodedURL':'https://monespace.grdf.fr/web/guest/monespace/particulier/consommation/tableau-de-bord?p_p_id=eConsosynthese_WAR_eConsoportlet&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_cacheability=cacheLevelPage&p_p_col_id=column-3&p_p_col_count=5&p_p_col_pos=1&_eConsosynthese_WAR_eConsoportlet__jsfBridgeAjax=true&_eConsosynthese_WAR_eConsoportlet__facesViewIdResource=%2Fviews%2Fcompteur%2Fsynthese%2FsyntheseViewMode.xhtml',
               'javax.faces.ViewState': JAVAVXS }



    session.cookies['KPISavedRef'] ='https://monespace.grdf.fr/monespace/particulier/consommation/tableau-de-bord'

    req = session.post('https://monespace.grdf.fr/monespace/particulier/consommation/tableau-de-bord', allow_redirects=False, data=payload, params=params)
    #print(session.headers)
    #print(session.cookies)
    #print(payload)
    #print(req.text)

    # We send the session token so that the server knows who we are
    payload = {
               'javax.faces.partial.ajax':'true',
               'javax.faces.source':'_eConsosynthese_WAR_eConsoportlet_:j_idt5:j_idt25:2',
               'javax.faces.partial.execute':'_eConsosynthese_WAR_eConsoportlet_:j_idt5:j_idt25',
               'javax.faces.partial.render':'_eConsosynthese_WAR_eConsoportlet_:j_idt5:chartHisto',
               'javax.faces.behavior.event':'change',
               'javax.faces.partial.event':'change',
               'javax.faces.ViewState': JAVAVXS,
               '_eConsosynthese_WAR_eConsoportlet_':'j_idt5:_eConsosynthese_WAR_eConsoportlet_:j_idt5',
               'javax.faces.encodedURL':'https://monespace.grdf.fr/web/guest/monespace/particulier/consommation/tableau-de-bord?p_p_id=eConsosynthese_WAR_eConsoportlet&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_cacheability=cacheLevelPage&p_p_col_id=column-3&p_p_col_count=5&p_p_col_pos=1&_eConsosynthese_WAR_eConsoportlet__jsfBridgeAjax=true&_eConsosynthese_WAR_eConsoportlet__facesViewIdResource=%2Fviews%2Fcompteur%2Fsynthese%2FsyntheseViewMode.xhtml',
               '_eConsosynthese_WAR_eConsoportlet_:j_idt5:j_idt25':'Jour'
    }

    params = {
               'p_p_id':'eConsosynthese_WAR_eConsoportlet',
               'p_p_lifecycle':'2',
               'p_p_state':'normal',
               'p_p_mode':'view',
               'p_p_cacheability':'cacheLevelPage',
               'p_p_col_id':'column-3',
               'p_p_col_count':'5',
               'p_p_col_pos':'1',
               '_eConsosynthese_WAR_eConsoportlet__jsfBridgeAjax':'true',
               '_eConsosynthese_WAR_eConsoportlet__facesViewIdResource':'/views/compteur/synthese/syntheseViewMode.xhtml'
    }

    session.cookies['KPISavedRef'] ='https://monespace.grdf.fr/monespace/particulier/consommation/tableau-de-bord'

    req = session.post('https://monespace.grdf.fr/monespace/particulier/consommation/tableau-de-bord', allow_redirects=False, data=payload, params=params)

    #print(payload)
    #print(req.text)
    m = re.search("categories = \"(.*?)\"", req.text)
    value = m.group(1)
    print(value)
    m = re.search("donneesCourante = \"(.*?)\"", req.text)
    value = m.group(1)
    print(value)

    if 300 <= req.status_code < 400:
        # So... apparently, we may need to do that once again if we hit a 302
        # ¯\_(ツ)_/¯
        req = session.post(API_BASE_URI + API_ENDPOINT_DATA, allow_redirects=False, data=payload, params=params)

    if req.status_code == 200 and req.text is not None and "Conditions d'utilisation" in req.text:
        raise GazparLoginException("You need to accept the latest Terms of Use. Please manually log into the website, "
                                  "then come back.")

    try:
        res = req.json()
    except:
        logging.info("Unable to log in")
        sys.exit(os.EX_SOFTWARE)

    if res['etat'] and res['etat']['valeur'] == 'erreur' and res['etat']['erreurText']:
        raise GazparServiceException(html.unescape(res['etat']['erreurText']))

    return res
