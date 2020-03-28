#!/usr/bin/python
# coding: utf-8
'''
import pexpect
from time import sleep
import sys
import time
import colorsys
from datetime import datetime
from textwrap import wrap
import re
from datetime import timedelta
'''
from kettle.kettleclass import RedmondKettler
from kettle.logclass import logclass
from kettle.logclass import log
import json
''' Конфигурация чайника '''
mac = "cc:6a:a9:e7:13:10"
key = "b54c75b1b40c88ef"


''' '''

kettler = None # global object

#log = logclass(0)
log.maxlevel = 0;

def Setup_Kettler():
    global kettler
    
    if len(key) != 16:
        log.warning("Bluetooth KEY value is empty or wrong")
        return False

    kettler = RedmondKettler( mac, key)

    #try:
    log.info ("Strating first connect1")
    kettler.firstConnect()
    return kettler.ready
    #except:
    log.error("Connect to Kettle %s failed" % (mac))
    log.debug("Unexpected error info:" + str(sys.exc_info()[0]))
    return False


ready = Setup_Kettler()
if ready:
    log.info("Kettle setup was successfully completed, can proceed with commands further")
    #kettler.sendStart()
    kettler.sendGetStatus()
    kettler.sendGetStat()
    #print("Status aquired [mode = %s, targettemp = %s, temp = %s, status = %s (00 off, 02 on), durat = 0x%s]"%(kettler._mode, kettler._tgtemp, kettler._temp, kettler._status, kettler.durat))
    #print("Statistics aquired [watts = %s, alltime = %s, times = %s]"%(kettler._Watts, kettler._alltime, kettler._times))
    
    data = {}
    data['mode'] = kettler._mode
    data['targettemp'] = kettler._tgtemp
    data['temp'] = kettler._temp
    data['status'] = kettler._status
    data['durat'] = kettler.durat
   
    data['watts'] = kettler._Watts
    data['alltime'] = kettler._alltime
    data['times'] = kettler._times

    json_data = json.dumps(data)
    print (json_data)
    
kettler.disconnect()
