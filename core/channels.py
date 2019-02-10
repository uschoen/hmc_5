'''
Created on 01.12.2018

@author: uschoen
'''


__version__='5.1'
__author__ = 'ullrich schoen'

# Standard library imports
import copy
import logging
# Local apllication constant
from .hmcException import coreChannelException,coreDeviceException
from gateways.hmc.devices.deviceException import deviceChannelException

LOG=logging.getLogger(__name__)

class channels():
    '''
    core events function
    '''
    def __init__(self,*args):
        '''
        core channels
        '''
        LOG.info("load core.channels modul")
    
    def setDeviceChannelValue(self,deviceID,channelName,value,forceUpdate=False):
        '''
        set the value of a channel from a device
        '''
        try:
            channelName=str(channelName)
            channelName=channelName.lower()
            if not self.ifDeviceIDExists(deviceID):
                raise coreDeviceException("deviceID %s not exist"%(deviceID))
            self.devices[deviceID].setChannelValue(channelName,value)
            self.updateRemoteCore(forceUpdate,deviceID,'setDeviceChannelValue',deviceID,channelName,value)
        except coreDeviceException as e:
            raise e
        except:
            raise coreChannelException("can not change channel %s for deviceID %s to value %s"%(channelName,deviceID,value))
    
    def ifDeviceChannelExist(self,deviceID,channelName):
        '''
        check if channel in device ID exists
        '''
        try:
            if not self.ifDeviceIDExists(deviceID):
                raise coreDeviceException("deviceID %s not exist"%(deviceID))
            return self.devices[deviceID].ifDeviceChannelExist(channelName)  
        except coreDeviceException as e:
            raise e
        except:
            raise coreChannelException("unkown error in deviceID %s"%(deviceID))
    
    def getAllDeviceChannelAttribute(self,deviceID,channelName):
        try:
            if not deviceID in self.devices:
                raise coreDeviceException("deviceID %s not existing"%(deviceID))
            channelName=str(channelName)
            channelName=channelName.lower()
            return self.devices[deviceID].getAllChannelAttribute(channelName)
        except coreDeviceException as e:
            raise e
        except:
            raise coreChannelException("can not getDeviceChannelAttribute for channel:%s for deviceID:%s"%(channelName,deviceID))  
    
    def getDeviceChannelAttributValue(self,deviceID,channelName,attribut):
        try:
            if not deviceID in self.devices:
                raise coreDeviceException("deviceID %s not existing"%(deviceID))
            return self.devices[deviceID].getAllChannelAttributeValue(channelName,attribut)
        except coreDeviceException as e:
            raise e
        except:
            raise coreChannelException("can not getDeviceChannelAttributValue %s:%s for deviceID %s"%(channelName,attribut,deviceID))  
        
    def getDeviceChannelValue(self,deviceID,channelName):
        try:
            if not deviceID in self.devices:
                raise coreDeviceException("deviceID %s not existing"%(deviceID))
            channelName=str(channelName)
            channelName=channelName.lower()
            return self.devices[deviceID].getChannelValue(channelName)
        except coreDeviceException as e:
            raise e
        except:
            raise coreChannelException("can not getDeviceChannelValue %s for deviceID %s"%(channelName,deviceID))  
          
    def addDeviceChannel(self,deviceID,channelName,channelCFG={},forceUpdate=False):
        '''
        add a new device Channel
        
        channelName= channel name
        channelfCFG= channel parameter
        '''
        try:
            if not deviceID in self.devices:
                raise coreDeviceException("deviceID %s not existing"%(deviceID))
            channelName=str(channelName)
            channelName=channelName.lower()
            channelValuesCP=copy.deepcopy(channelCFG)
            self.devices[deviceID].addChannel(channelName,channelValuesCP)
            self.updateRemoteCore(forceUpdate,deviceID,'addDeviceChannel',deviceID,channelName,channelValuesCP)
        except (coreDeviceException,deviceChannelException) as e:
            raise e
        except:
            raise coreChannelException("can not add channel %s for deviceID %s values %s"%(channelName,deviceID,channelCFG))
    