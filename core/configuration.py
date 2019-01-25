'''
Created on 01.12.2018

@author: uschoen
'''

__version__='5.0'
__author__ = 'ullrich schoen'

# Standard library imports

# Local application imports
from .hmcException import coreException,coreConfigurationException

class configuration():
    '''
    core events function
    '''
    def __init__(self,*args):
        self.logger.info("load core.configuration modul")
    
    def loadAllSystemConfiguration(self,objectID=None):
        '''
        load all configuration files
        '''
        try:
            if objectID==None:
                objectID="conf@%s"%(self.host)
            if self.ifonThisHost(objectID):
                '''
                load configuration for this host
                '''
                path=self.__getConfigurationPath()
                '''
                core
                '''
                try:
                    objectID="core@%s"%(self.host)
                    fileNameABS="%s/%s"%(path,self.args['configuration']['files']['core'])
                    if not self.ifFileExists(fileNameABS):
                        if not self.ifPathExists(path):
                            self.makeDir(path)
                        self.writeJSON(fileNameABS,self.getCoreDefaults())
                    self.loadCoreFile(objectID,fileNameABS)
                except:
                    self.logger.error("can't load core file %s"%(fileNameABS),exc_info=True)
                '''
                logger
                '''
                try:
                    objectID="logger@%s"%(self.host)
                    fileNameABS="%s/%s"%(path,self.args['configuration']['files']['logger'])
                    if not self.ifFileExists(fileNameABS):
                        if not self.ifPathExists(path):
                            self.makeDir(path)
                        self.writeJSON(fileNameABS,self.getLoggerDefaults())
                    self.loadLoggerConfiguration(objectID,fileNameABS)
                except:
                    self.logger.error("can't load logger file %s"%(fileNameABS),exc_info=True)
                '''
                remoteCore
                '''
                try:
                    objectID="remoteCore@%s"%(self.host)
                    fileNameABS="%s/%s"%(path,self.args['configuration']['files']['remoteCore'])
                    if not self.ifFileExists(fileNameABS):
                        if not self.ifPathExists(path):
                            self.makeDir(path)
                        self.writeJSON(fileNameABS)
                    self.loadRemoteCoreConfiguration(objectID,fileNameABS)
                except:
                    self.logger.error("can't load remote core file %s"%(fileNameABS),exc_info=True)
                '''
                module
                '''
                try:
                    objectID="module@%s"%(self.host)
                    fileNameABS="%s/%s"%(path,self.args['configuration']['files']['module'])
                    if not self.ifFileExists(fileNameABS):
                        if not self.ifPathExists(path):
                            self.makeDir(path)
                        self.writeJSON(fileNameABS)
                    self.loadModuleConfiguration(objectID,fileNameABS)
                except:
                    self.logger.error("can't load module file %s"%(fileNameABS))
                '''
                devices
                '''
                try:
                    objectID="devices@%s"%(self.host)
                    fileNameABS="%s/%s"%(path,self.args['configuration']['files']['devices'])
                    if not self.ifFileExists(fileNameABS):
                        if not self.ifPathExists(path):
                            self.makeDir(path)
                        self.writeJSON(fileNameABS,{})
                    self.loadDeviceConfiguration(objectID,fileNameABS)
                except:
                    self.logger.error("can't load device file %s"%(fileNameABS),exc_info=True)
                '''
                gateway
                '''
                try:
                    objectID="gateways@%s"%(self.host)
                    fileNameABS="%s/%s"%(path,self.args['configuration']['files']['gateways'])
                    if not self.ifFileExists(fileNameABS):
                        if not self.ifPathExists(path):
                            self.makeDir(path)
                        self.writeJSON(fileNameABS)
                    self.loadGatewayConfiguration(objectID,fileNameABS)
                except:
                    self.logger.error("can't load gateway file %s"%(fileNameABS))
            else:
                forceUpdate=True
                self.updateRemoteCore(forceUpdate,objectID,'loadAllSystemConfiguration',objectID) 
        except (coreConfigurationException,coreException) as e:
            raise e
        except:
            raise coreConfigurationException("can't exc loadAllSystemConfiguration")
    
    def loadCoreFile(self,objectID=None,fileNameABS=None):
        '''
        internal function to load the cor configuration 
        
        fileNameABS=None    
        
        exception:
        
        if none fileNameABS raise exception
        if fileNameABS file not exist rasie exception
        '''
        if fileNameABS==None:
            raise coreConfigurationException("no filename given to load core file")
        try:
            if objectID==None:
                objectID="core@%s"%(self.host)
            if self.ifonThisHost(objectID):
                if not self.ifFileExists(fileNameABS):
                    raise coreConfigurationException("file %s not found to load core files"%(fileNameABS))
                self.logger.info("load core file %s"%(fileNameABS))
                coreCFG=self.loadJSON(fileNameABS=fileNameABS)
                if len(coreCFG)==0:
                    self.logger.info("core file is empty")
                    return
                self.args=coreCFG
            else:
                forceUpdate=True
                self.updateRemoteCore(forceUpdate,objectID,'loadCoreFile',objectID,fileNameABS) 
        except (coreConfigurationException,coreException) as e:
            raise e
        except:
            raise coreConfigurationException("can't read core configuration") 
    
     
    
    def saveAllSystemConfiguration(self,objectID=None):
        '''
        load all configuration files
        '''
        try:
            if objectID==None:
                objectID="conf@%s"%(self.host)
            if self.ifonThisHost(objectID):
                '''
                load configuration for this host
                '''
                path=self.__getConfigurationPath()
                '''
                core
                '''
                try:
                    objectID="core@%s"%(self.host)
                    fileNameABS="%s/%s"%(path,self.args['configuration']['files']['core'])
                    if not self.ifPathExists(path):
                        self.makeDir(path)
                    self.writeCoreFile(objectID,fileNameABS)
                except:
                    self.logger.error("can't save core file %s"%(fileNameABS),exc_info=True)
                '''
                logger
                '''
                try:   
                    objectID="logger@%s"%(self.host)
                    fileNameABS="%s/%s"%(path,self.args['configuration']['files']['logger'])
                    if not self.ifPathExists(path):
                        self.makeDir(path)
                    self.writeLoggerConfiguration(objectID,fileNameABS)
                except:
                    self.logger.error("can't save logger file %s"%(fileNameABS),exc_info=True)
                '''
                gateways
                '''
                try:   
                    objectID="gateways@%s"%(self.host)
                    fileNameABS="%s/%s"%(path,self.args['configuration']['files']['gateways'])
                    if not self.ifPathExists(path):
                        self.makeDir(path)
                    self.writeGatewayConfiguration(objectID,fileNameABS)
                except:
                    self.logger.error("can't save gateway file %s"%(fileNameABS),exc_info=True)
                '''
                devices
                '''
                try:   
                    objectID="devices@%s"%(self.host)
                    fileNameABS="%s/%s"%(path,self.args['configuration']['files']['devices'])
                    if not self.ifPathExists(path):
                        self.makeDir(path)
                    self.writeDeviceConfiguration(objectID,fileNameABS)
                except:
                    self.logger.error("can't save device file %s"%(fileNameABS),exc_info=True)
                '''
                module
                '''
                try:   
                    objectID="module@%s"%(self.host)
                    fileNameABS="%s/%s"%(path,self.args['configuration']['files']['module'])
                    if not self.ifPathExists(path):
                        self.makeDir(path)
                    self.writeModuleConfiguration(objectID,fileNameABS)
                except:
                    self.logger.error("can't save module file %s"%(fileNameABS),exc_info=True)
                '''
                remoteCore
                '''
                try: 
                    objectID="remoteCore@%s"%(self.host)  
                    fileNameABS="%s/%s"%(path,self.args['configuration']['files']['remoteCore'])
                    if not self.ifPathExists(path):
                        self.makeDir(path)
                    self._writeRemoteCoreConfiguration(fileNameABS)
                except:
                    self.logger.error("can't save remote core file %s"%(fileNameABS),exc_info=True)    
            else:
                forceUpdate=True
                self.updateRemoteCore(forceUpdate,objectID,'saveAllSystemConfiguration',objectID) 
        except (coreConfigurationException,coreException) as e:
            raise e
        except:
            raise coreConfigurationException("can't exc saveAllSystemConfiguration") 
                   
    def writeCoreFile(self,objectID=None,fileNameABS=None):
        '''
        internal function to write the device configuration 
        
        fileNameABS=None    if none fileNameABS use deafult configuration
        
        if 0 devices in core configuration, no file written 
        '''
        if fileNameABS==None:
            raise coreConfigurationException("no filename given to save core file")
        try:
            if len(self.args)==0:
                self.logger.info("can't write core configuration, lenght is 0")
                return
            if objectID==None:
                objectID="core@%s"%(self.host)
            if self.ifonThisHost(objectID):
                self.logger.info("save core file %s"%(fileNameABS))
                self.writeJSON(fileNameABS,self.args)
            else:
                forceUpdate=True
                self.updateRemoteCore(forceUpdate,objectID,'writeCoreFile',objectID,fileNameABS) 
        except (coreException) as e:
            raise e
        except:
            raise coreConfigurationException("can't write core configuration")
      
    
    def __getConfigurationPath(self):
        try:
            path="%s%s/%s"%(self.path,self.args['configuration']['basePath'],self.args['configuration']['filePath'])
            return path
        except:
            raise coreConfigurationException("can't return configuration path")  