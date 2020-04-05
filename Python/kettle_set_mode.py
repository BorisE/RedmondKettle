#!/usr/bin/python
# coding: utf-8

#from kettle.kettleclass import RedmondKettler
#from kettle.logclass import logclass
from kettle.logclass import log
import sys



#Use main wrapper library
from kettle_wrappers_lib import *

#Private part

if __name__ == "__main__":
    log.debug(f"Arguments count: {len(sys.argv)}")
    for i, arg in enumerate(sys.argv):
        log.debug(f"Argument {i:>6}: {arg}")
    
    # kettle_mode_heat mode target_temp duration_correction
    try:
        mode = str(sys.argv[1])
        mode=mode if len(str(mode))==2 else "0"+str(mode)
    except:
        mode = "00"
    
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
       
   
#Init Kettler Object
kettler = Setup_Kettler()

if kettler:
    log.info("Kettle setup was successfully completed, can proceed with commands further")
    #kettler.sendStart()
    
    log.info ("Setting kettle parameters: MODE=%s, TARGET_TEMP=%s, DURATION_CORRECTION=%s"%(mode,target_temp,dutation_correction))
    mainMethodAnswer = False
    if kettler.sendSetMode(mode, target_temp, dutation_correction):
        log.info ("Successfully set")
        mainMethodAnswer = True
    else:
        log.error ("Error setting kettle parameters")
        mainMethodAnswer = False

    json_data = Make_status_JSON (kettler, mainMethodAnswer)

    print (json_data)
    
    kettler.disconnect()
