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
__license__ = "LGPL"
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
        print "Logging in to "+self._host # +" with "+self._password
        default_login = 'getpage=../html/de/menus/menu2.html&errorpage=../html/index.html&var:lang=de&var:pagename=home&var:menu=home&=&login:command/password=%s'
        sid_challenge = 'getpage=../html/login_sid.xml'
        sid_login = 'login:command/response=%s&getpage=../html/login_sid.xml' 
        
        sid = urllib.urlopen("http://"+self._host+"/cgi-bin/webcm?"+sid_challenge)
        if not sid.getcode() == 200:
            raise IOError("Login challenge HTTP status "+sid.getcode()+", 200 expected")
        
        challenge = re.search('<Challenge>(.*?)</Challenge>', sid.read()).group(1)
        # print "Challenge: "+challenge
        challenge_bf = (challenge + '-' + self._password).decode('iso-8859-1').encode('utf-16le')
        m = hashlib.md5()
        m.update(challenge_bf)
        response_bf = challenge+'-'+m.hexdigest().lower()
        # print "Response: "+response_bf
        
        login = urllib.urlopen("http://"+self._host+"/cgi-bin/webcm?", sid_login % response_bf)
        if not login.getcode() == 200:
            raise IOError("Login response HTTP status "+sid.getcode()+", 200 expected")
        SID = re.search('<SID>(.*?)</SID>', login.read()).group(1)
        print "SID: "+SID
        return SID
    
    def getPage(self, pagename):
        print "Loading page "+pagename
        
        page_url = "getpage={pagename}&sid={sid}"
        
        page = urllib.urlopen("http://"+self._host+"/cgi-bin/webcm?", page_url.format(pagename=pagename, sid=self._sid))
        if not page.getcode() == 200:
            raise IOError("Get page "+pagename+" HTTP status "+sid.getcode()+", 200 expected")
        
        return page.read()
    
    def readAdslData(self):
        raw = self.getPage("../html/de/internet/adsldaten.xml")
        doc = etree.fromstring(raw)
        print etree.tostring(doc, pretty_print=True)
        
        flags = {}
        flags['dslMode'] = int(doc.xpath('/DSL/@mode')[0])
        flags['dslCarrierState'] = int(doc.xpath('/DSL/@carrierState')[0])
        flags['interleaveRx'] = int(doc.xpath('/DSL/DATA/Latenz/RX/@interleave')[0])
        flags['interleaveTx'] = int(doc.xpath('/DSL/DATA/Latenz/TX/@interleave')[0])
        flags['bitswapRx'] = int(doc.xpath('/DSL/DATA/Bitswap/@rx')[0])
        flags['bitswapTx'] = int(doc.xpath('/DSL/DATA/Bitswap/@tx')[0])
        flags['seamlessRateAdaptionRx'] = int(doc.xpath('/DSL/DATA/SeamlessRateAdaption/@rx')[0])
        flags['seamlessRateAdaptionTx'] = int(doc.xpath('/DSL/DATA/SeamlessRateAdaption/@tx')[0])
        flags['l2PowerSupported'] = int(doc.xpath('/DSL/DATA/L2PowerMode/@support')[0])
        flags['l2PowerActive'] = int(doc.xpath('/DSL/DATA/L2PowerMode/@active')[0])
        
        
        gauges = {}
        gauges['dslamMaxRateRx'] = int(doc.xpath('/DSL/DATA/MaxDslamRate/@rx')[0])
        gauges['dslamMaxRateTx'] = int(doc.xpath('/DSL/DATA/MaxDslamRate/@tx')[0])
        gauges['dslamMinRateRx'] = int(doc.xpath('/DSL/DATA/MinDslamRate/@rx')[0])
        gauges['dslamMinRateTx'] = int(doc.xpath('/DSL/DATA/MinDslamRate/@tx')[0])
        gauges['cableCapacityRx'] = int(doc.xpath('/DSL/DATA/CableCapacity/@rx')[0])
        gauges['cableCapacityTx'] = int(doc.xpath('/DSL/DATA/CableCapacity/@tx')[0])
        gauges['negotiatedRateRx'] = int(doc.xpath('/DSL/DATA/ActDataRate/@rx')[0])
        gauges['negotiatedRateTx'] = int(doc.xpath('/DSL/DATA/ActDataRate/@tx')[0])
        gauges['latencyRx'] = int(doc.xpath('/DSL/DATA/Latenz/RX/@delay')[0])
        gauges['latencyTx'] = int(doc.xpath('/DSL/DATA/Latenz/TX/@delay')[0])
        gauges['impulseNoiseProtectionRx'] = float(doc.xpath('/DSL/DATA/ImpulseNoiseProtection/@rx')[0])
        gauges['impulseNoiseProtectionTx'] = float(doc.xpath('/DSL/DATA/ImpulseNoiseProtection/@tx')[0])
        gauges['signalNoiseRatioRx'] = int(doc.xpath('/DSL/DATA/SignalNoiseDistance/@rx')[0])
        gauges['signalNoiseRatioTx'] = int(doc.xpath('/DSL/DATA/SignalNoiseDistance/@tx')[0])
        gauges['attenuationRx'] = int(doc.xpath('/DSL/DATA/LineLoss/@rx')[0])
        gauges['attenuationTx'] = int(doc.xpath('/DSL/DATA/LineLoss/@tx')[0])
        gauges['powerCutbackRx'] = int(doc.xpath('/DSL/DATA/PowerCutBack/@rx')[0])
        gauges['powerCutbackTx'] = int(doc.xpath('/DSL/DATA/PowerCutBack/@tx')[0])
        gauges['forwardErrorCorrectionsPerMinCpe'] = float(doc.xpath('/DSL/STATISTIC/FEC_min/@cpe')[0])
        gauges['forwardErrorCorrectionsPerMinCoe'] = float(doc.xpath('/DSL/STATISTIC/FEC_min/@coe')[0])
        gauges['cyclicRedundancyChecksPerMinCpe'] = float(doc.xpath('/DSL/STATISTIC/CRC_min/@cpe')[0])
        gauges['cyclicRedundancyChecksPerMinCoe'] = float(doc.xpath('/DSL/STATISTIC/CRC_min/@coe')[0])
        
        counters = {}
        counters['errorSecondsCpe'] = int(doc.xpath('/DSL/STATISTIC/ES/@cpe')[0])
        counters['errorSecondsCoe'] = int(doc.xpath('/DSL/STATISTIC/ES/@coe')[0])
        counters['severeErrorSecondsCpe'] = int(doc.xpath('/DSL/STATISTIC/SES/@cpe')[0])
        counters['severeErrorSecondsCoe'] = int(doc.xpath('/DSL/STATISTIC/SES/@coe')[0])
        counters['lossOfSignalCpe'] = int(doc.xpath('/DSL/STATISTIC/LossOfSignal/@cpe')[0])
        counters['lossOfSignalCoe'] = int(doc.xpath('/DSL/STATISTIC/LossOfSignal/@coe')[0])
        counters['lossOfFramesCpe'] = int(doc.xpath('/DSL/STATISTIC/LossOfFrames/@cpe')[0])
        counters['lossOfFramesCoe'] = int(doc.xpath('/DSL/STATISTIC/LossOfFrames/@coe')[0])
        counters['forwardErrorCorrectionsCpe'] = int(doc.xpath('/DSL/STATISTIC/FEC/@cpe')[0])
        counters['forwardErrorCorrectionsCoe'] = int(doc.xpath('/DSL/STATISTIC/FEC/@coe')[0])
        counters['cyclicRedundancyChecksCpe'] = int(doc.xpath('/DSL/STATISTIC/CRC/@cpe')[0])
        counters['cyclicRedundancyChecksCoe'] = int(doc.xpath('/DSL/STATISTIC/CRC/@coe')[0])
        counters['noCellDelineationCpe'] = int(doc.xpath('/DSL/STATISTIC/NoCellDelineation/@cpe')[0])
        counters['noCellDelineationCoe'] = int(doc.xpath('/DSL/STATISTIC/NoCellDelineation/@coe')[0])
        counters['headerErrorControlCpe'] = int(doc.xpath('/DSL/STATISTIC/HeaderErrorCtrl/@cpe')[0])
        counters['headerErrorControlCoe'] = int(doc.xpath('/DSL/STATISTIC/HeaderErrorCtrl/@coe')[0])
       
        return {'flags': flags, 'gauges': gauges, 'counters': counters}

if __name__ == '__main__':
    host = open("/tmp/fritz-host.txt", 'r').read()
    pw = open("/tmp/fritz-pw.txt", 'r').read()
    f = Fritz(host=host, password=pw)
    # print f.getPage("../html/de/internet/adsldaten.xml")
    data = f.readAdslData()
    pprint.pprint(data)

