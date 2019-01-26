'''
Created on 01.12.2018

@author: uschoen
'''
__version__ = '5.0'
__author__ = 'ullrich schoen'


# Standard library imports
import json
import os
import re
import importlib
import logging

# Local application imports
from .hmcException import coreException

LOG=logging.getLogger(__name__)
class base():
    
    def __init__(self,*args):
        LOG.info("load core.base modul")
        
    def writeJSON(self,fileNameABS=None,data={}):
        if fileNameABS==None:
            raise coreException("no fileNameABS given")
        try:
            LOG.info("write json file to %s"%(fileNameABS))
            with open(os.path.normpath(fileNameABS),'w') as outfile:
                json.dump(data, outfile,sort_keys=True, indent=4)
                outfile.close()
        except IOError:
            raise coreException("can not find file: %s "%(os.path.normpath(fileNameABS)))
        except ValueError:
            raise coreException("error in json find file: %s "%(os.path.normpath(fileNameABS)))
        except:
            raise coreException("unkown error in json file to write: %s"%(os.path.normpath(fileNameABS)))
                       
    def loadJSON(self,fileNameABS=None):
        '''
        loading configuration file
        '''
        if fileNameABS==None:
            raise coreException("no fileNameABS given")
        try:
            with open(os.path.normpath(fileNameABS)) as jsonDataFile:
                dateFile = json.load(jsonDataFile)
            return dateFile 
        except IOError:
            raise coreException("can not find file: %s "%(os.path.normpath(fileNameABS)))
        except ValueError:
            raise coreException("error in json file: %s "%(os.path.normpath(fileNameABS)))
        except:
            raise coreException("unkown error to read json file %s"%(os.path.normpath(fileNameABS)))
    
    def eventHome(self,pattern):
        LOG.warning("use old methode eventHome -> use ifonThisHost")
        return self.ifonThisHost(pattern)
    
    def ifonThisHost(self,objectID):
        '''
        check is objectID on this host
        
        check to parts of pattern
        
        1:
        *@*.*  deviceID@gateway.host
        2:
        *@*    name@host
        
        return true is host on thos host, else false
        '''
        try:
            if re.match('.*@.*\..*',objectID):
                ''' device id  device@gateway.host '''
                host=objectID.split("@")[1].split(".")[1]
                if host == self.host:
                    LOG.debug("objectID %s is on this host: %s"%(objectID,self.host))
                    return True
                else:
                    LOG.debug("objectID %s is not on host: %s"%(objectID,self.host))
                    return False
            
            if re.match('.*@.*',objectID):
                ''' object patter test@host '''
                host=objectID.split("@")[1]
                if host == self.host:
                    LOG.debug("objectID %s  is on host: %s"%(objectID,self.host))
                    return True
                else:
                    LOG.debug("objectID %s is not on host: %s"%(objectID,self.host))
                    return False
            LOG.error("unkown objectID pattern:%s"%(objectID))       
            return False
        except:
            LOG.error("can not format pattern %s"%(objectID),exc_info=True)
            return False
        
    def ifPathExists(self,pathABS=None):
        if pathABS==None:
            raise coreException("no path given")
        try:
            path=os.path.normpath(pathABS)
            erg=os.path.isdir(path)
            #LOG.debug("check if directory %s exists, result:%s"%(path,erg))
            return erg
        except:
            raise coreException("ifPathExists have a problem")
        
    def ifFileExists(self,fileNameABS=None):
        if fileNameABS==None:
            raise coreException("no file name given")
        try:
            filename=os.path.normpath(fileNameABS)
            erg=(os.path.exists(filename))
            #LOG.debug("check if file %s exists, result:%s"%(filename,erg))
            return erg
        except:
            raise coreException("ifFileExists have a problem")
        
    def makeDir(self,pathABS=None):
        if pathABS==None:
            raise coreException("no path  given")
        try:
            path=os.path.normpath(pathABS)
            LOG.debug("add directory %s"%(path))
            os.makedirs(path)
        except coreException as e:
            raise e
        except:
            raise coreException("can not add directory %s"%(path))
        
    def loadModul(self,pakage,modulName,modulCFG):
        """ load python pakage/module
        
        Keyword arguments:
        pakage -- pakage name 
        modulName -- the name of the gateway typ:strg
        modulCFG -- configuration of the gateway typ:direcorty as dic.
                    ['pakage'] -- pakage name
                    ['modul'] -- modul name
                    ['class'] -- class name
        
        return: class Object
        exception: yes 
        """           
        try:
            pakage=pakage+"."+modulCFG['pakage']+"."+modulCFG['modul']
            LOG.info("try to load event handler:%s with pakage: %s"%(modulName,pakage))
            ARGUMENTS = (modulCFG['config'],self)  
            module = importlib.import_module(pakage)
            CLASS_NAME = modulCFG['class']
            if hasattr(module, '__version__'):
                if module.__version__<__version__:
                    LOG.warning( "Version of %s is %s and can by to low"%(pakage,module.__version__))
                else:
                    LOG.info( "Version of %s is %s"%(pakage,module.__version__))
            else:
                LOG.warning( "pakage %s has no version Info"%(pakage))
            return getattr(module, CLASS_NAME)(*ARGUMENTS)
        except:
            raise coreException("can no load module: %s"%(pakage))  
        
    def writeFile(self,fileName,data):
        try:
            pythonFile = open(os.path.normpath(fileName),"a") 
            pythonFile.write(data)
            pythonFile.close()
        except:
            pass
     
    def checkModulVersion(self,package,module,modulVersion=__version__):
        try:
            if hasattr(module, '__version__'):
                if module.__version__<modulVersion:
                    LOG.warning("version of %s is %s and can by to low"%(package,module.__version__))
                else:
                    LOG.debug( "version of %s is %s"%(package,module.__version__))
            else:
                LOG.warning("modul %s has no version Info"%(package))
        except:
            LOG.critical("can't check modul version")   