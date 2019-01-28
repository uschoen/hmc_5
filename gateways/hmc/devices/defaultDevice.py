'''
Created on 02.12.2018
@author: ullrich schoen

'''
import logging
# Local application imports
from masterDevice import masterDevice


__version__="5.1"
__author__="ullrich schoen"
__DEVICEPACKAGE__="hmc.devices"
__DEVICENTYPE__="defaultDevice"

LOG=logging.getLogger(__name__)

class deviceManager(masterDevice):

    def __init__(self,deviceID,core,deviceCFG={},restore=False):
        deviceConfig=deviceCFG
        deviceConfig['devicePackage']=__DEVICEPACKAGE__
        deviceConfig['deviceType']=__DEVICENTYPE__
        masterDevice.__init__(self, deviceID, core, deviceConfig, restore)
        LOG.info("init deviceID:%s type:%s version:%s"%(self.deviceID,__DEVICENTYPE__,__version__))
