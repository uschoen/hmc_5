'''
Created on 18.12.2018
@author: ullrich schoen

'''
# Local application imports
from gateways.hmc.devices.masterDevice import masterDevice

__version__="5.0"
__author__="ullrich schoen"
__DEVICENTYPE__="ds1820"
__DEVICEPACKAGE__="raspberry.onewire"

class deviceManager(masterDevice):
    def __init__(self,deviceID,core,deviceCFG={},restore=False):
        deviceConfig=deviceCFG
        deviceConfig['device']['package']="raspberry.onewire"
        deviceConfig['device']['type']="ds1820"
        masterDevice.__init__(self, deviceID, core, deviceConfig,restore)
        self.logger.info("init device type %s finish(%s)"%(__DEVICENTYPE__,self.deviceID))