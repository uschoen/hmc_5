'''
Created on 23.12.2017

@author: uschoen
'''

__version__=5.1

# Standard library imports
import logging

# Local application imports

LOG=logging.getLogger(__name__)
WETHERDEVICE="wetter"
NAMEDEVICERSSI="rssi"


class ws300device(object):
    '''
    classdocs
    
    '''
    def __init__(self):
        LOG.debug("init cul ws300device version: %s"%(__version__))
        
    def decodeWs300weather(self,msg):
        try:
            LOG.debug("weather decode: %s length %i" %(msg,len(msg)))
            split_msg=list(msg)
            if int(split_msg[1])==0:
                LOG.debug("typ is AS3:%s"%(split_msg[1]))
            elif int(split_msg[1])==1:
                LOG.debug("typ is AS2000, ASH2000, S2000, S2001A, S2001IA, ASH2200, S300IA:%s"%(split_msg[1]))
            elif int(split_msg[1])==2:
                LOG.debug("typ is S2000R:%s"%(split_msg[1]))
            elif int(split_msg[1])==3:
                LOG.debug("typ is S2000W:%s"%(split_msg[1]))
            elif int(split_msg[1])==4:
                LOG.debug("typ is S2001I, S2001ID:%s"%(split_msg[1]))
            elif int(split_msg[1])==5:
                LOG.debug("typ is S2500H:%s"%(split_msg[1]))
            elif int(split_msg[1])==6:
                LOG.debug("typ is Pyrano (Strahlungsleistung):%s"%(split_msg[1]))
            elif int(split_msg[1])==7 and len(msg)==16:
                LOG.debug("typ is ks300:%s"%(split_msg[1]))
                self.__ks300Device(msg)
            else:
                LOG.info("typ is unknown:%s length %i"%(split_msg[1],len(msg)))
        except:
            LOG.error("can not decode weather data",exc_info=True)
    
    def __ks300Device(self,msg):
        LOG.debug("ks300 get code %s"%(msg))
        try:
            if not len(msg)==16:
                LOG.error( "incorrect message lenght: %s"%(len(msg)))
                return
            splitMsg=list(msg)
            rssi=self.calcRssi(int(splitMsg[14]+splitMsg[15],16))
            ''' wether device '''
            deviceID="%s@%s"%(WETHERDEVICE,self.config['gateway'])
            
            if not self.core.ifDeviceIDExists(deviceID):
                '''
                add device
                '''
                deviceCFG={
                    'deviceID':deviceID,
                    'deviceType':"ws300",
                    'devicePackage':"cul",
                    }
                self.core.addDevice(deviceID,deviceCFG)
            try:
                ''' 
                temperature 
                '''
                channelName="temperature"
                if not self.core.ifDeviceChannelExist(deviceID,channelName):
                    ''' add channel temperature '''
                    channeCFG={
                        'name':channelName
                        }
                    self.core.addDeviceChannel(deviceID,channelName,channeCFG)                             
                value=float(splitMsg[5]+splitMsg[2]+"."+splitMsg[3])
                if splitMsg[0] >="8":
                    value=value*(-1)
                self.core.setDeviceChannelValue(deviceID,channelName,value)
            except:
                LOG.error("can't add temperature channel",exc_info=True)
                
            try:   
                '''
                humidity
                '''
                channelName="humidity"
                if not self.core.ifDeviceChannelExist(deviceID,channelName):
                    ''' add channel humidity '''
                    channeCFG={
                        'name':channelName
                        }
                    self.core.addDeviceChannel(deviceID,channelName,channeCFG)
                value=int(splitMsg[7]+splitMsg[4])
                self.core.setDeviceChannelValue(deviceID,channelName,value)
            except:
                LOG.error("can't add humidity channel",exc_info=True)
                
            try:         
                ''' 
                wind 
                '''
                channelName="wind"
                if not self.core.ifDeviceChannelExist(deviceID,channelName):
                    ''' add channel wind '''
                    channeCFG={
                        'name':channelName
                        }
                    self.core.addDeviceChannel(deviceID,channelName,channeCFG)
                value=int(splitMsg[8]+splitMsg[9]+splitMsg[6])/10
                self.core.setDeviceChannelValue(deviceID,channelName,value)
            except:
                LOG.error("can't add wind channel",exc_info=True)
                
            try:
                '''
                windchill
                '''  
                channelName="windchill"
                if not self.core.ifDeviceChannelExist(deviceID,channelName):
                    ''' add channel windchill '''
                    channeCFG={
                        'name':channelName
                        }
                    self.core.addDeviceChannel(deviceID,channelName,channeCFG)
                value=int(splitMsg[8]+splitMsg[9]+splitMsg[6])/10
                self.core.setDeviceChannelValue(deviceID,channelName,value)
            except:
                LOG.error("can't add windchill channel",exc_info=True)
                
            try:    
                '''
                rain
                '''
                channelName="rain"
                if not self.core.ifDeviceChannelExist(deviceID,channelName):
                    ''' add channel rain '''
                    channeCFG={
                        'name':channelName
                        }
                    self.core.addDeviceChannel(deviceID,channelName,channeCFG)
                value=int(splitMsg[13]+splitMsg[10]+splitMsg[11],16)
                self.core.setDeviceChannelValue(deviceID,channelName,value)
            except:
                LOG.error("can't add rain channel",exc_info=True)
                
            try:
                '''
                rssi
                '''
                channelName="rssi"
                if not self.core.ifDeviceChannelExist(deviceID,channelName):
                    ''' add channel rssi '''
                    channeCFG={
                        'name':channelName
                        }
                    self.core.addDeviceChannel(deviceID,channelName,channeCFG)
                self.core.setDeviceChannelValue(deviceID,channelName,rssi)
            
            except:
                LOG.error("can't add rssi channel",exc_info=True)
                
            
        except :
            LOG.critical("can not update ks300", exc_info=True)

    def _addWS300(self,deviceID,deviceTyp,channelName,ChannelValue,rssi):
        try:
            '''
            if device exists
            '''
            if not self.core.ifDeviceIDExists(deviceID):
                LOG.info("add new deviceID: %s"%(deviceID))    
                self.addNewDevice(deviceID,deviceTyp)
            
            '''
            if not channel exists
            '''
            if not self.core.ifDeviceChannelExist(deviceID,channelName):
                LOG.info("add new channel %s for deviceID: %s"%(channelName,deviceID)) 
                self.addChannel(deviceID,channelName)
            '''
            set channel
            '''
            LOG.info("set channel %s to value: %s"%(channelName,ChannelValue)) 
            self.core.setDeviceChannelValue(deviceID,channelName,ChannelValue)
            '''
            if channel rssi exists
            '''
            if not self.core.ifDeviceChannelExist(deviceID,'rssi'):
                LOG.info("add new channel rssi to deviceID: %s"%(deviceID)) 
                self.addChannel(deviceID,'rssi')
            '''
            set rssi value
            '''
            LOG.info("add set channel rssi to value: %s"%(rssi)) 
            self.core.setDeviceChannelValue(deviceID,"rssi",rssi)
        except:
            LOG.error("can not add ws300 deviceID %s"%(deviceID),exc_info=True)