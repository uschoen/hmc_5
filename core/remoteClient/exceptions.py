'''
Created on 01.12.2018

@author: uschoen
'''

__version__='5.0'
__author__ = 'ullrich schoen'

# Standard library imports
import logging

LOG=logging.getLogger(__name__)

class clientException(Exception):
    def __init__(self, msg="unkown error occured",traceback=True):
        super(clientException, self).__init__(msg)
        self.msg = msg
        if traceback:
            LOG.critical(msg,exc_info=True)
        else:
            LOG.critical(msg)

class remoteServerException(Exception):
    def __init__(self, msg="unkown error occured",tracback=True):
        super(remoteServerException, self).__init__(msg)
        self.msg = msg
        if tracback:
            LOG.critical(msg,exc_info=True)
        else:
            LOG.critical(msg)
            
class cryptException(Exception):
    def __init__(self, msg="unkown error occured",traceback=True):
        super(cryptException, self).__init__(msg)
        self.msg = msg
        if traceback:
            LOG.critical(msg,exc_info=True)
        else:
            LOG.critical(msg)

class ServerException(Exception):
    def __init__(self, msg="unkown error occured",traceback=True):
        super(ServerException, self).__init__(msg)
        self.msg = msg
        if traceback:
            LOG.critical(msg,exc_info=True)
        else:
            LOG.critical(msg)

class protokolException(Exception):
    def __init__(self, msg="unkown error occured",traceback=True):
        super(protokolException, self).__init__(msg)
        self.msg = msg
        if traceback:
            LOG.critical(msg,exc_info=True)
        else:
            LOG.critical(msg)