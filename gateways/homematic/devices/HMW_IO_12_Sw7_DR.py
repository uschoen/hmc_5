'''
Created on 19.01.2019
@author: ullrich schoen

'''
# Local application imports
from gateways.hmc.devices.masterDevice import masterDevice

__version__="5.0"
__author__="ullrich schoen"
__DEVICENTYPE__="HMW_IO_12_Sw7_DR"
__DEVICEPACKAGE__="homematic"

class deviceManager(masterDevice):
    def __init__(self,deviceID,core,deviceCFG={},restore=False):
        deviceConfig=deviceCFG
        deviceConfig['device']['package']="homematic"
        deviceConfig['device']['type']="HMW_IO_12_Sw7_DR"
        masterDevice.__init__(self, deviceID, core, deviceConfig,restore)
        self.logger.info("init device type %s finish(%s)"%(__DEVICENTYPE__,self.deviceID))