'''
Created on 18.03.2018

@author: uschoen
'''
import coreException as hmc

class program():
    
    __version__ = 3.1

    '''
    classdocs
    '''
    def addProgram(self,programName,program,forecUpdate=False):
        '''
        add a program
        '''  
        try:
            pass
            self.updateRemoteCore(forecUpdate,programName,'addProgram',programName,program)
        except:
            raise hmc.programException("unknown error in addProgramm")
    
    def updateProgram(self,programName,program,forecUpdate=False):
        '''
        update a program
        '''
        try:
            pass
            self.updateRemoteCore(forecUpdate,programName,'updateProgram',programName,program)
        except:
            raise hmc.programException("unknown error in updateProgram")
    
    def restoreProgram(self,programName,program,forceUpdate=False):
        '''
        restore a program, only for restart/start
        '''
        try:
            self.logger.debug("restore program %s"%(programName))
            if programName in self.programs:
                self.__deleteProgramm(programName=programName)
            self.__addProgram(programName=programName,program=program)
            self.updateRemoteCore(forceUpdate,programName,'restoreProgram',programName,program)
        except:
            raise hmc.programException("unknown error in restoreProgram")
    
   
    def __addProgram(self,programName,program,test=False):
        try:
            self.logger.debug("add program %s"%(programName))
            self.programs[programName]=program
        except:
            raise hmc.programException("unknown error in __addProgram")
        
    def runProgram(self,deviceID=None,channelName=None,eventTyp=None,programName=None,programDeep=0,test=False,forecUpdate=False):
        try:
            program=self.programs.get(programName)
            self.programPraraphser.parsingProgram(deviceID,channelName,eventTyp,programName,program,programDeep)
            self.updateRemoteCore(forecUpdate,programName,'runProgram',deviceID,channelName,eventTyp,programName,programDeep,test)
        except hmc.programException as e:
            raise e
        except:
            raise hmc.coreException("unknown error in runProgram")
   
    def deleteProgramm(self,programName,forecUpdate=False):
        try:
            pass
            self.updateRemoteCore(forecUpdate,programName,'deleteProgramm',programName)
        except:
            raise hmc.programException("unknown error in deleteProgramm")
    
    def __deleteProgramm(self,programName):
        try:
            if not programName in self.programs:
                return
            self.logger.info("delete program %s"%(programName))
            del self.programs[programName]
        except:
            raise hmc.programException("unknown error in __deleteProgramm")

    
    