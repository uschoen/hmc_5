'''
Created on 01.12.2018

@author: uschoen
'''

__version__='5.1'
__author__ = 'ullrich schoen'

# Standard library imports
import threading
import logging.config
import time

# Local application imports
from core.hmcException import gatewayException 

class defaultGateway(threading.Thread):
    '''
    classdocs
    '''
    def __init__(self,gatewaysCFG,core):
        '''
        Constructor
        '''
        threading.Thread.__init__(self)
        self.log=logging.getLogger(__name__) 
        self.core=core
        self.config={
                        'name':"default Device",
                        'enable':False,
                      }
        self.config.update(gatewaysCFG)
        
        ''' Name of the gateway '''
        self.name=self.config['name']
        
        ''' gateway running '''
        self.running=self.config.get('enable',False)
        
        ''' core intance '''
        self.core=core
        
        self.log.debug("build defaultGateways %s instance"%(__name__))
        
    def defaultDeviceConfig(self,deviceID):
        config={
                    "deviceID":deviceID,
                    "enable":True,
                    "name":deviceID,
                    'deviceType':"defaultDevice",
                    'devicePackage':"hmc"
                   }
        return config
        
    def defaultChannelConfig(self,deviceID):
        config={}
        return config
    
    def send(self,command):
        self.log.info("gateway %s can`t send commands"%(self.config.get('name',"unkown")))
    
    def run(self):
        try:
            self.log.info("%s start"%(self.config.get('name',"unkown")))
            while self.running:
                self.log.debug("default gateway, is a dummy")
                time.sleep(0.5)
            self.log.warning("%s gateway is now stoped"%(self.config.get('name',"unkown")))
        except:
            raise gatewayException("some error in default gateway. gateway stop")
       
    def shutdown(self):
        '''
        shutdown the gateway
        '''
        self.running=0
        self.log.critical("stop %s gateways"%(self.config.get('name',"unkown")))
    
    def addNewDeviceChannel(self,deviceID,channelName,channelCFG={}):
        try:
            config={}
            config=self.defaultChannelConfig(deviceID)
            config.update(channelCFG)
            self.core.addDeviceChannel(deviceID,channelName,config) 
        except:
            raise gatewayException("can not add new device channel %s for deviceID %s to core"%(channelName,deviceID))
    
    def addNewDevice(self,deviceID,deviceConfig={}):
        '''
        add a new sensor to core core devices
        '''
        try:
            deviceCFG={}
            deviceCFG=self.defaultDeviceConfig(deviceID)
            deviceCFG.update(deviceConfig)
            if not self.core.ifDeviceIDExists(deviceID):
                self.log.info("add deviceID %s to core"%(deviceID))
                self.core.addDevice(deviceID=deviceID,deviceCFG=deviceCFG)
        except:
            raise gatewayException("can not add new deviceID %s to core"%(deviceID))   
        
if __name__ == '__main__':
    logCFG={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "simple": {
                    "format": "%(asctime)s %(levelname)s - %(message)s"
                }
            },
        
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG",
                    "formatter": "simple",
                    "stream": "ext://sys.stdout"
                },
            },   
            "root": {
                "level": "DEBUG",
                "handlers": ["console"]
            }
        }
    logger=logging.getLogger(__name__) 
    logging.config.dictConfig(logCFG)
    logger.info("start gateway")
    class core(object):
        def ifDeviceIDExists(self):
            return False
            
    
    coreOBJ=core()
    gatewayCFG={    
                "config":{
                    "name":"defaultGW test"}
                        }
    gateways = defaultGateway(gatewayCFG,coreOBJ)
    gateways.daemon = True
    logger.info("start gateway %s"%("deafultGW"))
    gateways.start()
    time.sleep(2)
    gateways.stop()
    time.sleep(2)
    print("stop")     
