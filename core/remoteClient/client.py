'''
Created on 01.12.2018

@author: uschoen
'''


__version__='5.0'
__author__ = 'ullrich schoen'

# Standard library imports
import threading
import logging
import time
import queue                    #@UnresolvedImport
from time import sleep
# Local apllication constant
from .exceptions import clientException,cryptException,protokolException
from .protokol.version1  import coreProtokol1



class coreClient(threading.Thread):
    '''
    object um eine verbindung zu einem remote core aufzubauen 
    um remote command zu uebermitteln.
    '''


    def __init__(self,core,clientCFG={}):
        threading.Thread.__init__(self)
        self.logger=logging.getLogger(__name__) 
        
        #default client config
        self.__cfg={
            'hostName':"localhost",
            'enable':False,
            'blocked':60,
            "protokolVersion":1          
            }
        self.__cfg.update(clientCFG)
        
        ''' core intance'''
        self.__core=core
        
        ''' short form for hostname '''
        self.__hostName=self.__cfg['hostName']
        
        #is remote core in sync
        self.coreStatusSync=False
        
        #block time for client
        self.__clientBlocked=0
        
        #network connection
        self.__remoteCoreProtokoll=False
        
        #core queue
        self.__coreQueue=queue.Queue()
        
        ''' sync queue '''
        self.__syncQueue=queue.Queue()
        
        #is connection running
        self.running=self.__cfg['enable']
        
        #add coreProtokoll version
        coreProtocol={
                        1:coreProtokol1
                      }
        if not self.__cfg['protokolVersion'] in coreProtocol:
            self.logger.error("protokolVersion %s is not avaible option set to 1"%(self.__cfg['protokolVersion']))
            self.__cfg['protokolVersion']=1
        self.__coreProtocol=coreProtocol[self.__cfg['protokolVersion']](self.__cfg)  
        
        self.logger.info("build remote core client %s"%(self.__hostName))
    
    def shutdown(self):
        try:
            self.logger.critical("shutdown down remote client %s"%(self.__hostName))
            self.running=False
        except:
            raise clientException("can't shutdown remote client %s"%(self.__hostName))
               
    def run(self):
        '''
        client loop
        '''
        try:
            self.logger.info("%s start"%(__name__))
            while self.running:
                try:
                    if self.__clientBlocked<time.time():
                        if not self.__remoteCoreProtokoll:
                            self.__remoteCoreProtokoll=self.__coreProtocol
                            self.__syncClient(self.__remoteCoreProtokoll)
                        if not self.__coreQueue.empty():
                            self.__workingQueue(self.__remoteCoreProtokoll,self.__coreQueue)
                except:
                    self.__blockClient()
                    self.__setCoreNotSync()
                    self.__remoteCoreProtokoll=False   
                sleep(0.1)
            self.logger.info("remote client %s is stop"%(self.__hostName))
        except:
            self.logger.error("remote client %s is stop with error"%(self.__hostName))
    
    def __workingQueue(self,remoteCoreProtokol,jobQueue):
        try:
            self.logger.debug("work for queue to core %s"%(self.__hostName))
            while not jobQueue.empty():
                remoteCoreProtokol.sendJob(jobQueue.get())
        except (cryptException,protokolException) as e:
            raise e
        except:
            raise clientException("can't work on queue for client to core %s"%(self.__hostName),False)
    
    def __syncClient(self,remoteCoreProtokol):
        try:
            self.logger.info("try to sync for core client %s"%(self.__hostName))
            self.__clearCoreQueue()
            
            self.__syncQueue.queue.clear()
            self.__syncCoreDevices()
            self.__syncCoreGateways()
            self.__syncCoreClients()
            while not self.coreStatusSync:
                if self.__syncQueue.empty():
                    break
                self.__workingQueue(remoteCoreProtokol,self.__syncQueue)
            self.logger.info("finish with sync to core %s"%(self.__hostName))
            self.__unblockClient()
            self.__setCoreIsSync()
        except (clientException) as e:
            self.__blockClient()
            self.__setCoreNotSync()
            raise e
        except :
            self.__blockClient()
            self.__setCoreNotSync()
            raise clientException("can't sync client to core %s"%(self.__hostName))
    
    def updateRemoteCore(self,objectID,callFunction,args):
        '''
            put a job in the work queue
        '''
        try:
            if self.__clientBlocked>int(time.time()):
                self.logger.debug("core client %s block for %i s"%(self.__hostName,self.__clientBlocked-int(time.time())))
                return
            self.logger.debug("putting job for objectID:%s callFunction:%s into queue from %s"%(objectID,callFunction,self.__hostName))
            updateObj={
                        'objectID':objectID,
                        'callFunction':callFunction,
                        'args':args
                        }
            self.__coreQueue.put(updateObj)
        except:
            raise clientException("can't put update in queue for objectID %s on remote client %s"%(objectID,self.__hostName))
    
    def __blockClient(self):
        '''
            block connection to client for x sec
        ''' 
        self.logger.warning("block core client to core %s for %i s"%(self.__hostName,self.__cfg['blocked'] ))
        self.__clientBlocked=int(time.time())+self.__cfg['blocked']
    
    def __unblockClient(self):
        '''
            unblock connection to client
        ''' 
        self.logger.info("unblock core client %s"%(self.__hostName))
        self.__clientBlocked=0
    
    def setSyncStatus(self):
        '''
            set staus sync to true
        '''
        self.__setCoreIsSync()
        
    def __setCoreIsSync(self):
        '''
            set staus sync to true
        '''
        self.logger.info("core client to core %s is syncron"%(self.__hostName))
        self.coreStatusSync=True
    
    def __setCoreNotSync(self):
        '''
            set staus sync to false
        '''
        self.logger.info("core client to core %s is not syncron"%(self.__hostName))
        self.coreStatusSync=False
    
    def __clearCoreQueue(self):
        '''
        ' clear the core Queue
        '''
        try:
            self.logger.info("clear core queue")
            self.__coreQueue.queue.clear()
        except:
            raise clientException("can't clear coreQueue to host %s"%(self.__hostName),False)
    
    def __syncCoreDevices(self):
        '''
        sync all devices from this host
        '''
        try:
            self.logger.info("sync devices to core %s"%(self.__hostName))
            for deviceID in self.__core.getAllDeviceID():
                if not self.__core.ifonThisHost(deviceID):
                    continue
                self.logger.info("sync devicesID %s to core %s"%(deviceID,self.__hostName))
                device=self.__core.getDeviceConfiguration(deviceID)
                args=(deviceID,device)
                updateObj={
                        'objectID':deviceID,
                        'callFunction':'restoreDevice',
                        'args':args}
                self.__syncQueue.put(updateObj)
        except:
            raise clientException("can't sync devices to host %s"%(self.__hostName),False)
            
    def __syncCoreGateways(self):
        '''
        sync all gateways events from this host
        '''
        try:
            self.logger.info("sync Gateways to host %s"%(self.__hostName))
            for gatewayName in self.__core.getAllGatewayNames():
                if not self.__core.ifonThisHost(gatewayName):
                    continue
                updateObj={
                        'objectID':gatewayName,
                        'callFunction':'restoreGateway',
                        'args':(gatewayName,self.__core.getGatewayConfiguration(gatewayName))}
                self.__syncQueue.put(updateObj)
        except:
            raise clientException("can't sync gateways to host %s"%(self.__hostName),False)
        
    def __syncCoreClients(self):
        '''
        sync all core clients from this host
        '''
        try:
            self.logger.info("sync CoreClients to host %s"%(self.__hostName))
            for coreName in self.__core.coreClients:
                if not self.__core.ifonThisHost(coreName):
                    continue
                args=(coreName,self.__core.coreClients[coreName]['config'])
                updateObj={
                            'objectID':coreName,
                            'callFunction':'restoreCoreClient',
                            'args':args}
                self.__syncQueue.put(updateObj)
        except:
            raise clientException("can't sync coreClients to host %s"%(self.__hostName),False)
    

            

    
