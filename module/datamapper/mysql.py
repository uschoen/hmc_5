'''
Created on 01.12.2018

@author: uschoen
'''


__version__='5.0'
__author__ = 'ullrich schoen'

# Local application imports
from core.hmcException import coreModuleException

# Standard library imports
import logging
try:
    import mysql.connector                                                         #@UnresolvedImport
    from mysql.connector import Error                                              #@UnresolvedImport,@UnusedImport
    from mysql.connector import errorcode                                          #@UnresolvedImport,@UnusedImport
except:
    raise coreModuleException("no mysql.connector module installed")
import time

# Local apllication constant
LOG=logging.getLogger(__name__)


class mysqlManager(object):
    '''
    modulCFG={
            "db": "hmc", 
            "host": "127.0.0.1", 
            "modulName": "dataMapper@hmc", 
            "password": "password", 
            "port": 3306, 
            "user": "user",
            "table":"statistic",
            "mapping":{
                "timestamp":"getTimestamp",
                "value":"getValue",
                "deviceID":"getDeviceID",
                "channel":"getChannel",
            }
        }
    '''
    def __init__(self,modulName,modulCFG,core):
        '''
        Constructor
        '''
        try:
            self.core=core
            self.config={
                            'modulName':modulName,
                            'host':"127.0.0.1",
                            'user':"unknown",
                            'db':"unknown",
                            'password':"unknown",
                            "port":3306,
                            "table":"statistic",
                            "mapping":{}
                        }
            self.callerARGS={}
            self.mappers={
                "getTimestamp":self.__getTimestamp,
                "getValue":self.__getValue,
                "getDeviceID":self.__getDeviceID,
                "getChannel":self.__getChannel
                }
            self.config.update(modulCFG)
            self.__dbConnection=False
            LOG.info("build mysqlMapper modul:%s"%(modulName))
        except:
            raise coreModuleException("can't build modul %s"%(modulName))
    def __getTimestamp(self):
        return int(time.time())
    
    def __getValue(self):
        try:
            channelValue=self.core.getDeviceChannelValue(self.callerARGS['deviceID'],self.callerARGS['channelName'])
            return channelValue
        except coreModuleException as e:
            raise e
        except:
            raise coreModuleException("can't get value from device")
    
    def __getDeviceID(self):
        return self.callerARGS['deviceID']   
    
    def __getChannel(self):
        return self.callerARGS['channelName']
    
    def update(self,args):
        try:
            self.callerARGS=args
            if self.callerARGS['deviceID']==None:
                raise coreModuleException("no device ID given")
            if self.callerARGS['channelName']=="device":
                LOG.debug("ignore update , deviceID %s, is device channel"%(self.callerARGS['deviceID']))
                return
            LOG.debug("call update from deviceID %s channel:%s "%(self.callerARGS['deviceID'],self.callerARGS['deviceID']))   
            sql=self.__buildSQL()
            if not self.__dbConnection:
                self.__dbConnect()
            self.__insert(sql)
        except:
            LOG.error("some error in modul")
            self.__dbClose()
    
    def __insert(self,sql):
        try:
            
            LOG.debug("insert : %s"%(sql))
            cur = self.__dbConnection.cursor()
            cur.execute(sql)
            self.__dbConnection.commit()  
        except (mysql.connector.Error) as e:
            raise e
        except :
            raise coreModuleException("unkown error sql:%s"%(sql))    
    
    def shutdown(self):
        try:
            LOG.critical("shutdown mysql modul")   
            self.__dbClose()  
        except:
            LOG.error("some error to shutdown mysql connctor")   
                  
    def __buildSQL(self):
        try:
            fieldstring=""
            valuestring=""
            secound=False
            for key in self.config['mapping']:
                if secound:
                    fieldstring+=","
                    valuestring+=","
                secound=True
                fieldstring+=("`%s`"%(key))
                valuestring+=("'%s'"%(self.mappers[self.config['mapping'][key]]()))
            sql=("INSERT INTO %s (%s) VALUES (%s);"%(self.config['table'],fieldstring,valuestring))
            LOG.debug("build sql string:%s"%(sql))
            return sql
        except coreModuleException as e: 
            raise e
        except:
            raise coreModuleException("error in modul")  
                
    def __dbClose(self):
        try:
            if self.__dbConnection:
                LOG.info("close database")
                self.__dbConnection.close()
        except:
            LOG.error("can't close db connection")
            
    def __dbConnect(self):
        LOG.info("try connect to host:%s:%s with user:%s table:%s"%(self.config['host'],self.config['port'],self.config['user'],self.config['db']))
        try:
            self.__dbConnection = mysql.connector.connect(
                                                  host=self.config['host'],
                                                  db=self.config['db'],
                                                  user=self.config['user'], 
                                                  passwd=self.config['password'],
                                                  port=self.config['port']
                                                  )
            #self.__dbConnection.apilevel = "2.0"
            #self.__dbConnection.threadsafety = 3
            #self.__dbConnection.paramstyle = "format" 
            #self.__dbConnection.autocommit=True
            LOG.info("connect succecfull")
        except (mysql.connector.Error) as e:
            self.__dbConnection=False
            LOG.error("can't not connect to database: %s"%(e))
            self.__dbClose()  
            raise e
