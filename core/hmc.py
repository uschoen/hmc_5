'''
Created on 01.12.2018

@author: uschoen
'''
__version__ = '5.0'
__author__ = 'ullrich schoen'


# Standard library imports
import threading
import time
import logging
import os
import sys
import socket

# Local application imports
from .hmcException import coreException
from .event import event
from .configuration import configuration
from .channels import channels
from .base import base
from .remoteCore import remoteCore
from .logger import logger
from .gateways import gateways
from .device import device
from .module import modul
from .defaults import defaults

class manager(threading.Thread,base,event,configuration,remoteCore,logger,gateways,device,modul,channels,defaults):
    
    def __init__(self,configFile=None):
        threading.Thread.__init__(self) 
        '''
        global vars
        '''
        #config
        self.args={}
        # logger
        self.logger=logging.getLogger(__name__)
        
        '''
        start up
        '''
        self.path='' if not os.path.dirname(sys.argv[0]) else '%s/'%(os.path.dirname(sys.argv[0]))
        self.host=socket.gethostbyaddr(socket.gethostname())[0]
        self.logger.debug("start to init core on host %s in path %s"%(self.host,self.path))
        ''' 
            load core configuration
        '''
        defaults.__init__(self)
        self.args=self.getCoreDefaults()
        
        try:
            if not configFile == None:
                self.args.update(self.loadJSON(configFile))
        except:
            self.logger.warning("can not load config file %s, use default config"%(configFile))
        '''
            load core module
        '''
        self.logger.debug("load core.manager modul")
        # cor Module
        base.__init__(self)
        configuration.__init__(self)
        event.__init__(self)
        remoteCore.__init__(self)
        logger.__init__(self)
        gateways.__init__(self)
        device.__init__(self)
        channels.__init__(self)
        modul.__init__(self)
        
    def run(self):
        try:
            self.logger.info("startup core")
            self.onboot_event()
            while True:
                self.logger.debug("wait core 60sec")
                time.sleep(60)
        except:
            raise coreException("core have some problems")
        finally:
            self.logger.critical("stop core")
            self.shutdown()
            
    
    def shutdown(self):
        self.logger.warning("shutdown core")
        self.onshutdown_event()


if __name__ == "__main__":
    pass
    