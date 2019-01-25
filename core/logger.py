'''
Created on 01.12.2018

@author: uschoen
'''

__version__='5.0'
__author__ = 'ullrich schoen'

# Standard library imports
import logging.config
# Local application imports
from .hmcException import loggerCoreException,coreException

class logger():
    '''
    core events function
    '''
    def __init__(self,*args):
        self.loggerConf={}
        self.logger.info("load core.logger modul")
    
    def __applyLoggerConfiguration(self,loggerConf):
        try:
            self.logger.info("apply new logger configuration")
            logging.config.dictConfig(loggerConf)
        except:
            raise loggerCoreException("can not add logging intances") 
    
    
    def loadLoggerConfiguration(self,objectID=None,fileNameABS=None,forceUpdate=False):
        '''
        internal function to load the logger configuration 
        
        fileNameABS=None
        
        exception:
        
        if none fileNameABS raise exception
        if fileNameABS file not exist rasie exception
        '''
        try:
            if fileNameABS==None:
                raise loggerCoreException("no filename given to load core file")
            if objectID==None:
                objectID="logger@%s"%(self.host)
            if self.ifonThisHost(objectID):
                if not self.ifFileExists(fileNameABS):
                    raise loggerCoreException("file %s not found"%(fileNameABS))
                self.logger.info("load logger file %s"%(fileNameABS))
                loggerCFG=self.loadJSON(fileNameABS)
                if len(loggerCFG)==0:
                    self.logger.info("logger file is empty")
                    return
                self.__applyLoggerConfiguration(loggerCFG)
                self.loggerConf=loggerCFG
            else:
                self.updateRemoteCore(forceUpdate,objectID,'loadLoggerConfiguration',objectID,fileNameABS)
        except (loggerCoreException,coreException) as e:
            raise e
        except:
            raise loggerCoreException("can't read logging configuration")
        
    def writeLoggerConfiguration(self,objectID=None,fileNameABS=None,forceUpdate=False):
        '''
        internal function to write the logger configuration 
        
        fileNameABS=None    if none fileNameABS use deafult configuration
        
        if 0 devices in core configuration, no file written 
        '''
        try:
            if fileNameABS==None:
                raise loggerCoreException("no filename given to save logger file")
            if objectID==None:
                objectID="logger@%s"%(self.host)
            if self.ifonThisHost(objectID):
                if len(self.loggerConf)==0:
                    self.logger.info("can't write logger configuration, lenght is 0")
                    return
                self.logger.info("save logger file %s"%(fileNameABS))
                self.writeJSON(fileNameABS,self.loggerConf)
            else:
                self.updateRemoteCore(forceUpdate,objectID,'writeLoggerConfiguration',objectID,fileNameABS)        
        except (coreException) as e:
            raise e
        except:
            raise loggerCoreException("can't write logger configuration") 