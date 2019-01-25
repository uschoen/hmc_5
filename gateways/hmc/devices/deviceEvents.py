'''
Created on 01.12.2018

@author: uschoen
'''

__version__='5.0'
__author__ = 'ullrich schoen'

# Standard library imports
import time
import copy
import logging
# Local application imports
from .deviceException import deviceEventException


LOG=logging.getLogger(__name__)


class deviceEvents():

    def __init__ (self):
        '''
        device ID
        '''     
        self.eventTyps={
            'onchange':self.onchange,
            'oncreatechannel':self.oncreateChannel,
            'onrefresh':self.onrefresh,
            'oncreate':self.oncreate,
            'ondelete':self.ondelete
            }  
        
        self.eventCFG={
            'onchange':{
                'timestamp':int(time.time()),
                'module':[]
                    },
            'oncreate':{
                'timestamp':int(time.time()),
                'module':[]
                    },
            'onrefresh':{
                'timestamp':int(time.time()),
                'module':[]
                    },
            'ondelete':{
                'timestamp':0,
                'module':[]
                    },
            'oncreatechannel':{
                'timestamp':0,
                'module':[]
                }
            }          
        LOG.debug("init deviceEvents finish(%s)"%(self.deviceID))
        
    def getEventParameters(self,event):
        '''
         get the event parameter back
        ''' 
        try:
            if event not in self.eventCFG:
                LOG.error("event %s not found in event parameter"%(event))
                return {}
            eventList=copy.deepcopy(self.eventCFG.get(event,{}))
            return eventList
        except:
            raise deviceEventException("can't return events parameter")
               
    def getEventsTyps(self):
        '''
        return a list with all eventsTyps
        '''
        try:
            a=self.eventTyps.keys()
            return a
        except:
            raise deviceEventException("can't return eventsTyps")
    
    def eventAction(self,eventName,channelName):
        try:
            if eventName not in self.eventTyps:
                LOG.error("event % not found %s"%(eventName))
                return
            channelEvents=[]
            
            if not channelName=="device":
                ''' update event channel '''
                channelEvents=self.channels[channelName]['events'].get(eventName,[])
                self.eventTyps[eventName](channelName,channelEvents)
                callEvents=channelEvents.get('module',{})
                if len (callEvents)>0:
                    '''  
                    if device channel have one ore more module to call
                    '''
                    args={
                                'deviceID':self.deviceID,
                                'channelName':channelName,
                                'eventTyp':eventName}
                    self.core.callModul(callEvents,args)
            ''' update event device '''
            channelEvents=self.device['events'].get(eventName,[])
            LOG.info("%s event call from channel %s and deviceID %s"%(eventName,channelName,self.deviceID))
            self.eventTyps[eventName]('device',channelEvents)
            args={
                            'deviceID':self.deviceID,
                            'channelName':channelName,
                            'eventTyp':"device"}
            callEvents=channelEvents.get('module',{})
            if len (callEvents)>0:
                '''  
                if device have one ore more module to call
                '''
                self.core.callModul(callEvents,args)
        except:
            raise deviceEventException("can't try event action for event name %s and channel %s"%(eventName,channelName))
    
    def onchange(self,channelName,eventParameter):
        '''
        onchange event
        '''
        try:
            eventParameter['timestamp']=int(time.time())
        except:
            raise deviceEventException("can't try onchange evnet for deviceID:%s channelName %s"%(self.deviceID,channelName))
    
    def oncreate(self,channelName,eventParameter):
        '''
        oncreate event
        '''
        try:
            eventParameter['timestamp']=int(time.time())
        except:
            raise deviceEventException("can't try oncreate evnet for deviceID:%s channelName %s"%(self.deviceID,channelName))
    
    def onrefresh(self,channelName,eventParameter):
        '''
        onrefresh event
        '''
        try:
            eventParameter['timestamp']=int(time.time())
        except:
            raise deviceEventException("can't try onrefresh evnet for deviceID:%s channelName %s"%(self.deviceID,channelName))
        
    def ondelete(self,channelName,eventParameter):
        '''
        ondelete event
        '''
        try:
            eventParameter['timestamp']=int(time.time())
        except:
            raise deviceEventException("can't try onrefresh evnet for deviceID:%s channelName %s"%(self.deviceID,channelName))
    
    def oncreateChannel(self,channelName,eventParameter):
        '''
        oncratechannel event
        '''
        try:
            eventParameter['timestamp']=int(time.time())
        except:
            raise deviceEventException("can't try oncreateChannel evnet for deviceID:%s channelName %s"%(self.deviceID,channelName))
    
    