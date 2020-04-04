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
from kettle.kettleclass import RedmondKettler
from kettle.logclass import logclass
from kettle.logclass import log
import sys
import json
from datetime import datetime
import timeit

start = timeit.default_timer()

''' Конфигурация чайника '''
mac = "cc:6a:a9:e7:13:10"
key = "b54c75b1b40c88ef"


''' '''

kettler = None # global object

#log = logclass()
log.maxlevel = 5;

def Setup_Kettler():
    global kettler
    
    if len(key) != 16:
        log.warning("Bluetooth KEY value is empty or wrong")
        return False

    kettler = RedmondKettler( mac, key)

    #try:
    log.info ("Strating first connect")
    kettler.firstConnect()
    return kettler.ready
    #except:
    log.error("Connect to Kettle %s failed" % (mac))
    log.debug("Unexpected error info:" + str(sys.exc_info()[0]))
    return False


if __name__ == "__main__":
    log.debug(f"Arguments count: {len(sys.argv)}")
    for i, arg in enumerate(sys.argv):
        log.debug(f"Argument {i:>6}: {arg}")
    
    # kettle_mode_heat mode target_temp duration_correction
    try:
        mode = str(sys.argv[1])
        mode=mode if len(str(mode))==2 else "0"+str(mode)
    except:
        mode = "02"
    
    try:
        target_temp = int(sys.argv[2])
        if mode == "01" or  mode == "02":
            target_temp = min(target_temp, 90) #max allowed 90 in mode 1 & 2
    except:
        target_temp = 100

    try:
        dutation_correction = int(sys.argv[3])
    except:
        dutation_correction = 0
       
   

ready = Setup_Kettler()
if ready:
    log.info("Kettle setup was successfully completed, can proceed with commands further")
    #kettler.sendStart()
    
    log.info ("Setting kettle parameters: MODE=%s, TARGET_TEMP=%s, DURATION_CORRECTION=%s"%(mode,target_temp,dutation_correction))
    if kettler.sendSetMode(mode, target_temp, dutation_correction):
        log.info ("Successfully set")
    else:
        log.error ("Error setting kettle parameters")

    kettler.sendGetStatus()
    kettler.sendGetStat()

    data = {}
    data['mode'] = kettler._mode
    data['targettemp'] = kettler._tgtemp
    data['temp'] = kettler._temp
    data['status'] = kettler._status
    data['durat'] = kettler.durat
   
    data['watts'] = kettler._Watts
    data['alltime'] = kettler._alltime
    data['times'] = kettler._times
    data['now'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    stop = timeit.default_timer()
    data['runtime'] = round(stop - start,2) 

    json_data = json.dumps(data)
    print (json_data)
    
kettler.disconnect()
