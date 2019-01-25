'''
Created on 01.12.2018

@author: uschoen
'''

__version__='5.0'
__author__ = 'ullrich schoen'

# Standard library imports
import time

# Local application imports
from .hmcException import coreException

class event():
    '''
    core events function
    '''
    def __init__(self,*args):
        self.logger.info("load core.event modul")

    def onboot_event(self):
        '''
        call function onboot event
        '''
        try:
            self.loadAllSystemConfiguration()
        except:
            raise coreException("can't load system configuration")
        
    def onshutdown_event(self):
        '''
        call function onshutdown events
        '''
        try:
            self.stopAllRemoteCoreClients()
            self.stopAllGateways()
            timer=int(time.time())+5
            self.saveAllSystemConfiguration()
            while timer>time.time():
                self.logger.debug("wait a moment to close all threads")
                if self.gatewayRunning==0:
                    break
                time.sleep(1)
        except:
            self.logger.error("some error in shutdown process")