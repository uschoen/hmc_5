'''
Created on 01.12.2018

@author: uschoen

install 
'''


__version__='5.0'
__author__ = 'ullrich schoen'

#TODO: if gaeway stop its send two tmes a rpc stop command to homematic


# Standard library imports
import threading
import xmltodict                                            #@UnresolvedImport
import time
import urllib3                                              #@UnresolvedImport
import xmlrpc.client                                            #@UnresolvedImport
import random
import logging
from xmlrpc.server import SimpleXMLRPCServer           #@UnresolvedImport
from xmlrpc.server import SimpleXMLRPCRequestHandler   #@UnresolvedImport @UnusedImport


# Local application imports
from core.hmcException import gatewayException
from gateways.hmc.defaultGateway import defaultGateway
from gateways.homematic.hm_RPCCallback import hmcRPCcallback

LOG=logging.getLogger(__name__)

class server(defaultGateway):

    def __init__(self,gatewaysCFG,core):
        defaultGateway.__init__(self,gatewaysCFG,core)
        self.config={
            'enable':False,
            'name':"unkown",
            'blockRPCServer':60,
            'hm_interface_id':"u%s"%(random.randint(100,999)),
            'rpc_port':6050+random.randint(0,49),
            'rpc_ip':"127.0.0.0",
            'MSGtimeout':60,
            "HomeMaticURL":"http://127.0.0.1/config/xmlapi/statechange.cgi",
            "iseID":"1281",
            "iseIDValue":0,
            "hm_ip":"127.0.0.1",
            "hm_port":2001
            }
        self.config.update(gatewaysCFG)
        #"iseID_rf":"1012",
        ''' rpc server intance '''
        self.__rpcServer=False
        self.rpcServerINST=False
        
        ''' block time for rpc server'''
        self.__blockTime=0
        
        ''' timer '''
        self.__timerHmWakeUP=0
        self.__timerRestartXM=0
        
        LOG.info("build hm-RPC gateway, %s instance"%(__name__))
    
    def run(self):
        try:
            LOG.info("%s start"%(__name__))
            rpcIp=self.config['rpc_ip']
            rpcPort=self.config['rpc_port']
            hmIP=self.config['hm_ip']
            hmPort=self.config['hm_port']
            interfaceID=self.config['hm_interface_id']
            self.__resetHmMessagesTimer()
            self.__resetRestartXMLTimer()
            while self.running:
                try:
                    if self.__blockTime<int(time.time()):
                        if self.__buildRPCServer(rpcIp,rpcPort,self.config['name']):
                            self.__requestRpcMsg(rpcIp, rpcPort, hmIP, hmPort, interfaceID)
                        if self.__timerRestartXML<int(time.time()):
                            raise gatewayException("timeout-2 restart server",False)
                        if self.__timerHmWakeUP<int(time.time()):
                            LOG.warning("message timeout, detected. no message since %s sec"%(self.config['MSGtimeout']))
                            self.__sendXMLCMD(self.config['HomeMaticURL'],self.config['iseID'],self.config['iseIDValue'])  
                    time.sleep(0.1) 
                except:
                    LOG.error("error in rpc server %s"%(self.config['name']))  
                    self.__blockServer() 
                    self.__stopRpcMSG(self.config['rpc_ip'], self.config['rpc_port'], self.config['hm_ip'], self.config['hm_port'])
                    self.__stopRPCServer()
            LOG.critical("RPC server normally stop:%s"%(self.config['name']))  
        except:
            LOG.critical("%s have a problem and stop"%(self.config['name']),exc_info=True)
    
    def shutdown(self):
        try:
            LOG.critical("%s gateway shutdown"%(self.config['name']))
            self.__stopRpcMSG(self.config['rpc_ip'], self.config['rpc_port'], self.config['hm_ip'], self.config['hm_port'])
            self.__stopRPCServer()
            self.running=False
        except:
            pass
    
    def __resetAllTimer(self):
        self.__resetHmMessagesTimer()
        self.__resetRestartXMLTimer()
        
    def __resetHmMessagesTimer(self):
        ''' reset timer '''
        #LOG.debug("reset MSG timeout for gateway %s"%(self.config['name']))
        self.__timerHmWakeUP=self.config['MSGtimeout']+int(time.time()) 
    
    def __resetRestartXMLTimer(self):
        ''' reset timer '''
        #LOG.debug("reset MSG timeout for gateway %s"%(self.config['name']))
        self.__timerRestartXML=self.config['MSGtimeout']+int(time.time())+5
    
    def __requestRpcMsg(self,rpcIp,rpcPort,hmIP,hmPort,interfaceID):
        '''
        send a init Request to get data
        
        raise exception on failed
        '''
        try:
            LOG.info("send a RPC start INIT request at:http://%s:%i ID:%s" %(hmIP, int(hmPort),interfaceID))
            proxy=xmlrpc.client.ServerProxy("http://%s:%i" %(hmIP, int(hmPort)))
            proxy.init("http://%s:%i" %(rpcIp, rpcPort), interfaceID)
            LOG.debug("send a RPC INIT Request finish")
        except xmlrpc.client.Fault as err:
            LOG.error("proxyInit: Exception: %s" % str(err))
            LOG.error("INIT Request Fault code: %d" % err.faultCode)
            LOG.error("INIT request Fault string: %s" % err.faultString)
            raise gatewayException("some error in INIT Request")
        except:
            raise gatewayException("can't send a INIT request %s"%(self.config['name']))
    
    def __stopRpcMSG(self,rpcIp,rpcPort,hmIP,hmPort):
        try:
            LOG.info("send a RPC stop  INIT request at:http://%s:%i" %(hmIP, int(hmPort)))
            proxy=xmlrpc.client.ServerProxy("http://%s:%i" %(hmIP, int(hmPort)))
            proxy.init("http://%s:%s"%(rpcIp, int(rpcPort)))
        except xmlrpc.client.Fault as err:
            LOG.error("INIT Request Fault code: %d" % err.faultCode)
            LOG.error("INIT request Fault string: %s" % err.faultString)
            raise gatewayException("some error in INIT Request %s"%(self.config['name']))
        except:
            LOG.error("can't send a stop INIT request",exc_info=True)   
    
    def __sendXMLCMD(self,hmURL,iseID,iseValue):
        '''
        set a value in the homematic for a device to get a message back
        '''
        try:
            url=("%s?ise_id=%s&new_value=%s"%(hmURL,iseID,iseValue))
            LOG.info("send messages to homematic %s to wake up for gateway %s"%(url,self.config['name']))
            http = urllib3.PoolManager()
            response = http.request('GET', url)
            LOG.debug("http response code %s:"%(response.data))
            httpStatus=response.status
            if  httpStatus != 200:
                raise gatewayException("get html error '%s'"%(httpStatus),False) 
            HMresponse=xmltodict.parse(response.data)
            if "result" in HMresponse:
                if "changed" in HMresponse['result']: 
                    LOG.debug("value successful change")
                else:
                    raise gatewayException("get some unkown answer %s"%(response.data),False)
            else:
                raise gatewayException("get some unkown answer %s"%(response.data),False)
            self.__resetHmMessagesTimer()
        except (gatewayException) as e:
            raise e 
        except :
            raise gatewayException("something going wrong !!!")
                     
    def __buildRPCServer(self,ip,port,name):
        '''
        build a RPC Server
        '''
        try:
            if self.__rpcServer:
                if self.__rpcServer.isAlive():
                    ''' server is running '''
                    return False
                else:
                    ''' server is exciting but not running '''
                    LOG.warning("RPC Server %s:%s is stop,starting new server %s"%(ip,port,name))
                    self.__stopRpcMSG(self.config['rpc_ip'], self.config['rpc_port'], self.config['hm_ip'], self.config['hm_port'])
                    self.__stopRPCServer()
            LOG.info("RPC Server %s %s:%s start"%(name,ip,port))
            self.rpcServerINST = SimpleXMLRPCServer((ip,int(port)))
            self.rpcServerINST.logRequests=False
            self.rpcServerINST.register_introspection_functions() 
            self.rpcServerINST.register_multicall_functions() 
            self.rpcServerINST.register_instance(hmcRPCcallback(self.config,self.core,self.__resetAllTimer))
            self.__rpcServer = threading.Thread(target=self.rpcServerINST.serve_forever)
            self.__rpcServer.start()
            self.__resetAllTimer()
            LOG.info("RPC Server %s is start"%(name))
            return True
        except:
            raise gatewayException("can't start rpc server %"%(name))
    
    def __stopRPCServer(self):
        try:
            LOG.warning("stop RPC Server %s"%(self.config['name']))
            if self.__rpcServer:
                self.rpcServerINST.server_close()
            self.rpcServerINST=False
            self.__rpcServer=False
        except:
            LOG.error("can't stop RPC server %s"%(self.config['name']))
            
    def __blockServer(self):
        '''
        block the server for new connections
        '''
        try:
            LOG.error("block server %s for %s sec"%(self.config['name'],self.config['blockRPCServer']))
            self.__blockTime=self.config['blockRPCServer']+int(time.time())
        except:
            raise gatewayException("some unkown error in block server %s"%(self.config['name']))
            