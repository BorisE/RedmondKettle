#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  kettleclass.py
#
# Based on https://m.habr.com/ru/post/371965/abs
# and https://habr.com/ru/post/412583/
#
# Using code from https://github.com/mavrikkk/ha_kettler
#
#  Copyright 2020  <pi@raspberrypi>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#
'''
ToDo:
- include or smth similar of identical code in kettle_<wrappers>.py
- checking Kettle answer in all methods
- return kettle answer in json
'''

'''
Version history:
1.1  [2020-04-05]
 - code restructering for wrappers (wrapper lib)
 - check and return answer from wrappers
 - minor code improvements
1.08 [2020-04-04]
 - new method SetWorkingParameters
 - new wrapper for it kettle_set_mode.py
 - code improvements due to further Python learning ;)
 - check if kettle return succces in SetWorkingParameters
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

if __name__ == '__main__':
    from logclass import log
else:
    from kettle.logclass import log
    
CONF_MIN_TEMP = 40
CONF_MAX_TEMP = 100
CONF_TARGET_TEMP = 100

CONF_KETTLE_POWER = 2200

CONF_MAX_CONNECT_ATTEMPTS = 10
CONF_MAX_AUTH_ATTEMPTS = 10

'''
class

'''
class RedmondKettler:

    def __init__(self, addr, key):
        self.__mac = addr
        self.__key = key
        self.__iter = 0
        self.connected = False
        self.auth = False
        self.__is_busy = False
        self.child = None
        self.ready = False
        self.usebacklight = True
        
        self._mntemp = CONF_MIN_TEMP
        self._mxtemp = CONF_MAX_TEMP
        
        self.tgtemp = CONF_TARGET_TEMP
        
        #status and stats
        self.temp = 0
        self.Watts = 0
        self.Alltime = 0
        self.Times = 0
        self.__time_upd = '00:00'
        self._boiltime = '80'
        self._rgb1 = '0000ff'
        self._rgb2 = 'ff0000'
        self.__rand = '5e'
        self.mode = '00' # '00' - boil, '01' - keep temp,  '02' - boil and keep temp (combo mode), '03' - backlight
        self.status = '00' #may be '00' - OFF or '02' - ON
        self.durat = '0'
    
    # Color functions
    # - check if they working at all
    def calcMidColor(self, rgb1, rgb2):
        try:
            hs1 = self.rgbhex_to_hs(rgb1)
            hs2 = self.rgbhex_to_hs(rgb2)
            hmid = int((hs1[0]+hs2[0])/2)
            smid = int((hs1[1]+hs2[1])/2)
            hsmid = (hmid,smid)
            rgbmid = self.hs_to_rgbhex(hsmid)
        except:
            rgbmid = '00ff00'
        return rgbmid

    def rgbhex_to_hs(self, rgbhex):
        rgb = color_util.rgb_hex_to_rgb_list(rgbhex)
        return color_util.color_RGB_to_hs(*rgb)

    def hs_to_rgbhex(self, hs):
        rgb = color_util.color_hs_to_RGB(*hs)
        return color_util.color_rgb_to_hex(*rgb)

    # Status functions
    def theLightIsOn(self):
        if self.status == '02' and self.mode == '03':
            return True
        return False

    def theKettlerIsOn(self):
        if self.status == '02':
            if self.mode == '00' or self.mode == '01' or self.mode == '02':
                return True
        return False
    
    # Aux functions
    def iterase(self): # counter
        self.__iter+=1
        if self.__iter >= 100: self.__iter = 0

    def hexToDec(self, chr):
        return int(str(chr), 16)

    def decToHex(self, num):
        char = str(hex(int(num))[2:])
        if len(char) < 2:
            char = '0' + char
        return char

    ########################################
    # Kettle Commands
    ########################################
    # Send ON command
    def sendStart(self):
        answ = False
        log.info("Switching on kettle...")
        try:
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self.__iter) + "03aa") # ON
            self.child.expect("value: ")
            self.child.expect("\r\n")
            log.debug ( str(self.child.before) + " [should be 55 06 03 >01< aa]")
            answer = self.child.before.split()
            log.debug("Ok:" + str(answer[3] == b"01") )
            self.child.expect(r'\[LE\]>')
            self.iterase()
            answ = answer[3] == b"01"
            #if log.info ("Kettle switched on successfully")
        except:
            answ = False
            log.error('error starting mode ON')
            log.debug("Unexpected error info:" +str(sys.exc_info()[0]))
        return answ

    # Send OFF command
    def sendStop(self):
        answ = False
        log.info("Switching off kettle...")
        try:
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self.__iter) + "04aa") # OFF
            self.child.expect("value: ")
            self.child.expect("\r\n")
            log.debug ( str(self.child.before) + " [should be 55 06 04 >01< aa]")
            answer = self.child.before.split()
            log.debug("Ok:" + str(answer[3] == b"01") )
            self.child.expect(r'\[LE\]>')
            self.iterase()
            answ = answer[3] == b"01"
            #log.info ("Kettle switched off successfully")
        except:
            answ = False
            log.error('error starting mode OFF')
            log.debug("Unexpected error info:" +str(sys.exc_info()[0]))
        return answ
    
    # Send SYNC data (current time data)
    def sendSync(self, timezone = 3):
        answ = False
        log.info("Syncing kettle...")
        try:
            tmz_hex_list = wrap(str(self.decToHex(timezone*60*60)), 2)
            tmz_str = ''
            for i in reversed(tmz_hex_list):
                tmz_str+=i
            timeNow_list = wrap(str(self.decToHex(time.mktime(datetime.now().timetuple()))), 2)
            timeNow_str = ''
            for i in reversed(timeNow_list):
                timeNow_str+=i
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self.__iter) + "6e" + timeNow_str + tmz_str + "0000aa")
            self.child.expect("value: ")
            self.child.expect("\r\n")
            log.debug ( str(self.child.before)  + " [should be 55 02 6e 00 aa]")            
            self.child.expect(r'\[LE\]>')
            self.iterase()
            log.info("Syncing kettle complete")
            answ = True
        except:
            answ = False
            log.error('error sync time')
            log.debug("Unexpected error info:" +str(sys.exc_info()[0]))
        return answ
    
    # Send Use BackLight command
    def sendUseBackLight(self, use = True):
        answ = False
        log.info("Sending Use backlight command...")
        onoff="00"
        if use:
            onoff="01"
        try:
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self.__iter) + "37c8c8" + onoff + "aa") #  onoff: 00 - off, 01 - on
            self.child.expect("value: ")
            self.child.expect("\r\n")
            log.debug ( str(self.child.before)  + " [should be 55 08 32 00 aa]")
            self.child.expect(r'\[LE\]>')
            self.iterase()
            log.info("Use backlight command is complete")
            answ = True
        except:
            answ = False
            log.error('error set use backlight')
            log.debug("Unexpected error info:" +str(sys.exc_info()[0]))
        return answ
    
    # Send Set Color Data command
    def sendSetLightsColor(self, boilOrLight = '00', rgb1 = '0000ff', rgb2 = 'ff0000'): # 00 - boil light    01 - backlight
        answ = False
        log.info("Sending set lights color command...")
        try:
            if rgb1 == '0000ff' and rgb2 == 'ff0000':
                rgb_mid = '00ff00'
            else:
                rgb_mid = self.calcMidColor(rgb1,rgb2)
            if boilOrLight == "00":
                scale_light = ['28', '46', '64']
            else:
                scale_light = ['00', '32', '64']
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self.__iter) + "32" + boilOrLight + scale_light[0] + self.__rand + rgb1 + scale_light[1] + self.__rand + rgb_mid + scale_light[2] + self.__rand + rgb2 + "aa")
            self.child.expect("value: ")
            self.child.expect("\r\n")
            log.debug ( str(self.child.before) + " [should be 55 09 32 00 aa]")
            self.child.expect(r'\[LE\]>')
            self.iterase()
            log.info("Set lights color command complete")
            answ = True
        except:
            answ = False
            log.error('error set colors of light')
            log.debug("Unexpected error info:" +str(sys.exc_info()[0]))
        return answ
    
    # Send Get Usage Statistics command
    def sendGetStat(self):
        answ = False
        log.info("Starting quering statistics...")
        try:
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self.__iter) + "4700aa")
            self.child.expect("value: ")
            self.child.expect("\r\n")
            statusStr = self.child.before[0:].decode("utf-8")
            log.debug ( statusStr )
            self.Watts = self.hexToDec(str(statusStr.split()[11] + statusStr.split()[10] + statusStr.split()[9])) # in Watts
            self.Alltime = round(self.Watts/CONF_KETTLE_POWER, 1) # in hours
            self.child.expect(r'\[LE\]>')
            self.iterase()
            
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self.__iter) + "5000aa")
            self.child.expect("value: ")
            self.child.expect("\r\n")
            statusStr = self.child.before[0:].decode("utf-8")
            self.Times = self.hexToDec(str(statusStr.split()[7] + statusStr.split()[6]))
            self.child.expect(r'\[LE\]>')
            self.iterase()
            log.info("Statistics aquired [watts = %s, alltime = %s, times = %s]"%(self.Watts, self.Alltime, self.Times))
            answ = True
        except:
            answ = False
            log.error('error geting statistics')
            log.debug("Unexpected error info:" +str(sys.exc_info()[0]))
            
        return answ
    
    # Send Get Current Status command
    def sendGetStatus(self):
        answ = False
        log.info("Starting getting current status...")
        try:
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self.__iter) + "06aa") # status of device
            self.child.expect("value: ")
            self.child.expect("\r\n")
            statusStr = self.child.before[0:].decode("utf-8") # answer from device example 55 xx 06 00 00 00 00 01 2a 1e 00 00 00 00 00 00 80 00 00 aa
            log.debug ( statusStr )
            answer = statusStr.split()
            self.status = str(answer[11])
            self.temp = self.hexToDec(str(answer[8]))
            self.mode = str(answer[3])
            tgtemp = str(answer[5])
            if tgtemp != '00':
                self.tgtemp = self.hexToDec(tgtemp)
            else:
                self.tgtemp = 100
            self.durat= str(answer[16])
            self.child.expect(r'\[LE\]>')
            self.iterase()
            log.info("Status aquired [mode = %s, targettemp = %s, temp = %s, status = %s (00 off, 02 on), durat = 0x%s]"%(self.mode, self.tgtemp, self.temp, self.status, self.durat))
            answ = True
        except:
            answ = False
            log.error('error get status')
            log.debug("Unexpected error info:" +str(sys.exc_info()[0]))
           
        return answ
    
    # Send Set Working Parameters command
    def sendSetMode(self, mode, target_temp, boilduration_correction):   # 00 - boil 01 - heat to temp 03 - backlight (boil by default)    temp - in DEC
        answ = False
        log.info("Starting set current mode and parameters...")
        try:
            modest=mode if len(str(mode))==2 else "0"+str(mode)
            #log.debug("Mode:" + modest)
            boildurationHex=self.decToHex(self.hexToDec("80")+int(boilduration_correction))
            #log.debug("Boil dur:" + boildurationHex)
            if modest == "01" or  modest == "02":
                target_temp = min(target_temp, 91) #max allowed 90 in mode 1 & 2
            sendline = "0x000e 55" + self.decToHex(self.__iter) + "05" + modest + "00" + self.decToHex(target_temp) + "00000000000000000000" + boildurationHex + "0000aa"
            log.debug("Sending command string: [" + sendline+ "]")
            self.child.sendline("char-write-req "+sendline) # set Properties
            self.child.expect("value: ")
            self.child.expect("\r\n")
            log.debug ( str(self.child.before) + " [should be 55 05 05 >01< aa]")
            answer = self.child.before.split()
            log.debug("Ok:" + str(answer[3] == b"01") )
            self.child.expect(r'\[LE\]>')
            self.iterase()
            answ = answer[3] == b"01"
        except Exception as e:
            answ = False
            log.error('Error seting mode')
            log.debug("Unexpected error info:" +str(sys.exc_info()[0])+"|"+str(sys.exc_info()[1]))
        return answ



    ########################################
    # Connect methods
    ########################################
    def connect(self):
        answer = False
        if self.__is_busy:
            log.info("Busy")
            self.disconnect()
        try:
            log.info("Trying to connect to kettle [%s]..."%(self.__mac))
            self.__is_busy = True
            self.child = pexpect.spawn("gatttool -I -t random -b " + self.__mac, ignore_sighup=False)
            self.child.expect(r'\[LE\]>', timeout=1)
            self.child.sendline("connect")
            self.child.expect(r'Connection successful.*\[LE\]>', timeout=1)
            log.debug ( self.child.after )
            self.__is_busy = False
            answer = True
            self.connected = True;
            log.info("Connected")
        except:
            log.error('Error during connection attempt')
            log.debug("Unexpected error info:" +str(sys.exc_info()[0])) #+str(sys.exc_info()[1])
            self.connected = False;
        return answer

    def disconnect(self):
        log.info ("Disconnecting...")
        self.__is_busy = True
        if self.child != None:
            self.child.sendline("exit")
        self.child = None
        self.__is_busy = False
        self.connected = False
        self.auth = False
        self.ready = False
            
    def reset(self):
        log.info ("Resetting...")
        self.__is_busy = True
        if self.child != None:
            self.child.sendline("exit")
        self.connected = False
        self.auth = False
        self.ready = False        
        self.tgtemp = CONF_TARGET_TEMP
        self.temp = 0
        self.Watts = 0
        self.Alltime = 0
        self.Times = 0
        self.__time_upd = '00:00'
        self._boiltime = '80'
        self._rgb1 = '0000ff'
        self._rgb2 = 'ff0000'
        self.__rand = '5e'
        self.__iter = 0
        self.mode = '00'
        self.status = '00'
        self.usebacklight = True
        self.child = None
        self.__is_busy = False

    def sendSubcribeToResponses(self):
        answ = False
        log.info('Trying to subcsribe to kettle notifications...')
        try:
            self.child.sendline("char-write-cmd 0x000c 0100") #send packet to receive messages in future
            self.child.expect(r'\[LE\]>')
            log.info('Successfully subscribed to notifications')
            answ = True
        except:
            answ = False
            log.error('Error during device subscription')
        return answ

    def sendAuth(self):
        answer = False
        log.info('Trying to authenticate to kettle...')
        try:
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self.__iter) + "ff" + self.__key + "aa") #send authorise key
            self.child.expect("value: ") # wait for response
            self.child.expect("\r\n") # wait for end string
            log.debug(self.child.before) #for debug
            connectedStr = self.child.before[0:].decode("utf-8") # answer from device
            answ = connectedStr.split()[3] # parse: 00 - no   01 - yes
            self.child.expect(r'\[LE\]>')
            if answ == '01':
                answer = True
                self.auth = True
                log.info('Successfully authenticated')
            else:
                log.info('Could not authenticate')
                self.auth = False
            self.iterase()
        except:
            answer = False
            log.error('Authentication error')
        return answer
    
    def sendInitialSettings(self):
        if self.sendUseBackLight(self.usebacklight):
            if self.sendSetLightsColor():
                if self.sendSync():
                    self.__time_upd = time.strftime("%H:%M")
                

        
    def firstConnect(self):
        self.__is_busy = True #will eventually force disconnet
        iter = 0
        itera =0
        try:
            while iter < CONF_MAX_CONNECT_ATTEMPTS:  # 10 attempts to connect
                log.info ("Connection attempt #%s"%(iter))
                if self.connect():
                    iter = 11 #to break
                    while itera < CONF_MAX_AUTH_ATTEMPTS:  # 10 attempts to auth
                        log.info ("Authentication attempt #%s"%(itera))
                        if self.sendSubcribeToResponses():
                            if self.sendAuth():
                                break
                        sleep(1)
                        itera+=1
                sleep(1)
                iter+=1
        except:
            log.error('Error during first connect')
            log.debug("Unexpected error info:" +str(sys.exc_info()[0]))
            self.reset()
        
        if self.auth:
            self.ready = True
            self.sendInitialSettings()
            
            
        else:
            log.error('Error during first connect: not authenticated')
            self.reset()
            
        return self.auth

'''
end of class definition
'''


def main(args):
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
