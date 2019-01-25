'''
Created on 21.05.2018
@author: uschoen

'''
from gateways.hmc.devices.defaultDevice import defaultDevice

__version__="2.1"


class device(defaultDevice):
    def _name_(self):
        return "HM_LC_Sw2PBU_FM"
