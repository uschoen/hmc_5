'''
Created on 01.12.2018

@author: uschoen
'''


__version__='5.0'
__author__ = 'ullrich schoen'

# Standard library imports
import os
import time
import re
import copy
import logging

# Local application imports
from core.hmcException import gatewayException
from gateways.hmc.defaultGateway import defaultGateway

LOG=logging.getLogger(__name__)


class ds1820(defaultGateway):
    '''
    classdocs
    '''
    def __init__(self,gatewaysCFG,core):
        defaultGateway.__init__(self,gatewaysCFG,core)
        self.config={
                        "interval": 360,
                        "deviceType": "ds1820", 
                        "devicePackage": "raspberry.onewire", 
                        "path": "/sys/bus/w1/devices/", 
                        "busmaster":"w1_bus_master1",
                        "tolerance": 1, 
                        "blockGateway":600,
                        "gateway":"unkown",
                        'name':"default Device",
                        'enable':False
                        }
        # confiuration 
        self.config.update(gatewaysCFG)
        # all connected ds1820 sensors
        self.__connectedSensors={}
        # if error, block gateway for x sec
        self.gatewayBlockTime=0
        # last time read sensors
        self.__LastReadSenors=0
        
        LOG.info("build ds1820 gateway, %s instance"%(__name__))
    
    def __defaultDeviceConfig(self,sensorID):
        '''
        give the default parameter for a device ID back
        '''
        config={
                'name':sensorID,
                'deviceID':self.__deviceID(sensorID),
                'deviceType':self.config['deviceType'],
                'devicePackage':self.config['devicePackage']
               }
        return config 
    
    def __defaultChannelConfig(self,sensorID):
        config={
                'name':sensorID,
                'value':0
               }
        return config                      
    
    '''
    run
    '''    
    def run(self):
        try:
            LOG.debug("ds1820 gateway start")
            while self.running:
                try:
                    if self.__LastReadSenors<time.time():
                        if self.__checkOneWire():
                            self.__checkConnectedSensors()
                            
                            for sensorID in self.__connectedSensors:
                                try:
                                    if not self.running:
                                        break
                                    self.__readSensors(sensorID)
                                except:
                                    pass
                            self.__LastReadSenors=int(time.time())+self.config.get("interval",360)
                    time.sleep(0.5)
                except:
                    LOG.critical("can't check onewire bus")
                    self.__blockGateway()
            LOG.warning("ds1820 gateway stop")
        except gatewayException as e:
            raise e        
        except:
            LOG.error("some error in raspberry onewire gateway. gateway stop")
    
    def __readSensors(self,sensorID):
        try:
            deviceID=self.__deviceID(sensorID)
            '''
            check if sensor connected to onewire bus
            '''                    
            if  self.__connectedSensors[sensorID]["connected"]==False:
                LOG.info("sensor id %s is disconnected"%(sensorID))
                return
                '''
            check if sensor in core exists
            '''
            if not self.core.ifDeviceIDExists(deviceID):
                print (deviceID)
                self.__addNewDevice(sensorID)
            '''
            check if sensor enable in core
            '''
            if not self.core.ifDeviceIDenable(deviceID):
                LOG.info("sensor id %s is disabled"%(sensorID))
                return 
            '''
            check if sensor channel in device
            '''
            if not self.core.ifDeviceChannelExist(deviceID,"temperature"):
                self.__addNewChannel(sensorID)
            '''
            read temperature from sensor
            '''   
            LOG.debug("read sensorID %s"%(sensorID))
            path=self.config["path"]+sensorID+"/w1_slave"
            self.__updateSensorID(sensorID,self.__readSensorValue(path))
        except:
            self.__connectedSensors[sensorID]["connected"]=False
            LOG.error("can not read/update sensorID %s, disable senor"%(sensorID))
            
    def __readSensorValue(self,path):
        '''
        read Sensor
        '''
        try:
            f = open(path, "r")
            line = f.readline()
            if re.match(r"([0-9a-f]{2} ){9}: crc=[0-9a-f]{2} YES", line):
                line = f.readline()
                m = re.match(r"([0-9a-f]{2} ){9}t=([+-]?[0-9]+)", line)
                if m:
                    value =str(float(m.group(2)) / 1000.0)
                    f.close()
                    value=round(float(value),2)
                    return value
                else:
                    raise gatewayException("value error at sensor path"%(path),False)    
            else:
                raise gatewayException("crc error at sensor path"%(path),False)
        except (gatewayException) as e:
            raise e
        except:
            raise gatewayException("can not read sensor path %s"%(path),False)
               
    def __updateSensorID(self,sensorID,value):
        '''
        read onewire sensor and compare old & new value
        update core device
        '''
        try:
            deviceID=self.__deviceID(sensorID)
            lastValue=self.core.getDeviceChannelValue(deviceID,'temperature')
            
            tempDiv=float(self.config["tolerance"])
            LOG.debug("sensorID:%s old value:%s new value:%s tolerance:%s"%(sensorID,lastValue,value,tempDiv))
            
            if (lastValue < (value-tempDiv)) or (lastValue >(value+tempDiv)):
                LOG.debug("temperature is change, update device channel temperature") 
                self.core.setDeviceChannelValue(deviceID=deviceID,channelName="temperature",value=value)
                LOG.debug("update for deviceID %s success"%(deviceID))                                   
            else:
                LOG.debug("temperature is not change")
        except:    
            raise gatewayException("can not update sensorID %s"%(sensorID)) 
    
          
    def __checkConnectedSensors(self):
        '''
        check if new onewire sensor connect to bus and 
        add them to core
        '''
        try:
            LOG.debug("check connected sensors")
            self.__disableAllSensor()
            sensorList =os.listdir(self.config["path"])
            LOG.debug("read connected sensors in path %s"%(sensorList))
            for sensorID in sensorList:
                LOG.debug("found sensorID %s"%(sensorID))
                if sensorID==self.config["busmaster"]:  continue
                if sensorID in self.__connectedSensors:
                    self.__connectedSensors[sensorID]["connected"]=True
                else:
                    try:
                        if not self.core.ifDeviceIDExists(self.__deviceID(sensorID)):
                            self.__addNewDevice(sensorID)
                    except:
                        LOG.error("can not add new sensorID %s"%(sensorID),exc_info=True)
            self.__deleteDisconectedSensors()
        except:
            raise gatewayException("can't not check connectedt senors")
    
    def __deviceID(self,sensorID):
        deviceID="%s@%s"%(sensorID,self.config.get("gateway","unknown"))
        return deviceID
    
    def __addNewChannel(self,sensorID):
        '''
        add a new channel with name temperature
        '''
        try:
            channelName="temperature"
            deviceID=self.__deviceID(sensorID)
            channelCFG=self.__defaultChannelConfig(sensorID)
            self.core.addDeviceChannel(deviceID,channelName,channelCFG) 
            LOG.debug("add new channel %s to deviceID %s"%(channelName,deviceID))
        except:
            self.__connectedSensors[sensorID]={
                                                "connected":False
                                                }
            raise gatewayException("can not add new channel temperature for deviceID %s to core"%(deviceID))
            
    
    def __addNewDevice(self,sensorID):
        '''
        add a new sensor to core core devices
        '''
        try:
            deviceCFG=self.__defaultDeviceConfig(sensorID)
            self.core.addDevice(self.__deviceID(sensorID),deviceCFG)
            LOG.debug("add new sensorID %s with deviceID %s and type %s"%(sensorID,self.__deviceID(sensorID),self.config['deviceType']))
            self.__connectedSensors[sensorID]={
                                                "connected":True
                                                }
        except:
            self.__connectedSensors[sensorID]={
                                                "connected":False
                                                }
            raise gatewayException("can not add new deviceID %s to core"%(self.__deviceID(sensorID)))
    
    
    def __disableAllSensor(self):
        '''
        disable all gateways sensors 
        '''
        LOG.debug("set all sensor value connect to false")
        for sensorID in self.__connectedSensors:
            self.__connectedSensors[sensorID]["connected"]=False
    
    def __deleteDisconectedSensors(self):
        '''
        delete disconnected sensor from gateways list
        '''
        try:
            LOG.debug("clear up and delete disconnected sensor")
            senors=copy.deepcopy(self.__connectedSensors)
            for sensorID in senors:
                if self.__connectedSensors[sensorID]["connected"]==False:
                    del self.__connectedSensors[sensorID]
                    LOG.info("delete sensor %s"%(sensorID))
        except:
            LOG.error("can't clear disconnect sensors",exc_info=True)
            
    def __checkOneWire(self):
        '''
        check if onewire path on host exists and one wire install
        '''
        if self.gatewayBlockTime>time.time():
            return False
        
        if not os.path.isdir(self.config["path"]):
            self.__blockGateway()
            LOG.error("no onewire installed")
            return False
        return True
           
    def __blockGateway(self):
        LOG.info("block onewire bus for % sec"%(self.config.get("blockGateway",600)))
        self.gatewayBlockTime=int(time.time())+self.config.get("blockGateway",600)
