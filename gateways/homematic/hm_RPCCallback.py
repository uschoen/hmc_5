'''
Created on 01.12.2018

@author: uschoen
'''


__version__='5.1'
__author__ = 'ullrich schoen'

# Standard library imports
import logging
import re
# Local application imports
from core.hmcException import gatewayException

LOG=logging.getLogger(__name__)
'''
debug modus for test
write files into LOG to see the HM DATA
'''
DEBUG=False

class hmcRPCcallback:
    '''
    call back function from the RPC Server
    to handle request
    '''
    def __init__(self,cfg,core,resetTimer):
        ''' core instance '''
        self.core=core
        ''' configuration parameter  '''
        self.config={
                        "name":"unknown"                       
                      }
        self.config.update(cfg)
        ''' name '''
        self.name=self.config['name']
        
        ''' reset timer function '''
        self.__resetTimer=resetTimer

        LOG.debug("init new hmcRPCcallback version %s"%(__version__))
        
    def event(self,interfaceID,deviceNumber,channelName,value,*unkown):
        if DEBUG:
            filer = open("log/channels%s.txt"%(self.name),'a') 
            filer.write('%s %s %s %s\n'%(deviceNumber,channelName,value,unkown))
            filer.close() 
        try:
            deviceID=""
            channelNumber=1
            self.__resetTimer()
            if re.match('.*:.*',deviceNumber):
                (deviceID,channelNumber)=deviceNumber.split(":")
            else:
                return ''
            deviceID=("%s@%s"%(deviceID,self.config.get('gateway')))  
            channelName=channelName.lower()
            channelName=("%s:%s")%(channelNumber,channelName)
            LOG.debug("event: deviceID: %s, channel name = %s, value = %s" % (deviceID,channelName,value))
            if not self.core.ifDeviceIDExists(deviceID):
                LOG.error("deviceID %s is not exists"%(deviceID))
                LOG.error("get deviceNumber:%s channelName:%s value:%s unkown:%s"%(deviceNumber,channelName,value,unkown))
                return''
            if not self.core.ifDeviceChannelExist(deviceID,channelName):
                channelCFG={
                     'name':channelName,
                     'value':0
                    }
                self.core.addDeviceChannel(deviceID,channelName,channelCFG)
            self.core.setDeviceChannelValue(deviceID,channelName,value)
            return ''
        except:
            LOG.error("error to add channel %s for deviceID %s "%(channelName,deviceID), exc_info=True)
            return ''
    
    def newDevices(self, interfaceID,allDevices):
        try:
            LOG.debug("call newDevices for interfaceID:%s"%(interfaceID))
            ''' 
            Debug modus for tests
            '''
            if DEBUG:
                filer = open("log/devices%s.txt"%(self.name),'a')
            for device in allDevices:
                self.__resetTimer()
                ''' 
                Debug modus for tests
                '''
                if DEBUG:
                    filer.write('%s\n'%(device))
                if device['PARENT']=="":
                    deviceID="%s@%s"%(device['ADDRESS'],self.config.get('gateway'))
                    try:
                        if not self.core.ifDeviceIDExists(deviceID):
                            self.__addNewDevice(device)
                        else:
                            LOG.info("deviceID is exist: %s"%(deviceID))
                    except:
                        LOG.warning("can not add deviceID: %s"%(deviceID), exc_info=True) 
                ''' 
                Debug modus for tests
                '''
                if DEBUG:
                    filer.close() 
            return ''
            
        except:
            raise gatewayException("some error in new devices at %"%(self.name))     
            return ''
        
    def listMethods(self,*args):
        self.__resetTimer()
        LOG.error("call listMethods for interfaceID %s"%(args))
        return ''
    
    def listDevices(self,*args):
        self.__resetTimer()
        LOG.error("call listDevices for interfaceID %s"%(args))
        return ''
    
    def __addNewDevice(self,device):
        '''
        add a new sensor to core devices
        '''
        try:
            deviceID="%s@%s"%(device['ADDRESS'],self.config['gateway'])
            LOG.info("add  new devicesID:%s"%(deviceID))
            devicetype=device['TYPE'].replace("-","_")
            deviceCFG={
                    "gateway":"%s"%(self.config['gateway']),
                    "deviceID":"%s"%(deviceID),
                    "enable":True,
                    "deviceType":"%s"%(devicetype),
                    "devicePackage":self.config['devicePackage'],
                    }
            self.core.addDevice(deviceID,deviceCFG)
        except:
            LOG.error("can not add deviceID: %s"%(deviceID))
            raise gatewayException("can't add device %s"%(deviceID))  