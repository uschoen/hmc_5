'''
Created on 01.12.2018

@author: uschoen
'''


__version__='5.1'
__author__ = 'ullrich schoen'
__DEVICETYPE__="defaultDevice"
__DEVICEPACKAGE__="hmc"

# Standard library imports
import copy
import logging
# Local application imports
from .deviceException import deviceParameterException

LOG=logging.getLogger(__name__)

class deviceParameter():

    def __init__ (self):
        '''
        device ID
        '''         
        self.device={
                        'enable':True,
                        'name':self.deviceID,
                        'type':__DEVICETYPE__,
                        'package':__DEVICEPACKAGE__,
                        'events':{}
                      }
        
        try:
            self.__defaultDeviceEvents=dict((events,self.getEventParameters(events)) for events in self.getEventsTyps())
        except:
            self.__defaultDeviceEvents={}
            
        LOG.debug("init deviceParameter finish(%s)"%(self.deviceID))
    
    def updateDeviceParameter(self,deviceCFG={}):
        '''
        update default device parameter
        '''
        try:
            deviceCFGEvents=deviceCFG.get('events',{})
            
            defaultEvents=copy.deepcopy(self.__defaultDeviceEvents)
            for eventName in defaultEvents:
                defaultEvents[eventName].update(deviceCFGEvents.get(eventName,{}))
            self.device.update(deviceCFG)
            self.device['events']=defaultEvents
        except:
            LOG.error("can't update device parameter,use defaults",exc_info=True)
    
    def getAllDeviceAttribute(self):
        '''
        return all device parameter back
        '''
        deviceAttribute=self.device.keys()
        return deviceAttribute
    
    def getDeviceAttributValue(self,attributName):
        '''
        return the value of the attribut
        '''
        value=""
        try:
            if not attributName in self.device:
                raise deviceParameterException("can't find attribute %s in deviceID %s"%(attributName,self.deviceID))
            value=self.device[attributName]
        except:
            pass
        return value
    
    def ifDeviceEnable(self):
        '''
        return true if the device enable
        '''
        return self.device['enable']
    
    def enableDevice(self):
        '''
        enable device
        '''
        self.eventAction("onchange","device") 
        self.device['enable']=True
    
    def disableDevice(self):
        '''
        disable device
        '''
        self.eventAction("onchange",'device') 
        self.device['enable']=False
        
    def delete(self,callEvents=True):
        '''
        delete function of the device
        '''
        try:
            LOG.info("delete device %s"%(self.deviceID))    
            if callEvents:
                self.eventAction("ondelete",'device') 
        except:
            raise deviceParameterException("can not call delete event for device %s"%(self.deviceID))