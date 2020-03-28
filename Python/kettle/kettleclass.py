#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  kettleclass2.py
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
import pexpect
from time import sleep
import sys
import time
import colorsys
from datetime import datetime
from textwrap import wrap
import re
from datetime import timedelta

from kettle.logclass import log

CONF_MIN_TEMP = 40
CONF_MAX_TEMP = 100
CONF_TARGET_TEMP = 100

CONF_MAX_CONNECT_ATTEMPTS = 3
CONF_MAX_AUTH_ATTEMPTS = 5

'''
class

'''
class RedmondKettler:

    def __init__(self, addr, key):
        self._mac = addr
        self._key = key
        self._iter = 0
        self._connected = False
        self._auth = False
        self._is_busy = False
        self.child = None
        self.ready = False
        self.usebacklight = True
        
        self._mntemp = CONF_MIN_TEMP
        self._mxtemp = CONF_MAX_TEMP
        self._tgtemp = CONF_TARGET_TEMP
        
        #status and stats
        self._temp = 0
        self._Watts = 0
        self._alltime = 0
        self._times = 0
        self._time_upd = '00:00'
        self._boiltime = '80'
        self._rgb1 = '0000ff'
        self._rgb2 = 'ff0000'
        self._rand = '5e'
        self._mode = '00' # '00' - boil, '01' - heat to temp, '03' - backlight
        self._status = '00' #may be '00' - OFF or '02' - ON
        self._hold = False
        self.durat = '0'

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

    def theLightIsOn(self):
        if self._status == '02' and self._mode == '03':
            return True
        return False

    def theKettlerIsOn(self):
        if self._status == '02':
            if self._mode == '00' or self._mode == '01':
                return True
        return False

    def iterase(self): # counter
        self._iter+=1
        if self._iter >= 100: self._iter = 0

    def hexToDec(self, chr):
        return int(str(chr), 16)

    def decToHex(self, num):
        char = str(hex(int(num))[2:])
        if len(char) < 2:
            char = '0' + char
        return char



    def sendStart(self):
        answ = False
        log.info("Switching on kettle...")
        try:
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self._iter) + "03aa") # ON
            self.child.expect("value: ")
            self.child.expect("\r\n")
            log.debug ( str(self.child.before) + " [should be 55 06 03 >01< aa]")
            self.child.expect(r'\[LE\]>')
            self.iterase()
            answ = True
            log.info ("Kettle switched on successfully")
        except:
            answ = False
            log.error('error starting mode ON')
            log.debug("Unexpected error info:" +str(sys.exc_info()[0]))
        return answ

    def sendStop(self):
        answ = False
        log.info("Switching off kettle...")
        try:
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self._iter) + "04aa") # OFF
            self.child.expect("value: ")
            self.child.expect("\r\n")
            log.debug ( str(self.child.before) + " [should be 55 06 04 >01< aa]")
            self.child.expect(r'\[LE\]>')
            self.iterase()
            answ = True
            log.info ("Kettle switched off successfully")
        except:
            answ = False
            log.error('error starting mode OFF')
            log.debug("Unexpected error info:" +str(sys.exc_info()[0]))
        return answ
    
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
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self._iter) + "6e" + timeNow_str + tmz_str + "0000aa")
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
    
    def sendUseBackLight(self, use = True):
        answ = False
        log.info("Sending Use backlight command...")
        onoff="00"
        if use:
            onoff="01"
        try:
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self._iter) + "37c8c8" + onoff + "aa") #  onoff: 00 - off, 01 - on
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
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self._iter) + "32" + boilOrLight + scale_light[0] + self._rand + rgb1 + scale_light[1] + self._rand + rgb_mid + scale_light[2] + self._rand + rgb2 + "aa")
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
    
    def sendGetStat(self):
        answ = False
        log.info("Starting quering statistics...")
        try:
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self._iter) + "4700aa")
            self.child.expect("value: ")
            self.child.expect("\r\n")
            statusStr = self.child.before[0:].decode("utf-8")
            log.debug ( statusStr )
            self._Watts = self.hexToDec(str(statusStr.split()[11] + statusStr.split()[10] + statusStr.split()[9])) # in Watts
            self._alltime = round(self._Watts/2200, 1) # in hours
            self.child.expect(r'\[LE\]>')
            self.iterase()
            
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self._iter) + "5000aa")
            self.child.expect("value: ")
            self.child.expect("\r\n")
            statusStr = self.child.before[0:].decode("utf-8")
            self._times = self.hexToDec(str(statusStr.split()[7] + statusStr.split()[6]))
            self.child.expect(r'\[LE\]>')
            self.iterase()
            log.info("Statistics aquired [watts = %s, alltime = %s, times = %s]"%(self._Watts, self._alltime, self._times))
            answ = True
        except:
            answ = False
            log.error('error geting statistics')
            log.debug("Unexpected error info:" +str(sys.exc_info()[0]))
            
        return answ
    
    
    def sendGetStatus(self):
        answ = False
        log.info("Starting getting current status...")
        try:
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self._iter) + "06aa") # status of device
            self.child.expect("value: ")
            self.child.expect("\r\n")
            statusStr = self.child.before[0:].decode("utf-8") # answer from device example 55 xx 06 00 00 00 00 01 2a 1e 00 00 00 00 00 00 80 00 00 aa
            log.debug ( statusStr )
            answer = statusStr.split()
            self._status = str(answer[11])
            self._temp = self.hexToDec(str(answer[8]))
            self._mode = str(answer[3])
            tgtemp = str(answer[5])
            if tgtemp != '00':
                self._tgtemp = self.hexToDec(tgtemp)
            else:
                self._tgtemp = 100
            self.durat= str(answer[16])
            self.child.expect(r'\[LE\]>')
            self.iterase()
            log.info("Status aquired [mode = %s, targettemp = %s, temp = %s, status = %s (00 off, 02 on), durat = 0x%s]"%(self._mode, self._tgtemp, self._temp, self._status, self.durat))
            answ = True
        except:
            answ = False
            log.error('error get status')
            log.debug("Unexpected error info:" +str(sys.exc_info()[0]))
           
        return answ
    
### connect methods
    
    def connect(self):
        answer = False
        if self._is_busy:
            log.info("Busy")
            self.disconnect()
        try:
            log.info("Trying to connect to kettle [%s]..."%(self._mac))
            self._is_busy = True
            self.child = pexpect.spawn("gatttool -I -t random -b " + self._mac, ignore_sighup=False)
            self.child.expect(r'\[LE\]>', timeout=1)
            self.child.sendline("connect")
            self.child.expect(r'Connection successful.*\[LE\]>', timeout=1)
            log.debug ( self.child.after )
            self._is_busy = False
            answer = True
            self._connected = True;
            log.info("Connected")
        except:
            log.error('Error during connection attempt')
            log.debug("Unexpected error info:" +str(sys.exc_info()[0]))
            self._connected = False;
        return answer

    def disconnect(self):
        log.info ("Disconnecting...")
        self._is_busy = True
        if self.child != None:
            self.child.sendline("exit")
        self.child = None
        self._is_busy = False
        self._connected = False
        self._auth = False
        self.ready = False
            
    def reset(self):
        log.info ("Resetting...")
        self._is_busy = True
        if self.child != None:
            self.child.sendline("exit")
        self._connected = False
        self._auth = False
        self.ready = False        
        self._tgtemp = CONF_TARGET_TEMP
        self._temp = 0
        self._Watts = 0
        self._alltime = 0
        self._times = 0
        self._time_upd = '00:00'
        self._boiltime = '80'
        self._rgb1 = '0000ff'
        self._rgb2 = 'ff0000'
        self._rand = '5e'
        self._iter = 0
        self._mode = '00'
        self._status = '00'
        self.usebacklight = True
        self._hold = False
        self.child = None
        self._is_busy = False

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
            self.child.sendline("char-write-req 0x000e 55" + self.decToHex(self._iter) + "ff" + self._key + "aa") #send authorise key
            self.child.expect("value: ") # wait for response
            self.child.expect("\r\n") # wait for end string
            log.debug(self.child.before) #for debug
            connectedStr = self.child.before[0:].decode("utf-8") # answer from device
            answ = connectedStr.split()[3] # parse: 00 - no   01 - yes
            self.child.expect(r'\[LE\]>')
            if answ == '01':
                answer = True
                self._auth = True
                log.info('Successfully authenticated')
            else:
                log.info('Could not authenticate')
                self._auth = False
            self.iterase()
        except:
            answer = False
            log.error('Authentication error')
        return answer
    
    def sendInitialSettings(self):
        if self.sendUseBackLight(self.usebacklight):
            if self.sendSetLightsColor():
                if self.sendSync():
                    self._time_upd = time.strftime("%H:%M")
                

        
    def firstConnect(self):
        self._is_busy = True #will eventually force disconnet
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
        
        if self._auth:
            self.ready = True
            self.sendInitialSettings()
            
            
        else:
            log.error('Error during first connect: not authenticated')
            self.reset()
            
        return self._auth

'''
end of class definition
'''


def main(args):
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
