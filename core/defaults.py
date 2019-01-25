'''
Created on 01.12.2018

@author: uschoen
'''

__version__='5.0'
__author__ = 'ullrich schoen'

# Standard library imports
import os
import sys

# Local application imports


class defaults():
    '''
    core events function
    '''
    def __init__(self,*args):
        self.logger.info("load core.defaults modul")

    def getCoreDefaults(self):
        defaults={
                'core':{
                    'daemon':True,
                    },
                'configuration':{
                    'basePath':"etc",
                    'filePath':self.host,
                    'files':{
                        'devices':"devices.json",
                        'module':"module.json",
                        'gateways':"gateways.json",
                        'remoteCore':"remoteCore.json",
                        'core':"config.json",
                        'logger':"logger.json"
                        }
                    }
                }
        return defaults
        
    def getLoggerDefaults(self):
        defaults={
            "disable_existing_loggers": False,
            "formatters": {
                "simple": {
                    "format": "%(asctime)s - %(name)30s - %(lineno)d - %(levelname)s - %(message)s"
                }
            },
            "handlers": {
                "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "level": "DEBUG",
            "stream": "ext://sys.stdout"
        },
                "warning_handler": {
                    "backupCount": 5,
                    "class": "logging.handlers.RotatingFileHandler",
                    "encoding": "utf8",
                    "filename": "%s/log/%s_warning.log"%(os.path.abspath(os.path.dirname(sys.argv[0])),self.host),
                    "formatter": "simple",
                    "level": "ERROR",
                    "maxBytes": 12000,
                    "mode": "a"
                }
            },
            "root": {
                "handlers": [
                    "warning_handler"                   
                ],
                "level": "WARNING"
            },
            "version": 1
        }
        return defaults