'''
Created on 01.12.2018

@author: uschoen
'''

__version__='5.0'
__author__ = 'ullrich schoen'

# Standard library imports
import json 
import traceback
import logging

def convertTraceBack(traceBackList):
    lines=[]
    for line in traceBackList:
        lines.append(line.strip())
    return lines

def buildJsonError(msg,traceBack,excType):  
    error={
            'result':{
                'result':"error",
                'type':excType,
                'msg':msg,
                'traceback':traceBack
            }}
    return json.dumps(error)  

class deviceException(Exception):
    def __init__(self, msg="unkown error occured"):
        self.logger=logging.getLogger(__name__)
        super(deviceException, self).__init__(msg)
        self.msg = msg
        self.traceBack= convertTraceBack(traceback.format_exc().splitlines())
        self.logger.critical(msg,exc_info=True)
        
    def getJsonResult(self):
        return buildJsonError(self.msg, self.traceBack,'deviceException')

class deviceChannelException(Exception):
    def __init__(self, msg="unkown error occured"):
        self.logger=logging.getLogger(__name__)
        super(deviceChannelException, self).__init__(msg)
        self.msg = msg
        self.traceBack= convertTraceBack(traceback.format_exc().splitlines())
        self.logger.critical(msg,exc_info=True)
        
    def getJsonResult(self):
        return buildJsonError(self.msg, self.traceBack,'deviceChannelException')

class deviceParameterException(Exception):
    def __init__(self, msg="unkown error occured"):
        self.logger=logging.getLogger(__name__)
        super(deviceParameterException, self).__init__(msg)
        self.msg = msg
        self.traceBack= convertTraceBack(traceback.format_exc().splitlines())
        self.logger.critical(msg,exc_info=True)
        
    def getJsonResult(self):
        return buildJsonError(self.msg, self.traceBack,'deviceParameterException')
    
class deviceEventException(Exception):
    def __init__(self, msg="unkown error occured"):
        self.logger=logging.getLogger(__name__)
        super(deviceEventException, self).__init__(msg)
        self.msg = msg
        self.traceBack= convertTraceBack(traceback.format_exc().splitlines())
        self.logger.critical(msg,exc_info=True)
        
    def getJsonResult(self):
        return buildJsonError(self.msg, self.traceBack,'deviceEventException')

class deviceConfigurationException(Exception):
    def __init__(self, msg="unkown error occured"):
        self.logger=logging.getLogger(__name__)
        super(deviceConfigurationException, self).__init__(msg)
        self.msg = msg
        self.traceBack= convertTraceBack(traceback.format_exc().splitlines())
        self.logger.critical(msg,exc_info=True)
        
    def getJsonResult(self):
        return buildJsonError(self.msg, self.traceBack,'deviceConfigurationException')
    