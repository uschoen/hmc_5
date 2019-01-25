'''
Created on 01.12.2018

sudo pip-3.2 install --index-url=https://pypi.python.org/simple/ netifaces


@author: uschoen
'''

__version__='5.0'
__author__ = 'ullrich schoen'

BUFFER=8192
ENDMARKER="<<<end>>>!!!"

# Standard library imports
import time
import socket
import threading
# Local application imports
from core.hmcException import gatewayException
from gateways.hmc.defaultGateway import defaultGateway
from core.remoteClient.server import clientRequest

class remoteCore(defaultGateway):
    '''
    classdocs
    '''
    def __init__(self,gatewaysCFG,core):
        defaultGateway.__init__(self,gatewaysCFG,core)
        ''' gateway config '''
        self.config={
                    'protocolVersion': 1,
                    'hostName':"localhost",
                    'ip': '0.0.0.0', 
                    'password': 'password', 
                    'port': 5091, 
                    'user': 'user',
                    "encoding":"plain",
                    "timeout":60 
                     }
        self.config.update(gatewaysCFG)
        
        ''' core '''
        self.__core=core
        
        ''' block gateway time '''
        self.__blockTime=0
        
        self.log.info("build remote core Gateways, %s instance"%(__name__))
    
    def run(self):
        try:
            networkSocket=False
            self.log.debug("remote core gateway start")
            while self.running:
                if self.__blockTime<int(time.time()):
                    try:
                        if not networkSocket:
                            networkSocket=self.__buildSocket(self.config['ip'],self.config['port'])
                        networkSocket.settimeout(0.3)
                        (clientSocket, ipAddr) = networkSocket.accept() 
                        networkSocket.settimeout(None) 
                        self.log.debug("get connection from %s"%(ipAddr[0]))
                        threading.Thread(target=self.__clientRequest,args = (clientSocket,ipAddr[0])).start()
                        self.log.debug("start new client thread for client ip:%s"%(ipAddr[0]))
                    except socket.timeout:
                        pass
                    except gatewayException as e:
                        networkSocket=False
                        self.__blockServer()
                        raise e
                    except:
                        networkSocket=False
                        self.__blockServer()
                        raise gatewayException("some error in server connection")
                time.sleep(0.1)
            self.log.warning("%s normally stop:"%(__name__))
        except:
            self.log.error("some error in raspberry onewire gateway. gateway stop")
    
    def __clientRequest(self,networkSocket,clientIP):
        try:
            clientServer=clientRequest(self.config,self.__core)
            clientServer.startRequest(networkSocket,clientIP)
            self.__closeSocket(networkSocket)
        except:
            self.log.error("some error in client Request remote core")
            self.__closeSocket(networkSocket)     
    
    def __buildSocket(self,ip,port):
        '''
        build a socket connection
        
        fetch exception
        '''
        self.log.debug("try to build socket ip:%s:%s"%(ip,port))
        try:
            networkSocket=socket.socket (socket.AF_INET, socket.SOCK_STREAM)
            networkSocket.bind((ip,port))
            networkSocket.setblocking(0)
            networkSocket.listen(20)
            self.log.info("socket ip:%s:%s is ready"%(ip,port))
            return networkSocket
        except :
            raise gatewayException("can not build socket ip:%s:%s"%(ip,port))
    
    def __closeSocket(self,clientsocket):
        ''' close the server socket '''
        try:
            clientsocket.close()
        except:
            pass
        self.log.debug("close socket server")
    
    def shutdown(self):
        '''
        shutdown server
        '''
        self.running=0
        self.log.critical("stop %s thread"%(__name__))
    
    def __blockServer(self):
        '''
        block the server for new connections
        '''
        self.log.error("block server for %i sec"%(self.config['timeout']))
        self.__blockTime=self.config['timeout']+int(time.time())