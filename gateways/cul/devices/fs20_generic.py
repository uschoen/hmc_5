'''
Created on 27.01.2019
@author: ullrich schoen

'''
import logging
# Local application imports
from gateways.hmc.devices.masterDevice import masterDevice

__version__="5.0"
__author__="ullrich schoen"
__DEVICENTYPE__="fs20_generic"
__DEVICEPACKAGE__="cul"

LOG=logging.getLogger(__name__)

class deviceManager(masterDevice):
    def __init__(self,deviceID,core,deviceCFG={},restore=False):
        deviceConfig=deviceCFG
        deviceConfig['device']['package']="cul"
        deviceConfig['device']['type']="fs20_generic"
        masterDevice.__init__(self, deviceID, core, deviceConfig,restore)
        LOG.info("init device type %s finish(%s)"%(__DEVICENTYPE__,self.deviceID))