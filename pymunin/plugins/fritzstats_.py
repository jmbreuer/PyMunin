#!/usr/bin/env python
"""fritzstats - Munin Plugin to monitor Fritz!Box DSL statistics


Requirements

  - Admin credentials for accessing the Status Page of the Fritz!Box
  
  

Wild Card Plugin

  Symlink indicates IP/hostname of Fritz!Box to be monitored:
  Ex: fritzstats_fritz.box -> .../plugins/fritzstats_


Multigraph Plugin - Graph Structure

   - fritz_linerates_down
   - fritz_linerates_up
   - fritz_analog_down
   - fritz_analog_up
   - fritz_errors_down
   - fritz_errors_up

   
Environment Variables

  password:      Fritz!Box password


"""
# Munin  - Magic Markers
#%# family=auto
#%# capabilities=autoconf nosuggest

# Add our surrounding modules to the module path
import os, sys, inspect
# realpath() will make the path absolute and deal with symlinks
module_folder = os.path.split(os.path.split(os.path.split(os.path.realpath(inspect.getfile(inspect.currentframe())))[0])[0])[0]
if module_folder not in sys.path:
  sys.path.insert(0, module_folder)

from pymunin import MuninGraph, MuninPlugin, muninMain
from pysysinfo.fritz import Fritz

__author__ = "Joachim Breuer"
__copyright__ = "Copyright 2012, Joachim Breuer EDV"
__credits__ = []
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Joachim Breuer"
__email__ = "pymunin at jmbreuer.net"
__status__ = "Development"


class MuninFritzPlugin(MuninPlugin):
    """Multigraph Munin Plugin for monitoring Fritz!Box DSL parameters

    """
    plugin_name = 'fritzstats_'
    isMultigraph = True
    isMultiInstance = True

    def __init__(self, argv=(), env=None, debug=False):
        """Populate Munin Plugin with MuninGraph instances.
        
        @param argv:  List of command line arguments.
        @param env:   Dictionary of environment variables.
        @param debug: Print debugging messages if True. (Default: False)
        
        """
        MuninPlugin.__init__(self, argv, env, debug)
        self._category = "FritzBox"
        
        self._host = self.envGet('host')
        if self._host is None:
            self._host = self.arg0
        self._password = self.envGet('password')

        graph = MuninGraph("Fritz!Box %s Downstream Line Rates" % self._host, self._category,
            info="Line rate stats for Fritz!Box DSL connection (RX, kbps)",
            args="--lower-limit 0")
        graph.addField('dslam_max', 'dslam_max', type='GAUGE', info="DSLM configured maximum downstream rate")
        graph.addField('dslam_min', 'dslam_min', type='GAUGE', info="DSLM configured minimum downstream rate")
        self.appendGraph('fritz_rate_down', graph)
        
        
    def retrieveVals(self):
        """Retrieve values for graphs."""
        f = Fritz(host=self._host, password=self._password)
        data = f.readAdslData()

        self.setGraphVal('fritz_rate_down', 'dslam_max', data['gauges']['dslamMaxRateRx'])
        self.setGraphVal('fritz_rate_down', 'dslam_min', data['gauges']['dslamMinRateRx'])
        
    
    
    def autoconf(self):
        """Implements Munin Plugin Auto-Configuration Option.
        
        @return: True if plugin can be  auto-configured, False otherwise.
                 
        """
        return False


def main():
    sys.exit(muninMain(MuninFritzPlugin))


if __name__ == "__main__":
    main()
