'''
Created on 01.12.2018

@author: uschoen
'''

__version__='5.0'
__author__ = 'ullrich schoen'

# Standard library imports
import logging


class clientException(Exception):
    def __init__(self, msg="unkown error occured",traceback=True):
        self.logger=logging.getLogger(__name__)
        super(clientException, self).__init__(msg)
        self.msg = msg
        if traceback:
            self.logger.critical(msg,exc_info=True)
        else:
            self.logger.critical(msg)

class remoteServerException(Exception):
    def __init__(self, msg="unkown error occured",tracback=True):
        self.logger=logging.getLogger(__name__)
        super(remoteServerException, self).__init__(msg)
        self.msg = msg
        if tracback:
            self.logger.critical(msg,exc_info=True)
        else:
            self.logger.critical(msg)
            
class cryptException(Exception):
    def __init__(self, msg="unkown error occured",traceback=True):
        self.logger=logging.getLogger(__name__)
        super(cryptException, self).__init__(msg)
        self.msg = msg
        if traceback:
            self.logger.critical(msg,exc_info=True)
        else:
            self.logger.critical(msg)

class ServerException(Exception):
    def __init__(self, msg="unkown error occured",traceback=True):
        self.logger=logging.getLogger(__name__)
        super(ServerException, self).__init__(msg)
        self.msg = msg
        if traceback:
            self.logger.critical(msg,exc_info=True)
        else:
            self.logger.critical(msg)

class protokolException(Exception):
    def __init__(self, msg="unkown error occured",traceback=True):
        self.logger=logging.getLogger(__name__)
        super(protokolException, self).__init__(msg)
        self.msg = msg
        if traceback:
            self.logger.critical(msg,exc_info=True)
        else:
            self.logger.critical(msg)