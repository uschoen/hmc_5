'''
Created on 01.12.2018

@author: uschoen
'''


__version__='5.0'
__author__ = 'ullrich schoen'

# Standard library imports

import logging



class coreException(Exception):
    def __init__(self, msg="unkown error occured"):
        self.logger=logging.getLogger(__name__)
        super(coreException, self).__init__(msg)
        self.msg = msg
        
        self.logger.critical(msg,exc_info=True)
        
    

        
    
class coreConfigurationException(Exception):
    def __init__(self, msg="unkown error occured"):
        self.logger=logging.getLogger(__name__)
        super(coreConfigurationException, self).__init__(msg)
        self.msg = msg
        
        self.logger.critical(msg,exc_info=True)
    
class remoteCoreException(Exception):
    def __init__(self, msg="unkown error occured",tracback=True):
        self.logger=logging.getLogger(__name__)
        super(remoteCoreException, self).__init__(msg)
        self.msg = msg
        if tracback:
            self.logger.critical(msg,exc_info=True)
        else:
            self.logger.critical(msg)

class coreGatewayException(Exception):
    def __init__(self, msg="unkown error occured",tracback=True):
        self.logger=logging.getLogger(__name__)
        super(coreGatewayException, self).__init__(msg)
        self.msg = msg
        if tracback:
            self.logger.critical(msg,exc_info=True)
        else:
            self.logger.critical(msg)

class loggerCoreException(Exception):
    def __init__(self, msg="unkown error occured"):
        self.logger=logging.getLogger(__name__)
        super(loggerCoreException, self).__init__(msg)
        self.msg = msg
        
        self.logger.critical(msg,exc_info=True)
        

class gatewayException(Exception):
    def __init__(self, msg="unkown error occured",tracback=True):
        self.logger=logging.getLogger(__name__)
        super(gatewayException, self).__init__(msg)
        self.msg = msg
        if tracback:
            self.logger.critical(msg,exc_info=True)
        else:
            self.logger.critical(msg)

class coreDeviceException(Exception):
    def __init__(self, msg="unkown error occured",tracback=True):
        self.logger=logging.getLogger(__name__)
        super(coreDeviceException, self).__init__(msg)
        self.msg = msg
        
        self.logger.critical(msg,exc_info=True)
  

class coreChannelException(Exception):
    def __init__(self, msg="unkown error occured"):
        self.logger=logging.getLogger(__name__)
        super(coreChannelException, self).__init__(msg)
        self.msg = msg
        
        self.logger.critical(msg,exc_info=True)

class coreModuleException(Exception):
    def __init__(self, msg="unkown error occured"):
        self.logger=logging.getLogger(__name__)
        super(coreModuleException, self).__init__(msg)
        self.msg = msg
        self.logger.critical(msg,exc_info=True)

class cryptException(Exception):
    def __init__(self, msg="unkown error occured"):
        self.logger=logging.getLogger(__name__)
        super(cryptException, self).__init__(msg)
        self.msg = msg
        self.logger.critical(msg,exc_info=True)