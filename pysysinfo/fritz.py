"""Implements Fritz Class for gathering stats from Fritz!Box devices.

The statistics are obtained by connecting to and querying the http
interface of the Fritz!Box 

"""

import sys, urllib, re, hashlib

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


if __name__ == '__main__':
    host = open("/tmp/fritz-host.txt", 'r').read()
    pw = open("/tmp/fritz-pw.txt", 'r').read()
    f = Fritz(host=host, password=pw)
    print f.getPage("../html/de/internet/adsldaten.xml")
