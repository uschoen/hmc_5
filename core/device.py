'''
Created on 01.12.2018

@author: uschoen
'''

__version__='5.0'
__author__ = 'ullrich schoen'

# Standard library imports
import copy
import importlib
import time
import os
import py_compile
import logging
# Local application imports
from .hmcException import coreDeviceException,coreException

# Local apllication constant
LOG=logging.getLogger(__name__)

class device():
    '''
    core events function
    '''
    def __init__(self,*args):
        '''
        core devices
        '''
        self.devices={}
        
        LOG.info("load core.device modul")
    
    def addDevice(self,deviceID,deviceCFG,forceUpdate=False):
        ''' 
        add a new device to core
        
        deviceID: device id from thr device
        deviceCFG: configuration of the device
        
        deviceCFG:{
                    'type': "example",
                    ...
                  }
        '''
        if self.ifDeviceIDExists(deviceID):
            raise coreDeviceException("deviceID %s is exists"%(deviceID),False)
        try:
            restore=False
            deviceConfig={
                'device':copy.deepcopy(deviceCFG),
                'channels':{}}
            self.__buildDevice(deviceID,deviceConfig,restore)
            self.updateRemoteCore(forceUpdate,deviceID,'addDevice',deviceID,deviceCFG)
        except:
            raise coreDeviceException("can't not add deviceID %s"%(deviceID))
    
    def getDeviceAttributValue(self,deviceID,attributName):
        if not self.ifDeviceIDExists(deviceID):
            raise coreDeviceException("deviceID %s is not exists"%(deviceID),False) 
        try:
            deviceAttributeValue=self.devices[deviceID].getDeviceAttributValue(attributName)
            return deviceAttributeValue
        except:
            raise coreDeviceException("can't return device attribute value %s for deviceID %s"%(attributName,deviceID))
            
    def getAllDeviceAttribute(self,deviceID):
        '''
        return all device attribute from a device back
        
        deviceID= device ID
        
        return
        '''
        if not self.ifDeviceIDExists(deviceID):
            raise coreDeviceException("deviceID %s is not exists"%(deviceID),False)
        try:
            deviceAttribute=self.devices[deviceID].getAllDeviceAttribute()
            return deviceAttribute
        except:
            raise coreDeviceException("can't return device attribute for deviceID %s"%(deviceID))
    
    def restoreDevice(self,objectID,deviceCFG,forceUpdate=False):
        '''
            restore a device
            
            deviceID: device id from thr device
            deviceCFG: configuration of the device
            
            deviceCFG:
                'device':{
                    'type': "example",
                    ...
                        },
                'channels': {
                    ...
                        }
                    }
        ''' 
        try:
            restore=True
            LOG.info("restore device with device id %s and deviceType:%s"%(objectID,deviceCFG['device']['type']))
            if self.ifDeviceIDExists(objectID):
                LOG.info("deviceID  exists :%s, old device will be delete"%(objectID))
                self.__deleteDevice(objectID)
            self.__buildDevice(objectID,copy.deepcopy(deviceCFG),restore)
            self.updateRemoteCore(forceUpdate,objectID,'restoreDevice',objectID,deviceCFG)
        except (coreDeviceException) as e:
            raise e
        except:
            raise coreDeviceException("can't not restoreDevice deviceID %s"%(objectID))
    
    def __deleteDevice(self,objectID):
        '''
            internal delte function to delte a device
            
            deviceID: device id forthe device
            callDeleteEvent: call the delete Event in the device if true
        '''
        try:
            if not self.ifDeviceIDExists(objectID):
                return
            LOG.info("delete deviceID %s"%(objectID))
            self.devices[objectID].delete(False)
            del self.devices[objectID]
        except coreDeviceException as e:
            raise e
        except:
            raise coreDeviceException("can't not delete device deviceID %s"%(objectID))
            
    def ifDeviceIDExists(self,deviceID):
        '''
            check if device exist
            
            deviceID: the device id to check if exists
            
            return: 
                true if device exists
                false if no device exists
            
            exception:
                hmc.coreExecption
        ''' 
        try: 
            if deviceID in self.devices:
                return True
            return False  
        except:
            raise coreDeviceException("can't not ckeck ifDeviceExists deviceID %s"%(deviceID))

    def getAllDeviceID(self):
        '''
        returnall device IDs
        '''
        try:
            return self.devices.keys()
        except:
            raise coreDeviceException("can't not get ll devices deviceID")
    
    def getDeviceConfiguration(self,deviceID) :
        '''
        get the device configuration back
        exception:
                coreDeviceExecption
        '''
        if not self.ifDeviceIDExists(deviceID):
            raise coreDeviceException("deviceID %s ist not exists"%(deviceID),False)
        try:
            return self.devices[deviceID].getConfiguration()
        except:
            raise coreDeviceException("can't not read deviceConfiguration deviceID %s"%(deviceID))
    
    def disableDeviceID(self,deviceID): 
        '''
        disable a device
        '''
        if not self.ifDeviceIDExists(deviceID):
            raise coreDeviceException("deviceID %s is not exist"%(deviceID),False)
        try: 
            self.devices[deviceID].disableDevice()
        except:
            raise coreDeviceException("can't not disable deviceID %s"%(deviceID))
    
    def enableDeviceID(self,deviceID):
        '''
        enable a device
        '''
        if not self.ifDeviceIDExists(deviceID):
            raise coreDeviceException("deviceID %s is not exist"%(deviceID),False)
        try: 
            self.devices[deviceID].enableDevice()
        except:
            raise coreDeviceException("can't not enable deviceID %s"%(deviceID))
      
    def ifDeviceIDenable(self,deviceID):
        '''
            check if device enable
            
            deviceID: the device id to check if enable
            
            return: 
                true if device enable
                false if no device disable
            
            exception:
                coreDeviceExecption
        '''
        if not self.ifDeviceIDExists(deviceID):
            raise coreDeviceException("deviceID %s is not exist"%(deviceID),False)
        try: 
            return self.devices[deviceID].ifDeviceEnable()
        except:
            raise coreDeviceException("can't not check ifdisable  deviceID %s"%(deviceID))
        
    def __buildDevice(self,deviceID,deviceCFG,restore=False):
        '''
            build a new device  
        '''  
        try:
            defaultDeviceCFG={
                                'device':{
                                    'deviceType':"defaultDevice",
                                    'devicePackage':"hmc",
                                    'deviceID':deviceID},
                                'channels':{}}
            
            if not restore:
                defaultDeviceCFG['device'].update(deviceCFG.get('device',{}))
            else:
                defaultDeviceCFG['device'].update(deviceCFG.get('device',{}))
                defaultDeviceCFG['channels'].update(deviceCFG.get('channels',{}))
            
            devicePackage="gateways.%s.devices.%s"%(defaultDeviceCFG['device']['devicePackage'],defaultDeviceCFG['device']['deviceType'])
            devicePath="%s%s"%(self.path,devicePackage.replace('.','/'))
            '''
                check if device file exists, if not, crate a new one
            '''
            self.__checkIfDeviceFileExists("%s.py"%(devicePath),defaultDeviceCFG['device']['deviceType'],defaultDeviceCFG['device']['devicePackage'])
            '''
                check if config file exists
            '''
            self.__checkIfConfigExists("%s.json"%(devicePath))
            '''
                build
            '''
            try:
                classModul = self.__loadPackage(devicePackage)
                className = "deviceManager"
                argumente={'deviceID':deviceID,'core':self,'deviceCFG':defaultDeviceCFG,'restore':restore}
                self.devices[deviceID]= getattr(classModul,className)(**argumente)
                if hasattr(classModul, '__version__'):
                    if classModul.__version__<__version__:
                        LOG.warning("version of %s is %s and can by to low"%(devicePackage,classModul.__version__))
                    else:
                        LOG.debug( "version of %s is %s"%(devicePackage,classModul.__version__))
                else:
                    LOG.warning("package %s has no version Info"%(devicePackage))
            except :
                raise coreDeviceException("can't not load package %s"%(devicePackage))
        except (coreException,coreDeviceException) as e:
            raise e    
        except:
            raise coreException("can't not buildDevice deviceID %s"%(deviceID))  
           
    def __loadPackage(self,devicePackage):
        try:
            classModul = importlib.import_module(devicePackage)
            LOG.info("load pakage %s"%(devicePackage))
            return classModul
        except:
            raise coreException("can't not loadPackage %s"%(devicePackage))
    
    
    def __checkIfConfigExists(self,deviceJsonName):
        try:
            if self.ifFileExists(deviceJsonName):
                return
            deviceFile={
                'channels':{}}
            self.writeJSON(deviceJsonName,deviceFile)
        except:
            raise coreException("can't not check if json config file exists or write json file")
       
    def writeDeviceConfiguration(self,objectID=None,fileNameABS=None):
        '''
        internal function to write the device configuration 
        
        fileNameABS=None    if none fileNameABS use deafult configuration
        
        if no devices in core configuration, no file written 
        '''
        if fileNameABS==None:
            raise coreDeviceException("no filename given to save device file",False)
        try:
            if objectID==None:
                objectID="device@%s"%(self.host)
            if self.ifonThisHost(objectID):
                if len(self.devices)==0:
                    LOG.info("can't write device configuration, lenght is 0")
                    return
                LOG.info("save device file %s"%(fileNameABS))
                devices={}
                for deviceID in self.getAllDeviceID():
                    devices[deviceID]=self.devices[deviceID].getConfiguration()
                self.writeJSON(fileNameABS,devices)
            else:
                forceUpdate=True
                self.updateRemoteCore(forceUpdate,objectID,'writeDeviceConfiguration',objectID,fileNameABS)
        except (coreDeviceException) as e:
            raise e
        except:
            raise coreDeviceException("can't write device configuration")
        
    def loadDeviceConfiguration(self,objectID=None,fileNameABS=None):
        '''
        internal function to load the device configuration 
        
        fileNameABS=None    
        
        exception:
        
        if none fileNameABS raise exception
        if fileNameABS file not exist rasie exception
        '''
        if fileNameABS==None:
            raise coreDeviceException("no filename given to load device file",False)
        try:
            if objectID==None:
                objectID="devices@%s"%(self.host)
            if self.ifonThisHost(objectID):
                if not self.ifFileExists(fileNameABS):
                        raise coreDeviceException("file %s not found"%(fileNameABS))
                LOG.info("load device file %s"%(fileNameABS))
                deviceCFG=self.loadJSON(fileNameABS=fileNameABS)
                if len(deviceCFG)==0:
                    LOG.info("device file is empty")
                    return
                for deviceID in deviceCFG:
                    try:
                        deviceIDCFG=deviceCFG[deviceID]
                        self.restoreDevice(deviceID,deviceIDCFG)
                    except:
                        LOG.critical("unkown error:can't restore deviceID: %s"(deviceID)) 
            else:
                forceUpdate=True
                self.updateRemoteCore(forceUpdate,objectID,'loadDeviceConfiguration',objectID,fileNameABS)
        except (coreDeviceException,coreException) as e:
            raise e
        except:
            raise coreDeviceException("can't read core configuration")      
        
    def __checkIfDeviceFileExists(self,devicefileName,deviceType,devicePackage):
        try:
            if self.ifFileExists(devicefileName):
                return
            pythonFile = open(os.path.normpath(devicefileName),"w") 
            pythonFile.write("\'\'\'\nCreated on %s\n"%(time.strftime("%d.%m.%Y")))
            pythonFile.write("@author: %s\n\n"%(__author__))
            pythonFile.write("\'\'\'\n")
            pythonFile.write("import logging\n")
            pythonFile.write("# Local application imports\n")
            pythonFile.write("from gateways.hmc.devices.masterDevice import masterDevice\n\n")
            pythonFile.write("__version__=\"%s\"\n"%(__version__))
            pythonFile.write("__author__=\"%s\"\n"%(__author__))
            pythonFile.write("__DEVICENTYPE__=\"%s\"\n"%(deviceType))
            pythonFile.write("__DEVICEPACKAGE__=\"%s\"\n"%(devicePackage))
            pythonFile.write("\n")
            pythonFile.write("LOG=logging.getLogger(__name__)\n")
            pythonFile.write("\n")
            pythonFile.write("class deviceManager(masterDevice):\n")
            pythonFile.write("    def __init__(self,deviceID,core,deviceCFG={},restore=False):\n")
            pythonFile.write("        deviceConfig=deviceCFG\n")
            pythonFile.write("        deviceConfig['device']['package']=\"%s\"\n"%(devicePackage))
            pythonFile.write("        deviceConfig['device']['type']=\"%s\"\n"%(deviceType))
            pythonFile.write("        masterDevice.__init__(self, deviceID, core, deviceConfig,restore)\n")
            pythonFile.write('        LOG.info("init device type %s finish(%s)"%(__DEVICENTYPE__,self.deviceID))')
            pythonFile.close()
            py_compile.compile(os.path.normpath(devicefileName))
        except:
            raise coreException("can't not check if device file exists")