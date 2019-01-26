'''
Created on 01.12.2018

@author: uschoen
'''


__version__='5.0'
__author__ = 'ullrich schoen'

# Standard library imports
import importlib
import threading
# Local application imports
from .hmcException import coreModuleException,coreException

# Local apllication constant

class modul():
    
    def __init__(self,*args):
        self.module={}
        self.logger.info("load core.module modul")
    
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
            if self.ifonThisHost(modulName):
                self._restoreModul(modulName, modulCFG)
            self.updateRemoteCore(forceUpdate,modulName,'restoreModul',modulName,modulCFG)
        except (coreModuleException) as e:
            raise e
        except:
            raise coreModuleException("unknown error in restoreModul")
        
    def _restoreModul(self,objectID,modulCFG):
        '''
        restore a modul, only for restart/start
        '''
        try:
            self.logger.debug("restore modul %s"%(objectID))
            if objectID in self.module:
                if self.module[objectID]['config']==modulCFG:
                    LOG.info("current module %s confiuration is equal new configuration"%(objectID))
                    return
                self._deleteModule(objectID) 
            self.__buildModul(objectID,modulCFG)
            self.__startModul(objectID)
        except coreModuleException as e:
            raise e
        except:
            raise coreModuleException("unknown error in restoreModul")
    
    def _deleteModule(self,objectID):
        '''
        delete a module
        '''
        try:
            if objectID not in self.module:
                self.logger.info("%s modul is not exists and can't delete"%(objectID))
                return
            del (self.module[objectID])
            self.logger.info("delete %s modul from core"%(objectID)) 
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
                    self.logger.error("modul %s does not exiting"%(modulName))
                    continue
                if self.ifonThisHost(modulName):
                    if modulName not in self.module:
                        self.logger.error("modul %s have no instance"%(modulName))
                        continue
                    if not self.module[modulName]['enable']:
                        self.logger.warning("modul %s is diable"%(modulName))
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
                        self.logger.error("can't start modul %s"%(modulName)) 
                else:
                    self.logger.info("modul %s not on this host %s"%(modulName,self.host)) 
        except:
            raise coreModuleException("unknown error in callModul")    
    
    def __startModulThread(self,modulName,args):
        method_to_call = getattr(self.module[modulName]['instance'], self.module[modulName]['caller'])
        method_to_call(args)
        
    def __buildModul(self,objectID,modulCFG):
        try:
            modulPackage="module.%s.%s"%(modulCFG.get('package'),modulCFG.get('modul'))
            classModul = self.__loadPackage(modulPackage)
            self.module[objectID]={
                                    'name':objectID,
                                    'status':"stop",
                                    'runnable':modulCFG.get('runnable',False),
                                    'enable':modulCFG.get('enable',False),
                                    'instance':False,
                                    'caller':modulCFG.get('caller',None),
                                    'config':modulCFG
                                    }
            if hasattr(classModul, '__version__'):
                if classModul.__version__<__version__:
                    self.logger.warning("version of %s is %s and can by to low"%(modulPackage,classModul.__version__))
                else:
                    self.logger.debug( "version of %s is %s"%(modulPackage,classModul.__version__))
            else:
                self.logger.warning("modul %s has no version Info"%(modulPackage))
            className = modulCFG.get('class')
            defaultCFG=modulCFG.get("config",{})
            defaultCFG['modulName']=objectID
            argumente=(objectID,defaultCFG,self)
            self.module[objectID]['instance']= getattr(classModul,className)(*argumente)
            if not hasattr(self.module[objectID]['instance'], self.module[objectID]['caller']):
                raise coreModuleException("modul %s has no caller %s"%(objectID,self.module[objectID]['caller']))
        except coreModuleException as e:
            raise e
        except:
            raise coreModuleException("unkown error in build modul")  
    
    def __loadPackage(self,modulPackage):
        try:
            classModul = importlib.import_module(modulPackage)
            self.logger.info("load pakage %s"%(modulPackage))
            return classModul
        except:
            raise coreModuleException("can't not __loadPackage %s"%(modulPackage)) 
    
    def __disableModul(self,objectID):
        '''
        disable module only on this host
        '''
        self.logger.info("disable modul %s"%(objectID))
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
                self.logger.info("start modul %s"%(objectID))
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
                self.logger.info("load module file %s"%(fileNameABS))
                if len(moduleCFG)==0:
                    self.logger.info("module file is empty")
                    return
                for modulName in moduleCFG:
                    try:
                        self.restoreModul(modulName,moduleCFG[modulName])
                    except:
                        self.logger.critical("unkown error:can't restore module name: %s"(modulName)) 
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
                    self.logger.info("can't write module configuration, lenght is 0")
                    return
                self.logger.info("save module file %s"%(fileNameABS))
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