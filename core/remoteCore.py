'''
Created on 01.12.2018

@author: uschoen
'''

__version__='5.0'
__author__ = 'ullrich schoen'

# Standard library imports
import copy
import logging

# Local application imports
from .hmcException import remoteCoreException,coreException
from .remoteClient.client import coreClient
from .remoteClient.server import coreServer

LOG=logging.getLogger(__name__)

class remoteCore():
    '''
    core events function
    '''
    def __init__(self,*args):
        self.coreClients={}
        
        LOG.info("load core.remoteCore modul")
    
    def restoreCoreClient(self,objectID,coreCFG,syncStatus=False,forceUpdate=False):
        '''
        add a core connector as server or client
        corename=the corename of the client (name@hostname)
        args:{
                    "hostName":"raspberry1",
                    "enable":true,
                    "user":"user1",
                    "password":"password12345",
                    "ip":"127.0.0.1",
                    "port":5090,
                    "timeout":50}
        syncStatus true/false if true it set the status to the core to is sync
        '''
        try:
            self.__restoreCoreClient(objectID, coreCFG, syncStatus)
            self.updateRemoteCore(forceUpdate,objectID,'restoreCoreClient',objectID,coreCFG,syncStatus)
        except:
            raise remoteCoreException("can not restore core sync server %s"%(objectID))
        
    def __restoreCoreClient(self,objectID,coreCFG,syncStatus=False):
        '''
        add a core connector as server or client
        corename=the corename of the client (name@hostname)
        args:{
                    "hostName":"raspberry1",
                    "enable":true,
                    "user":"user1",
                    "password":"password12345",
                    "ip":"127.0.0.1",
                    "port":5090,
                    "timeout":50}
        syncStatus true/false if true it set the status to the core to is sync
        '''
        try:
            if objectID in self.coreClients:
                if self.coreClients[objectID]['config']==coreCFG:
                    LOG.info("current remote core %s confiuration is equal new configuration"%(object))
                    return
                self.__stopRemoteCoreClient(objectID)
                self.__deleteRemoteCoreClient(objectID)
            self.__buildCoreClient(objectID,coreCFG,syncStatus)
            try:
                self.__startRemoteCoreClient(objectID)
            except (remoteCoreException) as e:
                LOG.error("can't start %s: %s"%(objectID,e.msg))
            except:
                LOG.error("can't start %s: unkown error"%(objectID), exc_info=True)
        except:
            raise remoteCoreException("can not restore remote core server %s"%(objectID))
    
    def __deleteRemoteCoreClient(self,objectID):
        try:
            LOG.info("delete remote core client %s"%(objectID))
            if objectID in self.coreClients:
                self.__stopRemoteCoreClient(objectID)
                del self.coreClients[objectID]
        except:
            raise remoteCoreException("can't delete remote core %s"%(objectID))
        
    def stopRemoteCoreClient(self,objectID,forceUpdate=False):
        if not objectID in self.coreClients:
            raise remoteCoreException("remote core %s not exists"%(objectID))
        try:
            self.__stopRemoteCoreClient(objectID)
            self.updateRemoteCore(forceUpdate,objectID,'stopRemoteCoreClient',objectID)
        except:
            raise coreException("can not stop remote core %s"%(objectID))
    
    def __stopRemoteCoreClient(self,objectID):
        try:
            LOG.info("stop remote core client %s"%(objectID))
            self.coreClients[objectID]['instance'].shutdown() 
            self.coreClients[objectID]['running']=False
        except:
            raise remoteCoreException("can not stop remote core %s"%(objectID))
    
    def stopAllRemoteCoreClients(self,objectID=None,forceUpdate=False):
        try:
            if objectID==None:
                objectID="remoteClients@%s"%(self.host)
            if self.ifonThisHost(objectID):
                LOG.info("stop all remote clients on host %s"%(self.host))
                for coreName in self.coreClients:
                    try:
                        self.__stopRemoteCoreClient(coreName)
                    except:
                        LOG.error("can't stop remote core client %s"%(coreName))
            else:
                self.updateRemoteCore(forceUpdate,objectID,'stopAllRemoteCoreClients',objectID)
        except:
            raise coreException("can't stop all remote clients")   
    
    def startRemoteCoreClient(self,objectID,forceUpdate=False):
        if not objectID in self.coreClients:
            raise remoteCoreException("remote core %s not exists"%(objectID))
        if not  self.coreClients[objectID]['enable']:
            raise remoteCoreException("remote core client %s is disable, can't not start"%(objectID))
        try:
            self.__startRemoteCoreClient(objectID)
            self.updateRemoteCore(forceUpdate,objectID,'startRemoteCoreClient',objectID)
        except:
            raise coreException("can not start remote core %s"%(objectID))
        
    def __startRemoteCoreClient(self,objectID):
        try:
            if not self.coreClients[objectID]['enable']:
                LOG.error("can not start remote core %s, is disable"%(objectID))
                return
            LOG.info("start remote core client %s"%(objectID))
            self.coreClients[objectID]['instance'].start() 
            self.coreClients[objectID]['running']=True
        except:
            raise remoteCoreException("can not start remote core %s"%(objectID))
            
    def loadRemoteCoreConfiguration(self,objectID=None,fileNameABS=None,forcedUpdate=False):
        '''
        load the remote core configuaion to a file
        '''
        if fileNameABS==None:
            raise remoteCoreException("no file name given to loadCoreConfiguration")
        if not self.ifFileExists(fileNameABS):
            raise remoteCoreException("file %s not found"%(fileNameABS))
        try:
            if objectID==None:
                objectID="remoteCore@%s"%(self.host)
            if self.ifonThisHost(objectID):
                self._loadRemoteCoreConfiguration(fileNameABS)
            else:
                self.updateRemoteCore(forcedUpdate,objectID,'loadRemoteCoreConfiguration',objectID,fileNameABS) 
        except (coreException,remoteCoreException) as e:
            raise e
        except:
            raise remoteCoreException("can't loadRemoteCore Configuration")

    def _loadRemoteCoreConfiguration(self,fileNameABS=None):
        '''
        load the remote core configuaion to a file
        '''
        if fileNameABS==None:
            raise remoteCoreException("no file name given to loadCoreConfiguration")
        if not self.ifFileExists(fileNameABS):
            raise remoteCoreException("file %s not found"%(fileNameABS))
        try:
            remoteCoreCFG=self.loadJSON(fileNameABS)
            if len(remoteCoreCFG)==0:
                LOG.info("remote core file is empty")
                return
            LOG.debug("load remote core file %s"%(fileNameABS))
            for coreName in remoteCoreCFG:
                try:
                    self.__restoreCoreClient(coreName, remoteCoreCFG[coreName])
                except:
                    LOG.error("can't restore remote core %s"%(coreName),exc_info=True)
        except (coreException,remoteCoreException) as e:
            raise e
        except:
            raise remoteCoreException("can't loadRemoteCore Configuration")
        
    def writeRemoteCoreConfiguration(self,objectID=None,fileNameABS=None,forceUpdate=False):
        '''
        write the remote core configuaion to a file
        '''
        if fileNameABS==None:
            raise remoteCoreException("no file name given to writeCoreConfiguration")
        try:
            if objectID==None:
                objectID="remoteCore@%s"%(self.host)
            if self.ifonThisHost(objectID):
                self._writeRemoteCoreConfiguration(fileNameABS)
            else:
                self.updateRemoteCore(forceUpdate,objectID,'writeRemoteCoreConfiguration',objectID,fileNameABS) 
        except (coreException) as e:
            raise e
        except:
            raise remoteCoreException("can't writeRemoteCore Configuration")
    
    def _writeRemoteCoreConfiguration(self,fileNameABS=None):
        '''
        write the remote core configuaion to a file
        '''
        if fileNameABS==None:
            raise remoteCoreException("no file name given to writeCoreConfiguration")
        try:
            if len(self.coreClients)==0:
                LOG.info("can't save remote core files lenght is 0")
                return
            LOG.info("save remote core files")
            remoteCoreCFG={}
            for coreNames in self.coreClients:
                remoteCoreCFG[coreNames]=self.coreClients[coreNames]['config']
            self.writeJSON(fileNameABS,remoteCoreCFG) 
        except (coreException) as e:
            raise e
        except:
            raise remoteCoreException("can't writeRemoteCore Configuration")
    
    def updateRemoteCore(self,forceUpdate,objectID,calling,*args):
        logpath="%sremote%s.csv"%(self.path,self.host)
        send="block"
        updateData="%s;%s;%s;%s\n"%(forceUpdate,objectID,calling,args)
        if not forceUpdate:
            '''
            if forceUpdate False check if device on this host
            if forceUpdtae True send to all remote host
            '''
            if not self.ifonThisHost(objectID):
                '''
                if device not on this host do nothing
                '''
                self.writeFile(logpath,"%s;%s"%(send,updateData))
                return 
                 
        for coreName in self.coreClients:
            try:
                if not self.ifonThisHost(coreName): 
                    ''' remote Core '''
                    if self.coreClients[coreName]['enable']==False:
                        continue
                    self.coreClients[coreName]['instance'].updateRemoteCore(objectID,calling,args)
                    send="send"
            except:
                LOG.error("can not update core Client queue: %s"%(coreName))
        self.writeFile(logpath,"%s;%s"%(send,updateData))       
    
    def __buildCoreClient(self,objectID,coreCFG={},syncStatus=False):
        '''
        add a core connector as server or client
        corename=the corename of the client (name@hostname)
        
        syncStatus true/false if true it set the status to the core to is sync
        '''
        if objectID in self.coreClients:
            raise remoteCoreException("gateway %s exists"%(objectID),False)
        try:
            LOG.info("try to build remote core client %s"%(objectID))
            coreConfig={ 
                        "enable":False,
                        "blocked": 60,  
                        "encoding": "plain", 
                        "hostName": objectID, 
                        "ip": "127.0.0.1", 
                        "password": "password", 
                        "port": 5091, 
                        "protokolVersion": 1, 
                        "user": "user"
            }
            coreConfig.update(copy.deepcopy(coreCFG))
            ''' gateway container '''
            self.coreClients[objectID]={
                'config':coreConfig,
                'instance':False,
                'enable':coreConfig['enable'],
                'running':False,
                'coreStatusSync':syncStatus
                }
            if self.ifonThisHost(objectID):
                '''
                build core Server
                '''
                LOG.info("remote core server %s is build"%(objectID))
                self.coreClients[objectID]['instance']=coreServer(self,coreConfig)
                self.coreClients[objectID]['instance'].daemon=True   
            else:
                '''
                build core Client
                '''
                LOG.info("remote core client %s is build"%(objectID))
                self.coreClients[objectID]['instance']=coreClient(self,coreConfig)
                self.coreClients[objectID]['instance'].daemon=True
                if self.coreClients[objectID]['coreStatusSync']:
                    self.coreClients[objectID]['instance'].setSyncStatus(syncStatus)
        except:
            self.coreClients[objectID]['enable']=False
            self.coreClients[objectID]['instance']=False
            self.coreClients[objectID]['running']=False
            self.coreClients[objectID]['coreStatusSync']=False
            raise coreException("can not build remote core client %s"%(objectID))