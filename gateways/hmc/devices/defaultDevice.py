'''
Created on 02.12.2018
@author: ullrich schoen

'''
import logging
# Local application imports
from masterDevice import masterDevice


__version__="5.1"
__author__="ullrich schoen"
__DEVICENNAME__="ds1820"
__DEVICEPACKAGE__="hmc.devices"
LOG=logging.getLogger(__name__)

class deviceManager(masterDevice):

    def __init__(self,deviceID,core,deviceCFG={},adding=True):
        masterDevice.__init__(self, deviceID, core, deviceCFG, adding)
        self.device['type']=__DEVICENNAME__
        self.device['package']=__DEVICEPACKAGE__
        LOG.info("init device %s finish(%s)"%(__DEVICENNAME__,self.deviceID))
