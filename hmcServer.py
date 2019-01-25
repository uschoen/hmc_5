#!/usr/bin/python3 -u

'''
File:hmcServer.py

Created on 01.12.2018
(C):2018
@author: ullrich schoen
@email: uschoen.hmc(@)johjoh.de
Requierment:python 3.2.3

Please use command to start:
python3 hmcServer.py 
'''
__version__='5.0'
__author__ = 'ullrich schoen'
__PYTHONVERSION__=(3,2,3)

# Standard library imports
import sys
import time
import signal
import logging.config
import argparse

# Constant
LOG=logging.getLogger(__name__)

''' 
set logging configuration
'''
logging.config.dictConfig({
            "version": 1,
            "disable_existing_LOGs": False,
            "formatters": {
                "simple": {
                    "format": "%(asctime)s %(levelname)s %(message)s"
                }
            },        
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "INFO",
                    "formatter": "simple",
                    "stream": "ext://sys.stdout"
                }
            },   
            "root": {
                "level": "INFO",
                "handlers": ["console"]
            }
        })

'''
check python version
'''
if sys.version_info <= __PYTHONVERSION__: 
    LOG.critical(__doc__)
    LOG.critical("This server have Python version is %s.%s.%s,"%(sys.version_info[:3]))
    LOG.critical("please use python version %s.%s.%s or grader."%(__PYTHONVERSION__))
    sys.exit(0)

'''
Local application imports
'''
from core.hmc import manager
from core.hmcException import coreException

'''
set signal handler
'''
def signal_handler(signum, frame):
    LOG.critical("Signal handler called with signal:%s frame:%s"%(signum,frame))
    sys.exit()
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

'''
start arguments
TODO: test start arguments
'''    
configFile=None
daemon=False
coreServer=False
try:
    parser = argparse.ArgumentParser(description='hmcServer help interface')
    parser.add_argument('--configfile','-c',help="full path of the configuration file",action="store", dest="configfile",default=None)
    parser.add_argument('--daemon','-d',help="start hmc as daemon, default true",action="store", dest="daemon",default=False) 
except:
    print("you forget some start arguments. Use -h help option"%(sys.version_info))
    sys.exit(0)
args = parser.parse_args()
configFile=args.configfile
daemon=args.daemon

'''
Main
'''
try:
    LOG.info("start up hmcServer -c %s -d %s"%(configFile,daemon)) 
    LOG.info("starting hmc core version %s"%(__version__))
    try:
        coreServer=manager(configFile)
        coreServer.daemon = True
        coreServer.start()
        LOG.debug("check if core alive")
        while True:
            if coreServer.isAlive():
                time.sleep(0.5)
            else:
                raise coreException ("core is stop !!!")
    except (SystemExit, KeyboardInterrupt):
        LOG.critical("control C press!!,system going down !!")  
    except :
        LOG.critical("unkown error:", exc_info=True)
    finally:
        LOG.critical("system going down !!")
        if coreServer:
            coreServer.shutdown() 
        LOG.critical("system is finally down !!")
        sys.exit()
except (SystemExit, KeyboardInterrupt):
    LOG.critical("control C press!!,system going down !!")  
        