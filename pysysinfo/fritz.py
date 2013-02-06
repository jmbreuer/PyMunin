"""Implements Fritz Class for gathering stats from Fritz!Box devices.

The statistics are obtained by connecting to and querying the http
interface of the Fritz!Box 

"""

import sys, urllib, re, hashlib
import pprint
from lxml import etree

__author__ = "Joachim Breuer"
__copyright__ = "Copyright 2012, Joachim Breuer"
__credits__ = []
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Joachim Breuer"
__email__ = "pymunin at jmbreuer.net"
__status__ = "Development"


defaultHost = "fritz.box"


class Fritz:
    """Class to retrieve stats for Fritz!Box devices"""
    
    def __init__(self, host=defaultHost, password=None):
        """Log in to Fritz!Box.
        
        @param host:     Fritz!Box hostname or IP adderess
                         (Defaults to 'fritz.box' if not provided.)
        @param password: Fritz!Box Password
                         (Required for now.)
        """
        self._host = host
        self._password = password
        self._sid = self.login()

    def login(self):
        # print "Logging in to "+self._host # +" with "+self._password
        default_login = 'getpage=../html/de/menus/menu2.html&errorpage=../html/index.html&var:lang=de&var:pagename=home&var:menu=home&=&login:command/password=%s'
        
        sid = urllib.urlopen("http://"+self._host+"/login_sid.lua")
        #print "Acquiring challenge: "+sid.geturl()
        if not sid.getcode() == 200:
            raise IOError("Login challenge HTTP status "+sid.getcode()+", 200 expected")
        
        challengePage = sid.read()
        #print challengePage

        challenge = re.search('<Challenge>(.*?)</Challenge>', challengePage).group(1)
        #print "Challenge: "+challenge
        challenge_bf = (challenge + '-' + self._password).decode('iso-8859-1').encode('utf-16le')
        m = hashlib.md5()
        m.update(challenge_bf)
        response_bf = challenge+'-'+m.hexdigest().lower()
        # print "Response: "+response_bf
        
        login = urllib.urlopen("http://"+self._host+"/login_sid.lua?response="+response_bf)
        #print "Sending response: "+login.geturl()
        if not login.getcode() == 200:
            raise IOError("Login response HTTP status "+str(login.getcode())+", 200 expected")
        SID = re.search('<SID>(.*?)</SID>', login.read()).group(1)
        #print "SID: "+SID
        return SID
    
    def getPage(self, pagename):
        # print "Loading page "+pagename
        
        page_url = "{pagename}?sid={sid}"
        
        page = urllib.urlopen("http://"+self._host+"/"+page_url.format(pagename=pagename, sid=self._sid))
        # print "getPage: "+page.geturl()
        if not page.getcode() == 200:
            raise IOError("Get page "+pagename+" HTTP status "+sid.getcode()+", 200 expected")
        
        return page.read()
    
    def intFromPretty(self, value):
        if (value == "-"):
            return 0
        else:
            return int(value)
    
    def readAdslData(self):
        raw = self.getPage("internet/dsl_stats_tab.lua")
        #print "AdslData page: "+raw

        queries = re.search(r'QUERIES =[^\{]*\{([^\}]*)\}', raw, flags=re.DOTALL|re.MULTILINE)
        # print queries.group(1)

        data = {}
        for m in re.finditer(r'\["([A-Za-z:/_]*)"] = "([^\"]*)"', queries.group(1)):
            data[m.group(1)] = m.group(2)

        flags = {}
        flags['dslMode'] = int(-1)
        flags['dslCarrierState'] = int(data['sar:status/dsl_train_state'])
        flags['interleaveRx'] = int(-1)
        flags['interleaveTx'] = int(-1)
        flags['bitswapRx'] = int(data['sar:status/exp_ds_olr_Bitswap'])
        flags['bitswapTx'] = int(data['sar:status/exp_us_olr_Bitswap'])
        try:
            flags['seamlessRateAdaptionRx'] = int(data['sar:status/exp_ds_olr_SeamlessRA'])
            flags['seamlessRateAdaptionTx'] = int(data['sar:status/exp_us_olr_SeamlessRA'])
        except IndexError:
            flags['seamlessRateAdaptionRx'] = -1
            flags['seamlessRateAdaptionTx'] = -1
        flags['l2PowerSupported'] = -1
        flags['l2PowerActive'] = -1
        
        gauges = {}
        gauges['dslamMaxRateRx'] = int(data['sar:status/exp_ds_max_rate'])
        gauges['dslamMaxRateTx'] = int(data['sar:status/exp_us_max_rate'])
        gauges['dslamMinRateRx'] = int(data['sar:status/exp_ds_min_rate'])
        gauges['dslamMinRateTx'] = int(data['sar:status/exp_us_min_rate'])
        gauges['lineCapacityRx'] = int(data['sar:status/ds_attainable'])
        gauges['lineCapacityTx'] = int(data['sar:status/us_attainable'])
        gauges['negotiatedRateRx'] = int(data['sar:status/dsl_ds_rate'])
        gauges['negotiatedRateTx'] = int(data['sar:status/dsl_us_rate'])
        gauges['latencyRx'] = int(data['sar:status/ds_delay'])
        gauges['latencyTx'] = int(data['sar:status/us_delay'])
        try:
            gauges['impulseNoiseProtectionRx'] = float(data['sar:status/exp_ds_inp_act'])
            gauges['impulseNoiseProtectionTx'] = float(data['sar:status/exp_us_inp_act'])
        except IndexError:
            gauges['impulseNoiseProtectionRx'] = -1
            gauges['impulseNoiseProtectionTx'] = -1
        gauges['signalNoiseRatioRx'] = int(data['sar:status/ds_margin'])
        gauges['signalNoiseRatioTx'] = int(data['sar:status/us_margin'])
        gauges['attenuationRx'] = int(data['sar:status/ds_attenuation'])
        gauges['attenuationTx'] = int(data['sar:status/us_attenuation'])
        gauges['powerCutbackRx'] = int(data['sar:status/ds_powercutback'])
        gauges['powerCutbackTx'] = int(data['sar:status/us_powercutback'])
        gauges['forwardErrorCorrectionsPerMinCpe'] = float(data['sar:status/ds_fec_minute'])
        gauges['forwardErrorCorrectionsPerMinCoe'] = float(data['sar:status/us_fec_minute'])
        gauges['cyclicRedundancyChecksPerMinCpe'] = float(data['sar:status/ds_crc_minute'])
        gauges['cyclicRedundancyChecksPerMinCoe'] = float(data['sar:status/us_crc_minute'])
        
        counters = {}
        counters['errorSecondsCpe'] = int(data['sar:status/ds_es'])
        counters['errorSecondsCoe'] = int(data['sar:status/us_es'])
        counters['severeErrorSecondsCpe'] = int(data['sar:status/ds_ses'])
        counters['severeErrorSecondsCoe'] = int(data['sar:status/us_ses'])
        counters['lossOfSignalCpe'] = int(-1)
        counters['lossOfSignalCoe'] = int(-1)
        counters['lossOfFramesCpe'] = int(-1)
        counters['lossOfFramesCoe'] = int(-1)
        counters['forwardErrorCorrectionsCpe'] = int(-1)
        counters['forwardErrorCorrectionsCoe'] = int(-1)
        counters['cyclicRedundancyChecksCpe'] = int(-1)
        counters['cyclicRedundancyChecksCoe'] = int(-1)
        counters['noCellDelineationCpe'] = -1
        counters['noCellDelineationCoe'] = -1
        counters['headerErrorControlCpe'] = -1
        counters['headerErrorControlCoe'] = -1
       
        return {'flags': flags, 'gauges': gauges, 'counters': counters}

if __name__ == '__main__':
    host = open("/tmp/fritz-host.txt", 'r').read()
    pw = open("/tmp/fritz-pw.txt", 'r').read()
    f = Fritz(host=host, password=pw)
    # print f.getPage("../html/de/internet/adsldaten.xml")
    data = f.readAdslData()
    pprint.pprint(data)

