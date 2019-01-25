'''
Created on 20.01.2018

@author: uschoen
'''

__version__ = 3.1

import logging
import time
import datetime
import threading

import coreException as hmc

class praraphser(threading.Thread):
    '''
    classdocs
    '''
    def __init__(self,core):
        threading.Thread.__init__(self)
        self.__scheduleJobs={}
        self.__conf={
            'maxProgramDeep':10
            }
        self.__core=core
        self.__CMD={
                    "condition":self.__condition,
                    "role":self.__role,
                    "value":self.__value,
                    "dateTimeNow":self.__dateTimeNow,
                    "timeNow":self.__timeNow,
                    "callerValue":self.__callerValue,
                    "=":self.__isEqual,
                    "<":self.__isLess,
                    ">":self.__isGrater,
                    "<>":self.__isUnequal,
                    "<=":self.__isLessOrEqual,
                    ">=":self.__isGraderOrEqual,
                    "or":self.__or,
                    "and":self.__and,
                    "xor":self.__xor,
                    "changeDeviceChannel":self.__changeDeviceChannel,
                    "getDeviceChannel":self.__getDeviceChannel,
                    "list":self.__list
                    
                    }
        self.__allowedCMD={
                    "root":['role','changeDeviceChannel'],
                    "role":['condition'],
                    "list":['condition','changeDeviceChannel'],
                    "condition":['sourceA','sourceB','comparison','true','false'],
                    "sourceAB":['value','condition','callerValue','getDeviceValue','dateTimeNow','timeNow'],
                    "comparison":["=","<",">","<>","<=",">=","or","and","xor"],
                    "truefalse":['list',"changeDeviceChannel"],
                    "changeDeviceChannel":["deviceID","channelName","value"],
                    "getDeviceChannel":["deviceID","channelName"],
                    "callerValue":["deviceID","channelName","eventTyp","programName","programDeep"]
                 }   
        self.__log=logging.getLogger(__name__)
        self.__log.info("buid program praraphser finsh")
        
    def parsingProgram(self,deviceID,channelName,eventTyp,programName,program,programDeep=0,test=False):
        self.__log.debug("start program %s for deviceID %s channel %s eventTyp %s"%(programName,deviceID,channelName,eventTyp))
        self.__callerValues={
                'deviceID':deviceID,
                'channelName':channelName,
                'eventTyp':eventTyp,
                'programName':programName,
                'programDeep':programDeep
                }
        if programDeep>self.__conf.get('maxProgramDeep',10):
            self.__log.error("maximum program deep (%s) is reached"%(programDeep)) 
            raise Exception
        try:
            threading.Thread(target=self.__run,args = (program)).start()
        except:
            self.__log.error("can't start program")             
     
    def __run(self,program):
        try:
            self.__root(program)
        except hmc.programException as e:
            raise e
        except:
            raise hmc.programException("some error in program %s"%(self.__callerValues.get('programName')))
    
    def __root(self,prog,cmd="root"):
       
        try:
            for field in prog:
                (field,value)=(prog.keys()[0],prog.values()[0])
                if field not in self.__allowedCMD[cmd]:
                    raise hmc.programException ("function %s is not supported in %s"%(field,cmd))
                self.__log.debug("call function %s value:%s"%(field,value))
                value=self.__CMD[field](value)
                return value
        except hmc.programException as e:
            raise e
        except:
            raise hmc.programException("build function has error: %s"%(prog))
    
    def __list(self,strg,cmd="list"):
        '''
        list function [LIST]
        '''
        try:
            self.__log.debug("call %s function"%(cmd))
            for role in strg:
                if role not in self.__allowedCMD[cmd]:
                    raise hmc.programException("function %s is not supported in %s"%(role,cmd))
                (field,value)=(strg.keys()[0],strg.values()[0])
                self.__log.debug("call function %s value:%s"%(field,value))
                self.__CMD[field](value)
        except hmc.programException as e:
            raise e
        except:
            raise  hmc.programException("%s function has error: %s"%(cmd,strg))
    
    
    def __role(self,strg,cmd="role"):
        '''
        role function [LIST]
        '''
        try:
            self.__log.debug("call %s function"%(cmd))
            for role in strg:
                if role not in self.__allowedCMD[cmd]:
                    self.__log.error("function %s is not supported in %s"%(role,cmd))
                    raise Exception
                (field,value)=(strg.keys()[0],strg.values()[0])
                self.__log.debug("call function %s value:%s"%(field,value))
                value=self.__CMD[field](value)
                return value
        except hmc.programException as e:
            raise e
        except:
            self.__log.error("%s function has error: %s"%(cmd,strg))
            
    def __isTrueFalse(self,strg,cmd="truefalse"):
        '''
        is true ore false {dic}
        ''' 
        try:
            self.__log.debug("call %s function"%(cmd))
            for job in strg:
                (field,value)=(job.keys()[0],job.values()[0])
                if field not in self.__allowedCMD[cmd]:
                    raise hmc.programException("function %s is not supported in %s"%(field,cmd))
                self.__log.debug("call function %s value:%s"%(field,value))
                value=self.__CMD[field](value)
                return value
        except hmc.programException as e:
            raise e
        except:
            self.__log.error("%s function has error: %s"%(cmd,strg))
                
    
    def __condition(self,strg,cmd='comparison'): 
        try:       
            self.__log.debug("call %s function"%(cmd)) 
            if not set(self.__allowedCMD[cmd]) <= set(strg):
                raise hmc.programException("%s function miss some atribute %s"%(cmd,strg.keys()))
            if strg.get('comparison') not in self.__allowedCMD['comparison']:
                raise hmc.programException("comparison: %s not allowed"%(strg.get(cmd)))
            valueA=self.__sourceAB(strg['sourceA'])
            valueB=self.__sourceAB(strg['sourceB'])
            self.__log.debug("A is: %s B is: %s"%(valueA,valueB))
            value=self.__CMD[strg['comparison']](valueA,valueB)
            self.__log.debug("comparison A and B is: %s"%(value))
            if value:
                strg=strg['true'] 
            else:
                strg=strg['false'] 
            value=self.__isTrueFalse(strg)
            return value
        except hmc.programException as e:
            raise e
        except:
            self.__log.error("%s function has error: %s"%(cmd,strg))
        
    def __sourceAB(self,strg): 
        '''
        source AB Function
        '''   
        self.__log.debug("call sourceA/B function")
        (field,value)=(strg.keys()[0],strg.values()[0])
        if field not in self.__allowedCMD['sourceAB']:
            raise hmc.programException("function %s is not supported in sourceAB"%(field)) 
        value=self.__CMD[field](value)
        return value 
            
    def __isLessOrEqual(self,valueA,valueB):
        '''
                check if <=
                
        return true or false
        '''        
        self.__log.debug("call isLessOrEqual function")
        try:
            if valueA<=valueB:
                return True
            return False
        except:
            raise hmc.programException("can't compare isLessOrEqual")
    
    def __isGraderOrEqual(self,valueA,valueB):
        '''
                check if >=
                
        return true or false
        '''
        self.__log.debug("call isGraderOrEqual function")
        try:
            if valueA>=valueB:
                return True
            return False
        except:
            raise hmc.programException("can't compare isGraderOrEqual")
    
    def __isEqual(self,valueA,valueB):
        '''
                check if =
                
        return true or false
        '''
        self.__log.debug("call isEqual function")
        try:
            if valueA==valueB:
                return True
            return False
        except:
            raise hmc.programException("can't compare isEqual")
        
    def __isGrater(self,valueA,valueB):
        '''
                check if >
                
        return true or false
        '''
        self.__log.debug("call isGrater function")
        try:
            if valueA>valueB:
                return True
            return False
        except:
            raise hmc.programException("can't compare isGrater")
        
    def __isLess(self,valueA,valueB):
        '''
                check if <
                
        return true or false
        '''
        self.__log.debug("call isLess function")
        try:
            if valueA<valueB:
                return True
            return False
        except:
            raise hmc.programException("can't compare isLess")
        
    def __isUnequal(self,valueA,valueB):
        '''
                check if <>
                
        return true or false
        '''
        self.__log.debug("call isUnequal function")
        try:
            if valueA<>valueB:
                return True
            return False
        except:
            raise hmc.programException("can't compare isUnequal")
    
    def __or(self,valueA,valueB):
        '''
                check if or
                
        return true or false
        '''
        self.__log.debug("call isUnequal function")
        try:
            if valueA or valueB:
                return True
            return False
        except:
            raise hmc.programException("can't compare isUnequal")

    
    def __and(self,valueA,valueB):
        '''
                check if and
                
        return true or false
        '''
        self.__log.debug("call isUnequal function")
        try:
            if valueA and valueB:
                return True
            return False
        except:
            raise hmc.programException("can't compare isUnequal")
    
    def __xor(self,valueA,valueB):
        '''
                check if xor
                
        return true or false
        '''
        self.__log.debug("call isUnequal function")
        try:
            if valueA != valueB:
                return True
            return False
        except:
            raise hmc.programException("can't compare isUnequal")

           
    def __value(self,strg):
        '''
        return a value
        '''
        self.__log.debug("call value function") 
        return strg
    
    def __changeDeviceChannel(self,strg):
        '''
        set a device Channel
        '''
        self.__log.debug("call changeDeviceChannel function")
        if not set(self.__allowedCMD['changeDeviceChannel']) <= set(strg):
            raise hmc.programException("changeDeviceChannel function miss some atribute %s"%(strg.keys()))

        (deviceID,channelName,value)=(strg.get('deviceID'),strg.get('channelName'),strg.get('value'))
        self.__log.debug("call function changeDeviceChannel %s and channelName %s to value: %s"%(deviceID,channelName,value))
        try:
            self.__core.changeDeviceChannelValue(deviceID,channelName,value)
        except hmc.programException as e:
            raise e
        except:
            raise hmc.programException("can't change deviceID %s and channelName %s to value: %s"%(deviceID,channelName,value))

        
    def __callerValue(self,strg):
        '''
        strg= Caller field
        raise all Exception   
        '''  
        self.__log.debug("call callerValue function")
        if strg not in self.__allowedCMD['getDeviceChannel']:
            raise hmc.programException("%s is not a caller variable"%(strg))
        return self.__callerValues.get(strg,"unknown")
    
    def __getDeviceChannel(self,strg):
        '''
        return a value for a device Channel
        
            raise exception on error
        '''
        self.__log.debug("call getDeviceChannel function")
        if not set(self.__allowedCMD['getDeviceChannel']) <= set(strg):
            raise hmc.programException("getDeviceChannel function miss some atribute %s"%(strg.keys()))
        (deviceID,channelName)=(strg.get('deviceID'),strg.get('channelName'))
        self.__log.debug("get value of deviceID %s and channelName:%s"%(deviceID,channelName))
        try:
            value=self.__core.getDeviceChannelValue(deviceID,channelName)
            return value
        except:
            raise hmc.programException("get no value for deviceID %s and channel %s"%(deviceID,channelName))

         
    def __dateTimeNow(self,strg=False):
        '''
        return a time stamp
        '''
        return int(time.time())
    
    def __timeNow(self,strg=False):
        '''
        return secound since midnight
        '''
        now = datetime.datetime.now()
        midnight = datetime.datetime.combine(now.date(), datetime.time())
        return (now - midnight).seconds

if __name__ == "__main__":
    
    class core():
        def __init__(self):
            pass
        def getDeviceChannelValue(self,deviceID,channelName):
            return "98"
        def setDeviceChannel(self,deviceID,channelName,value):
            print ("set deviceID %s channel %s to value %s"%(deviceID,channelName,value))
    coreDummy=core()
    log=logging.getLogger()
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    log.addHandler(ch)
    prog=praraphser(coreDummy)
    
    prog.callBack("temp@hmc", "temperatur", "onchange", "test@hmc", 0)