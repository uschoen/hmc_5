'''
Created on 01.12.2018

@author: uschoen
'''

__version__='5.1'
__author__ = 'ullrich schoen'

# Standard library imports
import copy
import logging
# Local application imports
from .deviceException import deviceChannelException

LOG=logging.getLogger(__name__)

class deviceChannel():

    def __init__ (self):
        '''
        channel={
                    'enable':True,
                    'name':channel name
                    'value': value of the channel
                    'events': events
                    }
        '''
        self.__defaultChannelParameter= lambda channelName:{
                                        'enable':True,
                                        'name':channelName,
                                        'value':"",
                                        'events':{}
        }
        try:
            self.__defaultChannelEvents=dict((events,self.getEventParameters(events)) for events in self.getEventsTyps())
        except:
            LOG.error("can't load default channel events use empty configuration")
            self.__defaultChannelEvents={}
            
        self.channels={}      
        LOG.info("init deviceChannels deviceID:%s version:%s"%(self.deviceID,__version__))
    
    def loadDefaultChannels(self):
        '''
        load chanel default , delte all old channels
        '''
        try:
            LOG.debug("load defaults. delete old channels for deviceID %s"%(self.deviceID))
            self.channels={}
            devicePackage=self.device['devicePackage']
            deviceFile="%sgateways/%s/devices/%s.json"%(self.path,devicePackage.replace('.','/'),self.device['deviceType'])
            deviceFileCFG={
                'channels':{}
                }
            deviceFileCFG.update(self._loadJSON(deviceFile))
            for channelName in deviceFileCFG['channels']:
                self._addChannel(channelName,deviceFileCFG['channels'][channelName])
                LOG.debug("add new channel %s from config file"%(channelName))
        except:
            LOG.error("can't read device file use empty channel configuration") 
    
    def _addChannelToConfig(self,channelName,channelCFG):
        try:
            devicePackage=self.device['devicePackage']
            deviceFile="%sgateways/%s/devices/%s.json"%(self.path,devicePackage.replace('.','/'),self.device['deviceType'])
            deviceFileCFG={}
            try:
                deviceFileCFG=self._loadJSON(deviceFile)
            except:
                LOG.error("can't read device file use empty configuration")
            if channelName in deviceFileCFG['channels']:
                return
            deviceFileCFG['channels'][channelName]=channelCFG
            self._writeJSON(deviceFile,deviceFileCFG)
        except:
            LOG.error("can't write configuration to %s"%(deviceFile))
                     
    def ifDeviceChannelExist(self,channelName):
        '''
        return true if channeName exists
        '''
        if channelName in self.channels:
            return True
        return False
    
    def getAllChannelAttribute(self,channelName):
        '''
        get all channel attribute
        public function
        '''    
        LOG.debug("get all channel atrribute for channel:%s"%(channelName))
        try:
            if not channelName in self.channels:
                raise deviceChannelException("channel %s is not exist"%(channelName))
            attribute= self.channels[channelName].keys()
            return attribute
        except deviceChannelException as e:
            raise e
        except:
            raise deviceChannelException("unknown error in getChannelValue") 
    
    def getAllChannelAttributeValue(self,channelName,attribut):
        '''
        get a value from channel attribute
        public function
        '''    
        LOG.debug("get value for channel %s and atrribute %s"%(channelName,attribut))
        try:
            if not channelName in self.channels:
                raise deviceChannelException("channel %s is not exist"%(channelName))
            if not attribut in self.channels[channelName]:
                raise deviceChannelException("attribut %s in channel %s is not exist"%(attribut,channelName))
            self.channels[channelName][attribut]
            return self.channels[channelName][attribut]
        except deviceChannelException as e:
            raise e
        except:
            raise deviceChannelException("unknown error in getChannelValue") 
    
       
    def getChannelValue(self,channelName):
        '''
        get value of channel
        public function
        '''    
        LOG.debug("get value for channel:%s"%(channelName))
        try:
            if not channelName in self.channels:
                raise deviceChannelException("channel %s is not exist"%(channelName))
            return self.channels[channelName]['value']
        except deviceChannelException as e:
            raise e
        except:
            raise deviceChannelException("unknown error in getChannelValue") 
    
    def setChannelValue(self,channelName,value):
        '''
        set value of channel
        ''' 
        try:
            if not channelName in self.channels:
                raise deviceChannelException("channel %s is not exist"%(channelName))
            if self.channels[channelName]['value']==value:
                LOG.debug("value in deviceID %s and channel %s not change"%(self.deviceID,channelName))
                self.eventAction("onrefresh",channelName)
                return
            self.channels[channelName]['value']=value 
            self.eventAction("onchange",channelName) 
        except deviceChannelException as e:    
            raise e
        except:
            raise deviceChannelException("can not set channel %s to %s"%(channelName,value))
    
    def addChannel(self,channelName,channelCFG={}):
        '''
        add a new device Channel
        default channel:
        
        
        '''
        try:
            if channelName in self.channels:
                raise deviceChannelException("can't add channel %s, channel exitst"%(channelName))
            self._addChannel(channelName, channelCFG)
            self._addChannelToConfig(channelName,self.channels[channelName])
            self.eventAction('oncreatechannel',channelName)
        except deviceChannelException as e:
            raise e
        except:
            raise deviceChannelException("unown err, can't add channel %s"%(channelName))
        
    def _addChannel(self,channelName,channelCFG={}):
        '''
        add a new device Channel
        default channel:
                '''
        try:
            self.channels[channelName]=self.__defaultChannelParameter(channelName)
            channelCFGEvents=channelCFG.get('events',{})
            
            defaultEvents=copy.deepcopy(self.__defaultChannelEvents)
            for eventName in defaultEvents:
                defaultEvents[eventName].update(channelCFGEvents.get(eventName,{}))
                
            self.channels[channelName].update(channelCFG)
            self.channels[channelName]['events']=defaultEvents
        except deviceChannelException as e:
            raise e
        except:
            raise deviceChannelException("unown err, can't add channel %s"%(channelName))