#!/usr/bin/python
# coding: utf-8

#from kettle.kettleclass import RedmondKettler
#from kettle.logclass import logclass
from kettle.logclass import log

''' Конфигурация чайника '''
#mac = "cc:6a:a9:e7:13:10"
#key = "b54c75b1b40c88ef"

#Use main wrapper library
from kettle_wrappers_lib import *

#Private part

kettler = Setup_Kettler()

if kettler:
    log.info("Kettle setup was successfully completed, can proceed with commands further")
    json_data = Make_status_JSON (kettler, True)

    print (json_data)
    
    kettler.disconnect()
    
