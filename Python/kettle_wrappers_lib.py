#!/usr/bin/python
# coding: utf-8
'''
import pexpect
from time import sleep

import time
import colorsys
from textwrap import wrap
import re
from datetime import timedelta
'''
import sys
import json
from datetime import datetime

from kettle.kettleclass import RedmondKettler
from kettle.logclass import log

import timeit

start = timeit.default_timer()


''' Конфигурация чайника '''
mac = "cc:6a:a9:e7:13:10"
key = "b54c75b1b40c88ef"


''' '''

kettler = None # global object
log.maxlevel = 10;
#log = logclass()

def Setup_Kettler():
    global kettler
    
    if len(key) != 16:
        log.warning("Bluetooth KEY value is empty or wrong")
        return False

    kettler = RedmondKettler( mac, key)

    #try:
    log.info ("Strating first connect")
    kettler.firstConnect()
    
    if kettler.ready != True:
        kettler = None
   
    return kettler
    #except:
    log.error("Connect to Kettle %s failed" % (mac))
    log.debug("Unexpected error info:" + str(sys.exc_info()[0]))
    return False

def Make_status_JSON(kettler, mainMethodAnswer):
    #global kettler   
    
    kettler.sendGetStatus()
    kettler.sendGetStat()

    
    data = {}
    data['mode'] = kettler.mode
    data['targettemp'] = kettler.tgtemp
    data['temp'] = kettler.temp
    data['status'] = kettler.status
    data['durat'] = kettler.durat
   
    data['watts'] = kettler.Watts
    data['alltime'] = kettler.Alltime
    data['times'] = kettler.Times
    data['now'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data['answer'] = mainMethodAnswer

    stop = timeit.default_timer()
    data['runtime'] = round(stop - start,2) 

    json_data = json.dumps(data)
    
    return json_data