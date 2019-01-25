'''
Created on 31.12.2018

@author: uschoen
'''

__version__='5.0'
__author__ = 'ullrich schoen'
BUFFER=512
ENDMARKER=b'<<stop>>!!!'
#ENDMARKER=b''
__protokolVersion__='1'

# Standard library imports
import logging
import socket
import string
import random

# Local apllication constant
from ..encryption.aes import aes
from ..encryption.plain import plain
from ..exceptions import protokolException,cryptException

randomSecret=lambda :''.join(random.choice(string.ascii_letters + string.digits) for _ in range(20))


LOG=logging.getLogger(__name__)

class coreProtokol1():
    '''
    remote core Protkoll Version 1
    '''
    def __init__(self,clientCFG):
        self.__cfg={
            'hostName':"localhost",
            'ip': '127.0.0.1', 
            'password': 'password', 
            'port': 5091, 
            'user': 'user',
            "encoding":"plain",
            "debug":False,
            "running":True       
            }
        self.__cfg.update(clientCFG)
     
        ''' allowed functions '''
        self.__allowedFunction={
                        'addDevice',
                        'restoreDevice',
                        'setDeviceChannelValue',
                        'restoreCoreClient',
                        'restoreGateway',
                        'addDeviceChannel'}
        
        ''' network socket '''
        self.__networkSocket=False
        
        ''' current aditionel session password'''
        self.__sessionPassword=""
        
        ''' last bit/byte of send meassgaes '''
        self.__lastMSG=b''
        
        ''' running flag '''
        self.running=True
        
        self._debug=self.__cfg['debug']
        #add en-decyption aes
        encoding={
            "aes":aes,
            "plain":plain
            }
        if not self.__cfg['encoding'] in encoding:
            LOG.error("%s is not avaible option for encoding, use plain now"%(self.__cfg['encoding']))
            self.__cfg['encoding']="plain"
        self.__crypt=encoding[self.__cfg['encoding']]()
            
        LOG.debug("build coreProtokoll V%s"%(__protokolVersion__))
    
    def __currentPassword(self):
        password="%s%s"%(self.__cfg['password'],self.__sessionPassword)
        return password
            
    def sendJob(self,args):
        try:
            self.__sessionPassword=""
            ip=self.__cfg.get('ip')
            port=int(self.__cfg.get('port'))
            user=self.__cfg.get('user')    
            
            if not self.__networkSocket:
                ''' build network connection '''
                self.__networkSocket=self.__openNetworkSocketToClient(ip,port)
                ''' send autorisation '''
                self.__sendAuthorization(self.__networkSocket,self.__crypt,user,self.__currentPassword())
                ''' retrive session password '''
                self.__sessionPassword=self.__getSessionPassword(self.__networkSocket,self.__crypt,user,self.__currentPassword())
            ''' send command '''
                
            self.__sendCommand(self.__networkSocket, self.__crypt, user, self.__currentPassword(), args)
            self.__checkCommandResponse(self.__networkSocket,self.__crypt,user,self.__currentPassword())
            self.__networkSocket=self.__networkSocket
        except (cryptException,protokolException,socket.error) as e:
            self.__networkSocketClose(self.__networkSocket)
            self.__networkSocket=False
            self.__sessionPassword=""
            raise e
        except:
            self.__networkSocketClose(self.__networkSocket)
            self.__networkSocket=False
            self.__sessionPassword=""
            raise protokolException ("unkown error to send to remote core client %"%(self.__cfg.get('hostName')))
        
    def readJob(self,networkSocket,firstRun):
        try:
            user=self.__cfg.get('user')  
            if firstRun:
                self. __getAuthorizationRequest(networkSocket, self.__crypt, user, self.__currentPassword())
                newSecret=randomSecret()
                self.__sendSessionPassword(networkSocket, self.__crypt, user, self.__currentPassword(), newSecret)
                self.__sessionPassword=newSecret
            commadsArgs=self.__getCommandRequest(networkSocket, self.__crypt, user, self.__currentPassword())
            if commadsArgs['callFunction'] not in self.__allowedFunction:
                raise protokolException("callfunction %s not allowed"%(commadsArgs['callFunction']),False)
            #LOG.debug("objectID: %s, callFuction %s"(objectID,callFunction))
            return commadsArgs
        except (protokolException,cryptException) as e:
            raise e
        except:
            raise protokolException("unkown error")
    
    def sendJobResult(self,networkSocket,result="error",message=""):
        try:
            user=self.__cfg.get('user') 
            self.__sendResult(networkSocket,self.__crypt,user,self.__currentPassword(),result,message)
        except (cryptException,protokolException) as e:
            raise e
        except:
            raise protokolException("can't send result") 
    
    def shutdown(self):
        try:
            LOG.warning("shutdown remote protokoll1 for %s"%(self.__cfg['hostName']))
            self.running=False      
        except:
            pass
            
    def __getAuthorizationRequest(self,networkSocket,encryption,user,password):
        '''
        check autorisation request 
        
        exception for: user error and protokoll error
        '''
        try:
            ''' read network socket '''
            #readData=networkSocket.recv(BUFFER)
            #if readData==b'':
            #    raise protokolException("network socket closed",False)
            readData=self.__readSocket(networkSocket)
            ''' check resived data '''
            LOG.debug("get autorisation")
            readVars=encryption.unSerialData(readData)
            self.__checkHeader(readVars.get("header",{}),user)            
            decryptBodyVars=self.__decryptBody(readVars.get("body",{}),encryption,password)
            if not "checkAuthorization" in decryptBodyVars.get('callFunction',None):
                raise protokolException("get no callFunction checkAuthorization")
        except (protokolException,cryptException) as e:
            raise e
        except:
            pass
    
    def __sendAuthorization(self,networkSocket,encryption,user,password):
        '''
        send autorision request to core
        '''
        try:
            body={
                'callFunction':'checkAuthorization'
            }
            body=self.__buildBody(encryption, body, password)
            autorisationString=self.__buildHeader(encryption, user, body)
            LOG.debug("send authorization")
            self.__writeSocket(networkSocket,autorisationString)
        except (protokolException,cryptException) as e:
            raise e
        except:
            raise protokolException("erro can't send autorisation")
    
    def __sendSessionPassword(self,networkSocket,encryption,user,password,newSecret):
        ''' 
        send a new sessesion password back to client
        '''
        try:
            body={
                'result':'ok',
                'sessionPassword':newSecret
                }
            body=self.__buildBody(encryption,body,password)
            commandString=self.__buildHeader(encryption, user, body)
            LOG.debug("send session password")
            self.__writeSocket(networkSocket,commandString)
        except (protokolException,cryptException) as e:
            raise e
        except:
            raise protokolException("err send autoriation")    

    def __getSessionPassword(self,networkSocket,encryption,user,password):
        '''
        check header and body, give the new session password back
        
        exception:protokolException,cryptException
        '''
        try:
            ''' read network socket '''
            #readData=networkSocket.recv(BUFFER)
            #if readData==b'':
            #    raise protokolException("network socket closed",False)
            readData=self.__readSocket(networkSocket)
            ''' check resived data '''
            LOG.debug("get session password:")
            readVars=encryption.unSerialData(readData)
            self.__checkHeader(readVars.get("header",{}),user)            
            decryptBodyVars=self.__decryptBody(readVars.get("body",{}),encryption,password)
            self.__checkResult(decryptBodyVars)
            if "sessionPassword" in decryptBodyVars:
                return decryptBodyVars.get('sessionPassword','')
            raise protokolException("error in sessionPassword,get body:%s"%(decryptBodyVars))
        except  (protokolException,cryptException) as e:
            raise e
        except:
            pass
    
    def __sendResult(self,networkSocket,encryption,user,password,result="error",message=""):   
        '''
        send a result meassages to core
        
        networkSocket: networkSocket object
        encryption: encryption object
        user: user
        password: password
        result: ok or error    (default=error)
        message: string with message (optional)
        '''
        try:
            body={
                'result':result,
                'message':message
                }
            body=self.__buildBody(encryption, body, password)
            autorisationString=self.__buildHeader(encryption, user, body)
            LOG.debug("send result %s"%(result))
            self.__writeSocket(networkSocket,autorisationString)
        except:
            raise protokolException("can't send result") 
         
    def __checkResult(self,decryptBodyVars):
        '''
        check result of a message
        
        if result not OK send exception: protokolException
        '''
        try:
            if not decryptBodyVars.get('result','error')=="ok":
                raise protokolException("result have error message::%s"%(decryptBodyVars.get('message',"unkown")),False)   
        except (protokolException) as e:
            raise e
        except:
            raise protokolException("error in check result. body:%s"%(decryptBodyVars))
    
    def __sendCommand(self,networkSocket,encryption,user,password,args): 
        try:
            body=self.__buildBody(encryption,args,password)
            commandString=self.__buildHeader(encryption, user, body)
            LOG.debug("send command (objectID %s)"%(args['objectID']))
            self.__writeSocket(networkSocket,commandString)
        except (protokolException,cryptException) as e:
            raise e
        except:
            raise protokolException("error send autoriation")    
    
    def __getCommandRequest(self,networkSocket,encryption,user,password):
        '''
        get a command request
        '''
        try:
            ''' read network socket '''
            LOG.debug("waiting for next command request")
            #readData=networkSocket.recv(BUFFER)
            #if readData==b'':
            #    raise protokolException("network socket closed",False)
            readData=self.__readSocket(networkSocket)
            LOG.debug("get Command Request")
            ''' check resived data '''
            readVars=encryption.unSerialData(readData)
            self.__checkHeader(readVars.get("header",{}),user) 
            decryptBodyVars=self.__decryptBody(readVars.get("body",{}),encryption,password)
            if decryptBodyVars.get('objectID',None)==None:
                raise protokolException("some error in command, no objectID",False)
            if decryptBodyVars.get('callFunction',None)==None:
                raise protokolException("some error in command, no callFunction",False)
            if decryptBodyVars.get('args',None)==None:
                raise protokolException("some error in command, no args",False)
            return (decryptBodyVars)
        except (cryptException,protokolException) as e:
            raise e
        except :
            raise protokolException("some error im get command request")
        
    def __checkCommandResponse(self,networkSocket,encryption,user,password):
        '''
        check a rseult after a command action
        
        networkSocket: networ socket object
        encryption: encryption object
        user: user
        password: password
        
        raise exception: 
        '''
        try:
            ''' read network socket '''
            #readData=networkSocket.recv(BUFFER)
            #if readData==b'':
            #    raise protokolException("network socket closed",False)
            readData=self.__readSocket(networkSocket)
            ''' check resived data '''
            readVars=encryption.unSerialData(readData)
            self.__checkHeader(readVars.get("header",{}),user)            
            decryptBodyVars=self.__decryptBody(readVars.get("body",{}),encryption,password)
            self.__checkResult(decryptBodyVars)
        except  (cryptException,protokolException) as e:
            raise e
        except:
            raise protokolException("error in response password")
    
    def __writeSocket(self,networkSocket,rawData):
        try:
            data=b''.join((rawData,ENDMARKER))
            if self._debug:
                LOG.debug("send data: %s"%(data))
            networkSocket.sendall(data)
        except:
            raise protokolException("can't sent data to network socket")
    
    def __readSocket(self,networkSocket):
        try:
            rawData=self.__lastMSG
            readData=b''
            nextMSG=b''
            while self.running:
                try:
                    networkSocket.settimeout(0.1)
                    readData=networkSocket.recv(BUFFER)
                    if readData==b'':
                        raise protokolException("network socket closed",False)
                except (protokolException) as e:
                    raise e
                except socket.timeout:
                    pass
                networkSocket.settimeout(None)
                rawData=b''.join((rawData,readData))
                if ENDMARKER in rawData:
                    ''' endmarker found '''
                    (readData,nextMSG)=rawData.split(ENDMARKER)
                    break                
            self.__lastMSG=nextMSG
            if self._debug:
                LOG.debug("get data %s"%(readData))
                LOG.debug("rest data %s"%(self.__lastMSG))
            return readData
        except (protokolException) as e:
            raise e
        except:
            raise protokolException("unkown error at reading network Socket",False)

    def __buildBody(self,encryption,body,password):
        '''
        build the body and return as string
        '''
        try:
            cryptBody=encryption.encrypt(body,password)
            return cryptBody
        except (cryptException) as e:
            raise e
        except:
            raise protokolException("error,can't build body")
        
    def __buildHeader(self,encryption,user,body):
        '''
        build the header and return as string
        '''
        try:
            header={
                'header':{
                    'user':user,
                    'protokoll':__protokolVersion__},
                'body':body
                }
            header=encryption.serialData(header)
            return header
        except (cryptException) as e:
            raise e
        except:
            raise protokolException("can'build Header")
    
    def __decryptBody(self,body,encryption,password):
        '''
        decrypt a body
        
        return body as var
        
        exception for entcryption error:cryptException
        exception for default error:protokolException
        '''
        try:
            encryptionBody=encryption.decrypt(body,password)
            return encryptionBody
        except (cryptException) as e:
            raise e
        except:
            raise protokolException("error can't entcrypt body: %s"%(body))
        
    def __checkHeader(self,header,user):
        try:
            if not header.get('protokoll',0)==__protokolVersion__:
                raise protokolException("error no or wrong protokol version. header is:%s"%(header))
            if not header.get('user',"unkown")==user:
                raise protokolException("error no or wrong user. header:%s"%(header))
        except (protokolException) as e:
            raise e
        except:
            raise protokolException("error with header in password response. header:%s"%(header))
         
   
    def __openNetworkSocketToClient(self,ip,port):
        '''
        open a network socket to a core
        
        ip:ip adress oft the server
        port: port of the server
        
        raise for all all erros and eyception: protokolException
        '''
        try:
            LOG.debug("try connect to Core %s:%s"%(ip,port))
            clientSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientSocket.connect((ip,port))
            return clientSocket
        except socket.error as e:
            LOG.error("can't open socket to remote core %s"%(ip))
            raise e
        except:
            raise protokolException ("can not connect to Core %s:%s"%(ip,port),False)
    
    def __networkSocketClose(self,networkSocket):
        '''
        close the socket to the client
        
        fetch the exception
        '''
        try:
            networkSocket.close()
        except:
            pass
        LOG.debug("close network socket") 
