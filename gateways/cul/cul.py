'''
Created on 01.12.2018

@author: uschoen

need python3 modul pyserial
sudo pip3 install pyserial

'''

__version__='5.1'
__author__ = 'ullrich schoen'

# Standard library imports
import logging
import time
import serial                   #@UnresolvedImport

# Local application imports
from core.hmcException import gatewayException
from gateways.hmc.defaultGateway import defaultGateway
from gateways.cul.fs20 import fs20device
from gateways.cul.ws300 import ws300device

LOG=logging.getLogger(__name__)
LINEFEED=b'\r\n'


class server(defaultGateway,
             fs20device,
             ws300device
             ):
    '''
    classdocs
    '''
    def __init__(self,gatewaysCFG,core):
        '''
        Constructor
       
        Vars from default GW
        LOG=logging.getLogger(__name__) 
        self.core=core
        self.config={
                        'name':"default Device",
                        'enable':False,
                      }
        self.name=self.config['name']
        self.running=self.config.['enable']
        '''
        defaultGateway.__init__(self,gatewaysCFG,core)
        self.config={
            'usbport':"/dev/ttyACM0",
            'baudrate':"9600",
            'timeout':1,
            'blockTime':60,
            'alive':320       
            }
        self.config.update(gatewaysCFG)
        
        ''' cul devices '''
        self.__culDevices={
            '21':self.__getBudget,
            'F':self.decodeFS20,
            'K':self.decodeWs300weather
            }
        
        ''' send budget '''
        self.__budget = 0
        
        ''' USB Port '''
        self.__USBport=False
        
        ''' serial data '''
        self.__pending_line = []
        
        ''' block at errors '''
        self.__block=0
        
        ''' check alive '''
        self.__alive=0
        
        ''' init cul devices '''
        fs20device.__init__(self)
        ws300device.__init__(self)
        
        LOG.info("init cul gateway version:%s"%(__version__))
        
    def send(self,command):
        LOG.info("gateway %s can`t send commands"%(self.config.get('name',"unkown")))
    
    def run(self):
        try:
            LOG.info("%s start"%(self.config.get('name',"unkown")))
            while self.running:
                try:
                    if self.__block>(time.time()):
                        time.sleep(1)
                        continue
                    if not self.__USBport:
                        self.__openUSB(self.config['usbport'], self.config['baudrate'], self.config['timeout'])
                        self.__initCUL()
                        HWVerion=self.__readHWVersion()
                        Verion=self.__readVersion()
                        LOG.info("INIT CUL Version:%s HW:%s"%(Verion,HWVerion))
                        self.__alive=int(time.time())+self.config['alive']
                    data=self.__readResult()
                    if not data=="":
                        self.__alive=int(time.time())+self.config['alive']
                        LOG.debug("get message from cul:%s"%(data))
                        if data[:2] in self.__culDevices:
                            self.__culDevices[data[:2]](data[2:])
                            continue
                        if data[:1] in self.__culDevices:
                            self.__culDevices[data[:1]](data[1:])
                            continue
                        LOG.warning("unkown meassges from CUL %s"%(data))
                    if self.__alive<time.time():
                        ''' check if cul alive '''
                        self.__readBudget()
                    if (self.__alive+5)<time.time():
                        LOG.error("get cul timeout, restart")
                        self.__closeUSB()
                    time.sleep(0.1)
                except (gatewayException) as e:
                    self.__blockCul(self.config['blockTime'])
                    LOG.warning("cul get some error %s"%(e.msg), exc_info=True)
                    
            LOG.warning("%s gateway is now stoped"%(self.config.get('name',"unkown")))
        except:
            raise gatewayException("some error in default gateway. gateway stop")
       
    def shutdown(self):
        '''
        shutdown the cul gateway
        '''
        try:
            LOG.critical("shutdown cul")
            self.running=False
            self.__closeUSB() 
        except:
            LOG.critical("some error in cul to shutdown")
    
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
                LOG.info("add deviceID %s to core"%(deviceID))
                self.core.addDevice(deviceID=deviceID,deviceCFG=deviceCFG)
        except:
            raise gatewayException("can not add new deviceID %s to core"%(deviceID))   
    
    def __sendCommand(self,command):
        '''
        send a command
        
        raise Exception 
        '''
        try:
            LOG.debug("send command:%s"%(command))
            self.__USBport.write(command)
            self.__USBport.write(LINEFEED)
        except:
            raise gatewayException("can not send command: %s"%(command),False)
   
    def __readResult(self):
        '''
        read usb port
        
        return string
        raise exception on error
        '''        
        try:
            readChunks=[]
            completed_line=""           
            while self.__USBport.inWaiting():
                readChunks.append(self.__USBport.read(1))
                if readChunks[-1]==b'':
                    break
                if readChunks[-1]==b'\n':
                    break
                if not self.running:
                    break
            completed_line=b''.join(readChunks[:-2]).decode()
            return completed_line
        except (gatewayException) as e:
            raise e
        except:
            raise gatewayException("can not read usb port")  
          
    def calcRssi(self,RAWvalue):
        '''
        calculate  RSSI Value
        '''
        try:
            rssi=RAWvalue
            if rssi>=128:
                rssi=((rssi-256)/2-74)
            else:
                rssi=rssi/2-74
            return rssi
        except:
            gatewayException("some error to calc RSSI",False)
            
    
    def __readHWVersion(self):
        '''
         command to read budget
        exception will be raise
        '''
        try:
            LOG.debug("read hardware version")
            self.__sendCommand(b'VH')
            time.sleep(0.1)
            culHWVersion=self.__readResult()
            return culHWVersion
        except gatewayException as e:
            raise e
        except:
            raise gatewayException("can't not read HW Version",False) 
    
    def __readBudget(self):
        '''
         command to read budget
        exception will be raise
        '''
        try:
            LOG.debug("read budget")
            self.__sendCommand(b'X')
            time.sleep(0.1)
        except gatewayException as e:
            raise e
        except:
            raise gatewayException("can't not read budget",False)
    
    def __getBudget(self,value):
        try:
            budget=self.__calcBudget(value)
            self.__budget=budget
            LOG.info("cul get budget %s"%(self.__budget))
        except:
            raise gatewayException("can't not getbudget",False)      

    
    def __calcBudget(self,value):
        '''
         command to read budget
        exception will be raise
        '''
        try:
            budget = int(value[2:].strip()) * 10 or 1
            return budget
        except gatewayException as e:
            raise e
        except:
            raise gatewayException("can't not calcbudget",False)
            
    def __readVersion(self):
        '''
         command to read budget
        exception will be raise
        '''
        
        try:
            LOG.debug("read software version")
            self.__sendCommand(b'V')
            time.sleep(0.1)
            culVersion=self.__readResult()
            return culVersion
        except gatewayException as e:
            raise e
        except:
            raise gatewayException("can't not read version",False) 
    
    def __initCUL(self):
        '''
        init command for cul stick
        exception will be raise
        '''
        try:
            LOG.info("initCUL")
            self.__sendCommand(b'X21')
            self.__USBport.reset_input_buffer()
            time.sleep(0.1)
        except gatewayException as e:
            raise e
        except:
            raise gatewayException("can't not init cul",False) 
    
    def __openUSB(self,usbport,baudrate,timeout):
        '''
        open usb port to cul stick
        
        return  true if usb open
                false is usb not open
        
        exception will be raise
        '''
        if not self.core.ifFileExists(usbport):
            raise gatewayException("no such usb port: %s"%(usbport),False) 
        try:
            if self.__USBport:
                if self.__USBport.isOpen():
                    return                
            LOG.info("open serial, port:%s baud:%s timeout:%s"%(usbport,baudrate,timeout))
            self.__USBport=serial.Serial(
                              port=usbport,
                              baudrate = baudrate,
                              parity=serial.PARITY_NONE,
                              stopbits=serial.STOPBITS_ONE,
                              bytesize=serial.EIGHTBITS,
                              timeout=timeout
                            ) 
        except:
            self.__USBport=False
            raise gatewayException("can not open serial, port:%s baud:%s timeout:%s"%(usbport,baudrate,timeout),False)
              
    def __closeUSB(self):
        '''
        close usb port
        '''
        try:
            self.__USBport.close()
            self.__USBport=False
        except:
            LOG.info("close serial, port:%s "%(self.config['usbport']))

    def __blockCul(self,blockTime):
        try:
            self.__block=int(time.time())+blockTime
            LOG.warning("block cul for %s sec"%(blockTime))
        except:
            pass