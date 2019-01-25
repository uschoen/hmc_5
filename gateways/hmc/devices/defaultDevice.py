'''
Created on 02.12.2018
@author: ullrich schoen

'''
# Local application imports
from masterDevice import masterDevice

__version__="5.0"
__author__="ullrich schoen"
__DEVICENNAME__="ds1820"
__DEVICEPACKAGE__="hmc.devices"

class deviceManager(masterDevice):

    def __init__(self,deviceID,core,deviceCFG={},adding=True):
        masterDevice.__init__(self, deviceID, core, deviceCFG, adding)
        self.device['type']=__DEVICENNAME__
        self.device['package']=__DEVICEPACKAGE__
        self.logger.info("init device %s finish(%s)"%(__DEVICENNAME__,self.deviceID))
