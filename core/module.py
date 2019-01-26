'''
Created on 01.12.2018

@author: uschoen
'''


__version__='5.0'
__author__ = 'ullrich schoen'

# Standard library imports
import importlib
import threading
import logging
# Local application imports
from .hmcException import coreModuleException,coreException

# Local apllication constant
LOG=logging.getLogger(__name__)


class modul():
    
    def __init__(self,*args):
        self.module={}
        LOG.info("load core.module modul")
    
    def getModulConfiguration(self,objectID) :
        '''
        get the gateways configuration back
        exception:
                coreGatewayExecption
        '''
        if objectID not in self.module:
            raise coreModuleException("gateway %s ist not exists"%(objectID))
        try:
            return self.module[objectID]['config']
        except (coreModuleException) as e:
            raise e
        except:
            raise coreModuleException("can't not read modulConfiguration objectID %s"%(objectID))
        
    def getAllModulNames(self):
        try:
            return list(self.module.keys())
        except:
            raise coreModuleException("can not getAllModulNames back")
    
    def restoreModul(self,modulName,modulCFG,forceUpdate=False):
        '''
        restore a modul, only for restart/start
        '''
        try:
            self.__restoreModul(modulName, modulCFG)
            self.updateRemoteCore(forceUpdate,modulName,'restoreModul',modulName,modulCFG)
        except (coreModuleException) as e:
            raise e
        except:
            raise coreModuleException("unknown error in restoreModul")
        
    def __restoreModul(self,objectID,modulCFG):
        '''
        restore a modul, only for restart/start
        '''
        try:
            LOG.debug("restore modul %s"%(objectID))
            if objectID in self.module:
                if self.module[objectID]['config']==modulCFG:
                    LOG.info("current module %s confiuration is equal new configuration"%(objectID))
                    return
                self.__deleteModule(objectID) 
            self.__buildModul(objectID,modulCFG)
            self.__startModul(objectID)
        except (coreModuleException) as e:
            raise e
        except:
            raise coreModuleException("unknown error in restoreModul")
    
    def __deleteModule(self,objectID):
        '''
        delete a module
        '''
        try:
            if objectID not in self.module:
                LOG.info("%s modul is not exists and can't delete"%(objectID))
                return
            del (self.module[objectID])
            LOG.info("delete %s modul from core"%(objectID)) 
        except:
            raise coreModuleException("unknown error in deleteModul")
    
    def callModul(self,modulList,args,forecUpdate=False):
        '''
        call module on this host
        if modul not on this host it will be ignored
        '''
        
        try:
            for modulName in modulList:
                if modulName not in self.module:
                    LOG.error("modul %s does not exiting"%(modulName))
                    continue
                if self.ifonThisHost(modulName):
                    if modulName not in self.module:
                        LOG.error("modul %s have no instance"%(modulName))
                        continue
                    if not self.module[modulName]['enable']:
                        LOG.warning("modul %s is diable"%(modulName))
                        continue
                    try:
                        deviceData={
                            'deviceID':None,
                            'channelName':None,
                            'eventTyp':None,
                            'modulName':modulName}
                        deviceData.update(args)
                        threading.Thread(target=self.__startModulThread,args = (modulName,deviceData)).start()
                    except:
                        LOG.error("can't start modul %s"%(modulName)) 
                else:
                    LOG.info("modul %s not on this host %s"%(modulName,self.host)) 
        except:
            raise coreModuleException("unknown error in callModul")    
    
    def __startModulThread(self,modulName,args):
        method_to_call = getattr(self.module[modulName]['instance'], self.module[modulName]['caller'])
        method_to_call(args)
        
    def __buildModul(self,objectID,modulCFG):
        if objectID in self.module:
            raise coreModuleException("gateway %s exists"%(objectID))
        try:
            LOG.info("build modul %s"%(objectID))
            defaultModulCFG={ 
                        "enable":False,
                        "package":"unkown",
                        "modul":"unkown",
                        "class":"unkown",
                        "config":{}
                        }
            defaultModulCFG.update(modulCFG)
            self.module[objectID]={
                                    'name':objectID,
                                    'status':"stop",
                                    'runnable':defaultModulCFG.get('runnable',False),
                                    'enable':defaultModulCFG.get('enable',False),
                                    'instance':False,
                                    'caller':defaultModulCFG.get('caller'),
                                    'config':defaultModulCFG
                                    }
            if self.ifonThisHost(objectID):
                try:
                    self.__buildModulInstance(objectID,defaultModulCFG)
                except (coreModuleException) as e:
                    raise e
        except (coreModuleException) as e:
            self.module[objectID]['instance']=False
            self.module[objectID]['enable']=False
            raise e
        except:
            self.module[objectID]['instance']=False
            self.module[objectID]['enable']=False
            raise coreModuleException("unkown error in build modul")  
    
    def __buildModulInstance(self,objectID,modulCFG):
        try:
            package="module.%s.%s"%(modulCFG.get('package'),modulCFG.get('modul'))
            CLASS_NAME = modulCFG.get('class')
            self.logger.debug("try to bild gateway instance: %s  with package: %s"%(objectID,package))
            ARGUMENTS = (objectID,modulCFG.get('config',{}),self)
            module = importlib.import_module(package)
            self.checkModulVersion(package,module)
            self.module[objectID]['instance'] = getattr(module, CLASS_NAME)(*ARGUMENTS)
            self.module[objectID]['instance'].daemon = True 
            if not hasattr(self.module[objectID]['instance'],modulCFG.get('caller')):
                raise coreModuleException("modul %s has no caller %s"%(objectID,modulCFG.get('caller')),False)
        except (coreModuleException) as e:
            raise e        
        except:
            self.module[objectID]['enable']=False
            raise coreModuleException("can't build gateway instance %s"(objectID))
    
    def __disableModul(self,objectID):
        '''
        disable module only on this host
        '''
        LOG.info("disable modul %s"%(objectID))
        if objectID not in self.module:
            raise coreModuleException("modul %s is not existing"%(objectID))
        self.module[objectID]['enable']=False
    
    def __startModul(self,objectID):
        '''
        start only module on this host
        '''
        if objectID not in self.module:
            raise coreModuleException("modul %s is not existing"%(objectID))
        if not self.module[objectID]['enable']:
            raise coreModuleException("module %s is not enable"%(objectID)) 
        try:
            if  not self.module[objectID]['runnable']:
                return
            try:
                LOG.info("start modul %s"%(objectID))
                self.module[objectID]['instance'].start()
                self.module[objectID]['status']="start"
            except:
                self.module[objectID]['status']="stop"
                self.__disableModul(objectID)
                raise coreModuleException("can not start modul %s"%(objectID))
        except coreModuleException as e:
            raise e
        except:
            raise coreModuleException("unknown error in __addProgram")
        
    def loadModuleConfiguration(self,objectID=None,fileNameABS=None,forcedUpdate=False):
        '''
        internal function to load the Module configuration 
        
        fileNameABS=None    
        
        exception:
        
        if none fileNameABS raise exception
        if fileNameABS file not exist rasie exception
        '''
        try:
            if fileNameABS==None:
                raise coreModuleException("no filename given to load module file")
            if objectID==None:
                objectID="module@%s"%(self.host)
            if self.ifonThisHost(objectID):
                if not self.ifFileExists(fileNameABS):
                    raise coreModuleException("file %s not found"%(fileNameABS))
                moduleCFG=self.loadJSON(fileNameABS=fileNameABS)
                LOG.info("load module file %s"%(fileNameABS))
                if len(moduleCFG)==0:
                    LOG.info("module file is empty")
                    return
                for modulName in moduleCFG:
                    try:
                        self.restoreModul(modulName,moduleCFG[modulName])
                    except:
                        LOG.critical("unkown error:can't restore module name: %s"(modulName)) 
            else:
                self.updateRemoteCore(forcedUpdate,objectID,'loadModuleConfiguration',objectID,fileNameABS) 
        except (coreModuleException,coreException) as e:
            raise e
        except:
            raise coreModuleException("can't read core configuration")
        
    def writeModuleConfiguration(self,objectID=None,fileNameABS=None,forceUpdate=False):
        '''
        internal function to write the module configuration 
        
        fileNameABS=None    if none fileNameABS use deafult configuration
        
        if 0 module in core configuration, no file written 
        '''
        if fileNameABS==None:
            raise coreModuleException("no filename given to save module file")    
        try:
            if objectID==None:
                objectID="module@%s"%(self.host)
            if self.ifonThisHost(objectID):
                if len(self.module)==0:
                    LOG.info("can't write module configuration, lenght is 0")
                    return
                LOG.info("save module file %s"%(fileNameABS))
                moduleCFG={}
                for modulName in self.module:
                    moduleCFG[modulName]=self.module[modulName]['config']
                self.writeJSON(fileNameABS,moduleCFG)
            else:
                self.updateRemoteCore(forceUpdate,objectID,'writeModuleConfiguration',objectID,fileNameABS)     
        except (coreException,coreModuleException) as e:
            raise e
        except:
            raise coreModuleException("can't write module configuration")