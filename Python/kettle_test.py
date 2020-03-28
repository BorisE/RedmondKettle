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

''' Конфигурация чайника '''
mac = "cc:6a:a9:e7:13:10"
key = "b54c75b1b40c88ef"


''' '''

kettler = None # global object

log = logclass()

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


ready = Setup_Kettler()
if ready:
    print("Kettle setup was successfully completed, can proceed with commands further")
    #kettler.sendStart()
    kettler.sendGetStatus()
    kettler.sendGetStat()
    
kettler.disconnect()
