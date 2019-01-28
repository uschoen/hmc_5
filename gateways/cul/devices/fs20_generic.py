'''
Created on 28.01.2019
@author: ullrich schoen

'''

# Standard library imports
import logging
# Local application imports
from gateways.hmc.devices.masterDevice import masterDevice

__version__="5.1"
__author__="ullrich schoen"
__DEVICENTYPE__="fs20_generic"
__DEVICEPACKAGE__="cul"

LOG=logging.getLogger(__name__)

class deviceManager(masterDevice):
    def __init__(self,deviceID,core,deviceCFG={},restore=False):
        deviceConfig=deviceCFG
        deviceConfig['devicePackage']=__DEVICEPACKAGE__
        deviceConfig['deviceType']=__DEVICENTYPE__
        masterDevice.__init__(self, deviceID, core, deviceConfig,restore)
        LOG.info("init deviceID:%s type:%s version:%s"%(self.deviceID,__DEVICENTYPE__,__version__))