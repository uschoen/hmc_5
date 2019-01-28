'''
Created on 01.12.2018

@author: uschoen
'''

__version__='5.1'
__author__ = 'ullrich schoen'
DEVICENTYPE="defaultDevice"
DEVICEPACKAGE="hmc.devices"

# Standard library imports
import logging
import os
import json
import sys

# Local application imports
from gateways.hmc.devices.deviceChannel import deviceChannel
from gateways.hmc.devices.deviceParameter import deviceParameter
from gateways.hmc.devices.deviceEvents import deviceEvents
from .deviceException import deviceException,deviceConfigurationException

LOG=logging.getLogger(__name__)

class masterDevice(deviceChannel,
                   deviceParameter,
                   deviceEvents,
                   object):

    def __init__ (self,deviceID,core,deviceCFG={},restore=False):
        '''
        core 
        '''
        self.core=core 
        self.deviceID=deviceID
        
        self.path='' if not os.path.dirname(sys.argv[0]) else '%s/'%(os.path.dirname(sys.argv[0]))
        
        deviceEvents.__init__(self)
        deviceParameter.__init__(self)
        deviceChannel.__init__(self)
        
        
        if restore:           
            self.__restoreDevice(deviceCFG)
        else:
            self.updateDeviceParameter(deviceCFG['device'])
            self.loadDefaultChannels()
            self.eventAction("oncreate",'device')

        LOG.info("init masterDevice deviceID:%s version:%s"%(self.deviceID,__version__))
        
            
    
    def __restoreDevice(self,deviceCFG):
        '''
        restore a device
        '''
        try:
            LOG.debug("restore deviceID %s"%(self.deviceID))
            self.updateDeviceParameter(deviceCFG.get('device',{}))
            self.loadDefaultChannels()
            deviceChannelConfig=deviceCFG.get('channels',{})
            for channelName in deviceChannelConfig:
                LOG.debug("restore channel %s for deviceID %s"%(channelName,self.deviceID))
                self._addChannel(channelName,deviceChannelConfig[channelName])
        except:
            raise deviceConfigurationException("can't restore deviceID %s"%(self.deviceID))
    
       
    def getConfiguration(self):
        '''
        get the device confikuration back
        '''
        try:
            device={
              'device':self.device,
              'channels':self.channels
              }  
            return device
        except:
            raise deviceException("can't get configuration")
    
    def _writeJSON(self,filename,data={}):
        LOG.info("write configuration to %s"%(filename))
        try:
            with open(os.path.normpath(filename),'w') as outfile:
                json.dump(data, outfile,sort_keys=True, indent=4)
                outfile.close()
        except IOError:
            raise deviceConfigurationException("can't write file: %s "%(os.path.normpath(filename)))
        except ValueError:
            raise deviceConfigurationException("error in file: %s "%(os.path.normpath(filename)))
        except:
            raise deviceConfigurationException("unknown error:")
                      
    def _loadJSON(self,filename):
        '''
        loading configuration file
        '''
        try:
            with open(os.path.normpath(filename)) as jsonDataFile:
                dateFile = json.load(jsonDataFile)
            return dateFile 
        except IOError:
            raise deviceConfigurationException("can't find file: %s "%(os.path.normpath(filename)))
        except ValueError:
            raise deviceConfigurationException("error in file: %s "%(os.path.normpath(filename)))
        except:
            raise deviceConfigurationException("unknown error:")    