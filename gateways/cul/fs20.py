'''
Created on 23.12.2017

@author: uschoen
'''
__verion__=5.1

# Standard library imports
import logging

# Local application imports
from core.hmcException import gatewayException

LOG=logging.getLogger(__name__)

NAMEDEVICE="value"
NAMEDEVICERSSI="rssi"

class fs20device(object):
    '''
    classdocs
    
    '''
    def __init__(self):
        LOG.debug("cul fs20 devices init")
        
    def decodeFS20(self,msg):
        try:
            LOG.debug("fs20 get code %s"%(msg))
            FS20ID="%s"%(msg[0:6])
            deviceID="%s@%s"%(msg[0:6],self.config['gateway'])
            rssi=self.calcRssi(int(msg[8:9],16))
            value=str(msg[6:8])
            LOG.debug("fs20 deviceID is %s"%(deviceID))
            
            if not self.core.ifDeviceIDExists(deviceID):
                '''
                add device
                '''
                deviceCFG={
                    'deviceID':deviceID,
                    'name':FS20ID,
                    'deviceType':"fs20_generic",
                    'devicePackage':"cul",
                    }
                self.core.addDevice(deviceID,deviceCFG)
            if not self.core.ifDeviceChannelExist(deviceID,NAMEDEVICE):
                ''' 
                add channel device
                '''
                channelCFG={
                    'name':FS20ID,
                    'fs20ID':FS20ID
                    }
                self.core.addDeviceChannel(deviceID,NAMEDEVICE,channelCFG)
            self.core.setDeviceChannelValue(deviceID,NAMEDEVICE,value)
            
            if not self.core.ifDeviceChannelExist(deviceID,NAMEDEVICERSSI):
                '''
                add channel RSSI
                '''
                channelCFG={
                    'name':"RSSI"
                    }
                self.core.addDeviceChannel(deviceID,NAMEDEVICERSSI,channelCFG) 
            self.core.setDeviceChannelValue(deviceID,NAMEDEVICERSSI,rssi)
        except :
            raise gatewayException("can not add or update fs20 device",False)

        