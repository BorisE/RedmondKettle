#!/usr/bin/python
# coding: utf-8

#from kettle.kettleclass import RedmondKettler
#from kettle.logclass import logclass
from kettle.logclass import log
import sys

#Use main wrapper library
from kettle_wrappers_lib import *

#Private part

#Init Kettler Object
kettler = Setup_Kettler()

if kettler:
    log.info("Kettle setup was successfully completed, can proceed with commands further")
    mainMethodAnswer = False
    
    if kettler.sendStop():
        log.info ("Kettle switched off successfully")
        mainMethodAnswer = True
    else:
        log.error ("Error switching kettle off")
        mainMethodAnswer = False


    json_data = Make_status_JSON (kettler, mainMethodAnswer)

    print (json_data)
    
    kettler.disconnect()
