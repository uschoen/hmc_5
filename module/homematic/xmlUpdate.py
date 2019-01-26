'''
Created on 01.12.2018

@author: uschoen


requierments:
urllib3
sudo pip3 install urlib3
sudo pip3 install xmltodict

'''

__version__='5.0'
__author__ = 'ullrich schoen'

# Standard library imports
import urllib3                                       #@UnresolvedImport,@UnusedImport
import xmltodict                                     #@UnresolvedImport,@UnusedImport
import logging
# Local application imports


class HMupdater(object):
    '''
    classdocs
    '''
    def __init__(self,modulName,modulCFG,core):
        '''
        Constructor
         '''
        self.core=core
        self.__config={
            'modulName':modulName,
            "hmHost":"http://127.0.0.1",
            "url":"/config/xmlapi/statechange.cgi"
             }
        self.__config.update(modulCFG)
        
        self.__log=logging.getLogger(__name__) 
        self.__log.debug("debug  %s instance"%(__name__))
    
    def update(self,args):
        '''
        args={
                'deviceID':None,
                'channelName':None,
                'eventTyp':None,
                modulName':modulName}
        '''
        try:
            deviceID=args.get('deviceID',"unkown")
            channelName=args.get('channelName',"unkown")
            self.__log.debug("callback from device id %s"%(deviceID))
            try:
                if not "iseID" in self.core.getAllDeviceChannelAttribute(deviceID,channelName):
                    self.__log.error("device id %s has no attribut iseID"%(deviceID))
                    return
            except:
                self.__log.error("device id %s has no iseID parameter"%(deviceID),exc_info=True)
                return
            iseID=self.core.getDeviceChannelAttributValue(deviceID,channelName,'iseID')
            url=("%s%s?ise_id=%s&new_value=%s"%(self.__config['hmHost'],self.__config['url'],iseID,self.core.getDeviceChannelValue(deviceID,channelName)))
            self.__log.info("url is %s "%(url))
            http = urllib3.PoolManager()
            response = http.request('GET', url)
            self.__log.debug("http response code %s:"%(response.data))
            httpStatus=response.status
            if  httpStatus != 200:
                self.__log.error("get html error '%s'"%(httpStatus)) 
                return
            HMresponse=xmltodict.parse(response.data)
            if "result" in HMresponse:
                if "changed" in HMresponse['result']: 
                    self.__log.debug("value successful change")
                elif "not_found" in HMresponse['result']: 
                    self.__log.error("can not found iseID %s"%(iseID))
                else:
                    self.__log.warning("get some unkown answer %s"%(response.data))
            else:
                self.__log.warning("get some unkown answer %s"%(response.data)) 
        except urllib3.URLError:
            self.__log.error("get some error at url request")
        except ValueError:
            self.__log.error("some error at request, check configuration")
        except :
            self.__log.emergency("somthing going wrong !!!")            
                
'''
<_H_Boden_Ruecklauf enable="true" ise_id="29680" sensor_id="28-011591355eff"></_H_Boden_Ruecklauf>
                                <_H_Boden_Vorlauf enable="true" ise_id="29679"   sensor_id="28-0115913432ff"></_H_Boden_Vorlauf>
                                <_H_Heizung_Vorlauf enable="true" ise_id="29681" sensor_id="28-011591363eff"></_H_Heizung_Vorlauf>
                                <_H_Koerkper_Ruecklauf enable="true" ise_id="29701" sensor_id="28-011591382fff"></_H_Koerkper_Ruecklauf>
                                <_H_Koerkper_Vorlauf enable="true" ise_id="29700" sensor_id="28-0115913679ff"></_H_Koerkper_Vorlauf>
                                <_H_Warmwasser enable="true" ise_id="29702" sensor_id="28-0315911b36ff"></_H_Warmwasser>
'''
    