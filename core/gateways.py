'''
Created on 01.12.2018

@author: uschoen
'''

__version__='5.0'
__author__ = 'ullrich schoen'

# Standard library imports
import importlib
import threading
from copy import deepcopy
import logging
# Local application imports
from .hmcException import coreGatewayException,coreException

LOG=logging.getLogger(__name__)

class gateways():
    '''
    core gateway  function
  
        self.gateways:
    {
        "gatewayName":{                       # name of the gateways
                        "instance": class,    # class/object/instance of the gateway
                        "status": stop/start, # is thread running or not
                        "enable": True/False  # is gateway enable or not
                        "name": name          # name of the gateways
                     }
    }          
    '''
    def __init__(self,*args):
        
        LOG.info("load core.gateway modul")
        # gateways onjects
        self.gateways={}
        ''' running gateways '''
        self.gatewayRunning=0
    
    def getAllGatewayNames(self):
        try:
            return list(self.gateways.keys())
        except:
            raise coreGatewayException("can not getAllGatewayNames back")
        
    def stopAllGateways(self,objectID=None):
        try:
            if objectID==None:
                objectID="gateways@%s"%(self.host)
            if self.ifonThisHost(objectID):
                LOG.debug("%i gateways running"%(self.gatewayRunning))
                for gatewayName in self.getAllGatewayNames():   
                    try:
                        if not self.ifonThisHost(gatewayName):
                            continue
                        threading.Thread(target=self.stopGateway,args=(gatewayName,)).start()
                    except:
                        LOG.error("can't shutdown gateway %s"%(gatewayName))
            else:
                forceUpdate=True
                self.updateRemoteCore(forceUpdate,objectID,'stopAllGateways',objectID)
        except:
            raise coreGatewayException("can not stopAllGateway")
    
    def stopGateway(self,objectID,forceUpdate=False):
        '''
            stop a gateway
            
            gatewayInstance: the gateway instance
            raise exceptions
            '''
        if objectID not in self.gateways:
            raise coreGatewayException("gateway %s is not existing"%(objectID),False)
        try:
            self.__stopGateway(objectID)
            self.updateRemoteCore(forceUpdate,objectID,'stopGateway',objectID) 
        except (coreGatewayException) as e:
            raise e
        except:
            raise coreGatewayException("can not stop gateway %s"%(objectID),False)
        
    def __stopGateway(self,objectID):
        '''
            stop a gateway
            
            gatewayInstance: the gateway instance
            raise exceptions
            '''
        try:
            LOG.critical("shutdown gateway %s"%(objectID))
            if self.ifonThisHost(objectID):
                if self.gateways[objectID]['instance']:
                    if self.gateways[objectID]['instance'].isAlive():
                        self.gateways[objectID]['instance'].shutdown()
                        self.gateways[objectID]['instance'].join(5)
            self.gateways[objectID]['running']=False
            self.gateways[objectID]['instance']=False
            self.gatewayRunning=self.gatewayRunning-1
        except (coreGatewayException) as e:
            raise e
        except:
            raise coreGatewayException("can not stop gateway %s"%(objectID),False )
        
    def __deleteGateway(self,objectID):
        '''
        delete a gateway
        '''
        try:
            if objectID in self.gateways:
                self.__stopGateway(objectID)
                LOG.info("delete gateway %s intance"%(objectID))
                del self.gateways[objectID]
        except (coreGatewayException) as e:
            raise e
        except:
            raise coreGatewayException("can't delete gateway %s"%(objectID),False)
    
    def deleteGateway(self,objectID,forceUpdate=False):
        '''
        delete a gateway
        '''
        try:
            if objectID in self.gateways:
                self.__deleteGateway(objectID)
            self.updateRemoteCore(forceUpdate,objectID,'deleteGateway',objectID) 
        except (coreGatewayException) as e:
            raise e
        except:
            raise coreGatewayException("can't delete gateway %s"%(objectID))   
        
    def restoreGateway(self,objectID,gatewayCFG={},forceUpdate=False):
        ''' 
            restore a Gateway, the gateway name have to be unique and not exisitng,
            after restore its not update the other core server. This ist only
            a action for startup !!! 
            
            gatewayName: name of the gateway 
            config: configuration of the gateways
                {
                "enable": enable the gateway, if the gateway not enable it will not build only store in cfg file
                "package":package name of the gateways
                "modul": module name of the gateway
                "class": class of the module
                "config":configuration of the gateways class {}
                }
            
            raise exception 
        '''
        try:
            LOG.info("restore gateway %s"%(objectID))
            if objectID in self.gateways:
                if gatewayCFG==self.gateways[object]['config']:
                    LOG.info("gateway %s have the same configuration, do not restore")
                    return
                self.__deleteGateway(objectID)
            self.__buildGateway(objectID,deepcopy(gatewayCFG))
            if self.ifonThisHost(objectID):
                if self.gateways[objectID]['enable']:
                    self.__startGateway(objectID)
                else:
                    LOG.error("gateway %s is disable, can not start"%(objectID))  
            self.updateRemoteCore(forceUpdate,objectID,'restoreGateway',objectID,gatewayCFG)  
        except (coreGatewayException) as e:
            raise e  
        except:
            raise coreGatewayException("can't restore gateways %s"%(objectID),False)
        
    def __startGateway(self,objectID):
        '''
        start a gateway
        
        gatewayName=given gateway name
        
        exceptions:
        if gatewayName not exist in gatewayCFG
        if instance not exist in gateways
        if gateway not exist on this host
        if gateway disable
        
        '''
        if objectID not in self.gateways:
            raise coreGatewayException("gateways %s is not existing"%(objectID),False)
        if not self.gateways[objectID]['enable']:
            raise coreGatewayException("gateways %s is disable"%(objectID),False)   
        try:
            LOG.info("start gateway %s"%(objectID))
            if self.gateways[objectID]['instance']:
                self.gateways[objectID]['instance'].start()
            self.gateways[objectID]['running']=True
            self.gatewayRunning=self.gatewayRunning+1
        except:
            self.gateways[objectID]['running']=False
            self.disableGateway(objectID)
            raise coreGatewayException("can not start gateways %s"%(objectID),False)  
    
    def getGatewayConfiguration(self,objectID) :
        '''
        get the gateways configuration back
        exception:
                coreGatewayExecption
        '''
        if objectID not in self.gateways:
            raise coreGatewayException("gateway %s ist not exists"%(objectID))
        try:
            return self.gateways[objectID]['config']
        except (coreGatewayException) as e:
            raise e
        except:
            raise coreGatewayException("can't not read gatewayConfiguration objectID %s"%(objectID))
    
    
    def writeGatewayConfiguration(self,objectID=None,fileNameABS=None):
        '''
        internal function to write the gateway configuration 
        
        fileNameABS=None
        
        rasie exception if fileNameABS=NONE
        if 0 devices in core configuration, no file written 
        '''
        if fileNameABS==None:
            raise coreGatewayException("no filename given to save gateway file")
        try:
            if objectID==None:
                objectID="gateway@%s"%(self.host)
            if self.ifonThisHost(objectID):
                if len(self.gateways)==0:
                    LOG.info("can't write gateway configuration, lenght is 0")
                    return
                if fileNameABS==None:
                    raise coreGatewayException("no filename given to save gateway file")
                LOG.info("save gateway file %s"%(fileNameABS))
                gatewayCFG={}
                for gatewayName in self.gateways:
                    gatewayCFG[gatewayName]=self.gateways[gatewayName]['config']
                self.writeJSON(fileNameABS,gatewayCFG)
            else:
                forceUpdate=True
                self.updateRemoteCore(forceUpdate,objectID,'writeGatewayConfiguration',objectID,fileNameABS)
        except (coreGatewayException,coreException) as e:
            raise e
        except:
            raise coreGatewayException("can't write gateway configuration")
    
    def loadGatewayConfiguration(self,objectID=None,fileNameABS=None):
        '''
        internal function to load the gateway configuration 
        
        fileNameABS=None
        
        exception:
        
        if none fileNameABS raise exception
        if fileNameABS file not exist rasie exception
        '''
        if fileNameABS==None:
            raise coreGatewayException("no filename given to load core file")
        try:
            
            if objectID==None:
                objectID="gateway@%s"%(self.host)
            if self.ifonThisHost(objectID):
                if not self.ifFileExists(fileNameABS):
                    raise coreGatewayException("file %s not found"%(fileNameABS))
                LOG.info("load gateway file %s"%(fileNameABS))
                gatewaysCFG=self.loadJSON(fileNameABS)
                if len(gatewaysCFG)==0:
                    LOG.info("gateway file is empty")
                    return
                for gatewayName in gatewaysCFG:
                    try:
                        self.restoreGateway(gatewayName,gatewaysCFG[gatewayName])
                    except:
                        LOG.error("can't restore gateways %s"%(gatewayName),exc_info=True)
            else:
                forceUpdate=True
                self.updateRemoteCore(forceUpdate,objectID,'loadGatewayConfiguration',objectID,fileNameABS)
        except (coreException,coreGatewayException) as e:
            raise e
        except:
            raise coreGatewayException("can't read gateway configuration")     
          
    def disableGateway(self,objectID,forceUpdate=False):
        '''
        internal function to disable a gateway
        
        gatewayName=given gateway name
        
        exceptions:
        if gatewayName not exist in gatewayCFG
        if instance not exist gateways
        if gateway status not stop
        if gateway not on this host
        
        '''
        if objectID not in self.gateways:
            raise coreGatewayException("can't disable gateway, %s is not existing"%(objectID),False)
        if not self.gateways[objectID]['running']:
            raise coreGatewayException("can not disable gateway %s, is running"%(objectID),False)
        try:
            LOG.info("disable gateway %s"(objectID))
            self.gateways[objectID]['enable']=False
            self.gateways[objectID]['config']['enable']=False
            self.updateRemoteCore(forceUpdate,objectID,'disableGateway',objectID)      
        except:
            raise coreGatewayException("can not disable gateway %s"%(objectID))
    
    def __buildGateway(self,objectID,gatewayConfig={}):
        try:
            '''
            build a gateway
            
            gatewayName: name of the gateway 
            config: configuration of the gateways
                {
                "enable": enable the gateway, if the gateway not enable it will not build only store in cfg file
                "package":package name of the gateways
                "modul": module name of the gateway
                "class": class of the module
                "config":configuration of the gateways class
                }
                
            raise exception on failure
            '''
            if objectID in self.gateways:
                raise coreGatewayException("gateway %s exists"%(objectID))
            LOG.debug("build gateway %s"%(objectID))
            
            ''' deafult gateway configutation '''
            gatewayCFG={ 
                        "enable":False,
                        "package":"hmc",
                        "modul":"defaultGateway",
                        "class":"defaultGateway",
                        "config":{}
                        }
            gatewayCFG.update(gatewayConfig)
                       
            gatewayCFG['config']['gateway']="%s.%s" % (tuple(objectID.split("@")))  
            gatewayCFG['config']['package']=gatewayCFG['package']
            gatewayCFG['config']['name']=objectID
            gatewayCFG['config']['enable']=gatewayCFG['enable']
            gatewayCFG['config']['devicePackage']=gatewayConfig.get('config',{}).get('devicePackage',"hmc")
            gatewayCFG['config']['deviceType']=gatewayConfig.get('config',{}).get('deviceType',"defaultDevice")
            
            ''' gateway container '''
            self.gateways[objectID]={
                'config':gatewayCFG,
                'instance':False,
                'enable':gatewayCFG['enable'],
                'running':False}
            
            if self.ifonThisHost(objectID):
                try:
                    self.__buildGatewayInstance(objectID,gatewayCFG)
                except (coreGatewayException) as e:
                    raise e
        except (coreGatewayException) as e:
            raise e
        except:
            raise coreException("can not __buildGateway %s"%(objectID))
    
    def __buildGatewayInstance(self,objectID,gatewayCFG):
        try:
            package="gateways.%s.%s"%(gatewayCFG.get('package'),gatewayCFG.get('modul'))
            LOG.debug("try to bild gateway instance: %s  with package: %s"%(objectID,package))
            CLASS_NAME = gatewayCFG.get('class')
            ARGUMENTS = (gatewayCFG.get('config',{}),self)
            module = importlib.import_module(package)
            self.checkModulVersion(package,module)
            self.gateways[objectID]['instance'] = getattr(module, CLASS_NAME)(*ARGUMENTS)
            self.gateways[objectID]['instance'].daemon = True 
        except:
            self.gateways[objectID]['enable']=False
            raise coreGatewayException("can't build gateway instance %s"(objectID))