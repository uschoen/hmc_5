'''
Created on 01.12.2018

@author: uschoen
'''


__version__='5.0'
__author__ = 'ullrich schoen'

# Standard library imports
import logging
import threading
import time
import socket
# Local apllication constant
from .exceptions import cryptException,protokolException,remoteServerException
from .protokol.version1  import coreProtokol1

LOG=logging.getLogger(__name__) 

class coreServer(threading.Thread):
    
    def __init__(self,core,cfg):
        threading.Thread.__init__(self)
        
        ''' configuration '''
        self.config={
            'protokolVersion':'1',
            'password': 'password',  
            'user': 'user',
            "encoding":"plain",
            "hostName":"unkown"
            }
        self.config.update(cfg)
        
        ''' running flag '''
        self.running=True
        
        ''' remote core clients '''
        self.remoteClients=[]
        
        ''' core instance ''' 
        self.__core=core
        
        ''' core block for x sec'''
        self.__blockTime=0
        
        ''' add coreProtokoll version '''
        self.__coreProtocol={
                        1:coreProtokol1
                      }
        if not self.config['protokolVersion'] in self.__coreProtocol:
            self.logger.error("protokolVersion %s is not avaible option set to 1"%(self.config['protokolVersion']))
            self.config['protokolVersion']=1 
            
        LOG.info("init new remote server %s"%(self.config['hostName']))
    
    def run(self):
        try:
            networkSocket=False
            LOG.debug("remote core server start %s"%(self.config['hostName']))
            while self.running:
                if self.__blockTime<int(time.time()):
                    try:
                        if not networkSocket:
                            networkSocket=self.__buildSocket(self.config['ip'],self.config['port'])
                        networkSocket.settimeout(0.1)
                        (clientSocket, ipAddr) = networkSocket.accept() 
                        networkSocket.settimeout(None) 
                        LOG.debug("get connection from %s on remote server %s"%(ipAddr[0],self.config['hostName']))
                        threading.Thread(target=self.__clientRequest,args = (clientSocket,ipAddr[0])).start()
                    except socket.timeout:
                        pass
                    except:
                        self.__closeSocket(networkSocket)
                        networkSocket=False
                        self.__blockServer()
                        LOG.error("error in remote core server %s"%(self.config['hostName']))
                time.sleep(0.1)
            LOG.info("%s stop remote server:"%(self.config['hostName']))
        except:
            LOG.error("error in remote core server %s, server stop"%(self.config['hostName']))
    
    def __clientRequest(self,networkSocket,clientIP):
        try:
            LOG.debug("get new client request from %s on %s"%(clientIP,self.config['hostName']))
            coreProtokoll=self.__coreProtocol[self.config['protokolVersion']](self.config)
            self.remoteClients.append(coreProtokoll)
            firstRun=True
            while self.running:
                try:
                    ''' reading data '''
                    LOG.debug("work/wait for next job  from %s on server %s"%(clientIP,self.config['hostName']))
                    commadsArgs=coreProtokoll.readJob(networkSocket,firstRun)
                    LOG.debug("get job for object ID:%s function:%s on remote server %s"%(commadsArgs['objectID'],commadsArgs['callFunction'],self.config['hostName']))
                    ''' try to execute job'''
                    method_to_call = getattr(self.__core,commadsArgs['callFunction'])
                    args=commadsArgs['args']
                    method_to_call(*args)
                except Exception as e:
                    raise e
                    ''' send ok and wait for next job '''   
                coreProtokoll.sendJobResult(networkSocket,"ok",None)
                firstRun=False
        except (cryptException,protokolException) as e:
            LOG.error("%s"%(e.msg))
            coreProtokoll.sendJobResult(networkSocket,"error","%s"%(e.msg))
        except:
            LOG.error("some error in remote core server %s"%(self.config['hostName']))
            coreProtokoll.sendJobResult(networkSocket,"some error in remote core server %s"%(self.config['hostName']))
        self.__closeSocket(networkSocket)
    
    def shutdown(self):
        try:
            LOG.critical("shutdown remote server %s"%(self.config['hostName']))
            self.running=False
            for coreProtokoll in self.remoteClients:
                coreProtokoll.shutdown()
        except:
            raise remoteServerException("can't shutdown remote client %s"%(self.config['hostName']))
            
    def __buildSocket(self,ip,port):
        '''
        build a socket connection
        
        fetch exception
        '''
        try:
            networkSocket=socket.socket (socket.AF_INET, socket.SOCK_STREAM)
            networkSocket.bind((ip,port))
            networkSocket.setblocking(0)
            networkSocket.listen(20)
            LOG.debug("lissen on interface %s, port %s on remote server %s"%(ip,port,self.config['hostName']))
            return networkSocket
        except :
            raise remoteServerException("can not build socket ip:%s:%s on remote server %s"%(ip,port,self.config['hostName']))
                                 
    def __blockServer(self):
        '''
        block the server for new connections
        '''
        LOG.error("block remote server %s for %i sec"%(self.config['hostName'],self.config['timeout']))
        self.__blockTime=self.config['timeout']+int(time.time())
               
    def __closeSocket(self,networkSocket):
        ''' close the server socket '''
        try:
            networkSocket.close()
        except:
            pass
        LOG.debug("close socket from remote server %s"%(self.config['hostName']))