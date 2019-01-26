'''
Created on 09.01.2018
@author: uschoen

'''
from gateways.hmc.devices.defaultDevice import defaultDevice

__version__="3.0"


class device(defaultDevice):
    def _name_(self):
        return "HM_RC_4_2"
