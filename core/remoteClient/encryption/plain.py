'''
Created on 01.12.2018

@author: uschoen
'''

__version__='5.0'
__author__ = 'ullrich schoen'

# Standard library imports
import pickle as cPickle                   #@UnresolvedImport 
import logging
# Local application imports
from ..exceptions import cryptException

class plain(object):
    
    def __init__(self):
        self.logger=logging.getLogger(__name__)  
        self.logger.debug("build plain encryption")

    def serialData(self,var):
        '''
        serial data, from a json var to a string
        '''
        try:
            serialData=cPickle.dumps(var)
            return serialData
        except:
            raise cryptException("can't serial data")
    
    def unSerialData(self,serialData):
        try:
            unSerialData=cPickle.loads(serialData)
            return unSerialData 
        except:
            raise cryptException("can't unserial data")
        
    def decrypt(self,cryptstring,key=""):
        '''
        decrypt/entschluesseln a string
        '''
        try:
            plaintext=cryptstring
            var=self.unSerialData(plaintext)
            return var
        except (cryptException) as e:
            raise e
        except:
            raise cryptException( "can not decrypt message")
            
    
    def encrypt(self,var,key=""):
        '''
        encrypt/verschluesseln a var
        '''
        try:
            plaintext=self.serialData(var)   
            string=plaintext
            return string
        except (cryptException) as e:
            raise e
        except:
            raise cryptException( "can not encrypt message")
        
    
        
