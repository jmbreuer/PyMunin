#!/usr/bin/env python2.7
"""fritzstats - Munin Plugin to monitor Fritz!Box DSL statistics


Requirements

  - Admin credentials for accessing the Status Page of the Fritz!Box
  
  

Wild Card Plugin

  Symlink indicates IP/hostname of Fritz!Box to be monitored:
  Ex: fritzstats_fritz.box -> .../plugins/fritzstats_


Multigraph Plugin - Graph Structure

   - fritz_rate_down
   - fritz_rate_up
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

    def addField(self, g, name, label, type=None,  draw=None, info=None, #@ReservedAssignment
                 extinfo=None, colour=None, negative=None, graph=None, 
                 min=0, max=None, cdef=None, line=None, #@ReservedAssignment
                 warning=None, critical=None):
        if type == "COUNTER" and max is None:
            max = 1000000
        g.addField(name, label, type=type, draw=draw, info=info,
            extinfo=extinfo, colour=colour, negative=negative, graph=graph,
            min=min, max=max, cdef=cdef, line=line, warning=warning, critical=critical)

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
            args="--lower-limit 0", scale=False)
        self.addField(graph, 'current', "Current", type='GAUGE', info="Currently negotiated downstream rate")
        self.addField(graph, 'capacity', "Capacity", type='GAUGE', info="Downstream line capacity")
        self.addField(graph, 'dslam_max', "DSLAM configured max", type='GAUGE', info="DSLAM configured maximum downstream rate")
        self.addField(graph, 'dslam_min', "DSLAM configured min", type='GAUGE', info="DSLAM configured minimum downstream rate")
        self.appendGraph('fritz_rate_down', graph)

        graph = MuninGraph("Fritz!Box %s Downstream Analog Parameters" % self._host, self._category,
            info="Line analog parameters for Fritz!Box DSL connection (RX)",
            args="--lower-limit 0", scale=False)
        self.addField(graph, 'latency', "Latency (ms)", type='GAUGE', info="Latency (ms)")
        self.addField(graph, 'snr', "SNR (dB)", type='GAUGE', info="SNR (dB)")
        self.addField(graph, 'inp', "Impulse Noise Protection", type='GAUGE', info="Impulse Noise Protection")
        self.addField(graph, 'attenuation', "Attenuation (dB)", type='GAUGE', info="Line Attenuation (dB)")
        self.addField(graph, 'cutback', "Power Cutback (dB)", type='GAUGE', info="Power Cutback (dB)")
        self.appendGraph('fritz_analog_down', graph)
        
        graph = MuninGraph("Fritz!Box %s Downstream Errors" % self._host, self._category,
            info="Error counts (per minute) for Fritz!Box DSL connection (RX)",
            args="--base 1000 --logarithmic", scale=False)
        self.addField(graph, 'fec_minute', "FECs", type='GAUGE', info="Forward Error Corrections (masked errors)")
        self.addField(graph, 'crc_minute', "CRCs", type='GAUGE', info="Cyclic Redundancy Checks (uncorrectable errors)")
        self.addField(graph, 'hec', "Header Errors", type='COUNTER', info="Header Error Corrections")
        self.addField(graph, 'es', "ES", type='COUNTER', info="Error Seconds")
        self.addField(graph, 'ses', "SES", type='COUNTER', info="Severe Error Seconds")
        self.addField(graph, 'ncd', "No Cell Delineations", type='COUNTER', info="No Cell Delineations")
        self.addField(graph, 'frameLoss', "Frame Loss", type='COUNTER', info="Loss of Frame")
        self.addField(graph, 'signalLoss', "Signal Loss", type='COUNTER', info="Loss of Signal")
        self.appendGraph('fritz_errors_down', graph)


        graph = MuninGraph("Fritz!Box %s Upstream Line Rates" % self._host, self._category,
            info="Line rate stats for Fritz!Box DSL connection (TX, kbps)",
            args="--lower-limit 0", scale=False)
        self.addField(graph, 'current', "Current", type='GAUGE', info="Currently negotiated upstream rate")
        self.addField(graph, 'capacity', "Capacity", type='GAUGE', info="Upstream line capacity")
        self.addField(graph, 'dslam_max', "DSLAM configured max", type='GAUGE', info="DSLAM configured maximum upstream rate")
        self.addField(graph, 'dslam_min', "DSLAM configured min", type='GAUGE', info="DSLAM configured minimum upstream rate")
        self.appendGraph('fritz_rate_up', graph)

        graph = MuninGraph("Fritz!Box %s Upstream Analog Parameters" % self._host, self._category,
            info="Line analog parameters for Fritz!Box DSL connection (TX)",
            args="--lower-limit 0", scale=False)
        self.addField(graph, 'latency', "Latency (ms)", type='GAUGE', info="Latency (ms)")
        self.addField(graph, 'snr', "SNR (dB)", type='GAUGE', info="SNR (dB)")
        self.addField(graph, 'inp', "Impulse Noise Protection", type='GAUGE', info="Impulse Noise Protection")
        self.addField(graph, 'attenuation', "Attenuation (dB)", type='GAUGE', info="Line Attenuation (dB)")
        self.addField(graph, 'cutback', "Power Cutback (dB)", type='GAUGE', info="Power Cutback (dB)")
        self.appendGraph('fritz_analog_up', graph)

        graph = MuninGraph("Fritz!Box %s Upstream Errors" % self._host, self._category,
            info="Error counts (per minute) for Fritz!Box DSL connection (TX)",
            args="--base 1000 --logarithmic", scale=False)
        self.addField(graph, 'fec_minute', "FECs", type='GAUGE', info="Forward Error Corrections (masked errors)")
        self.addField(graph, 'crc_minute', "CRCs", type='GAUGE', info="Cyclic Redundancy Checks (uncorrectable errors)")
        self.addField(graph, 'hec', "Header Errors", type='COUNTER', info="Header Error Corrections")
        self.addField(graph, 'es', "ES", type='COUNTER', info="Error Seconds")
        self.addField(graph, 'ses', "SES", type='COUNTER', info="Severe Error Seconds")
        self.addField(graph, 'ncd', "No Cell Delineations", type='COUNTER', info="No Cell Delineations")
        self.addField(graph, 'frameLoss', "Frame Loss", type='COUNTER', info="Loss of Frame")
        self.addField(graph, 'signalLoss', "Signal Loss", type='COUNTER', info="Loss of Signal")
        self.appendGraph('fritz_errors_up', graph)
        
        
    def retrieveVals(self):
        """Retrieve values for graphs."""
        f = Fritz(host=self._host, password=self._password)
        data = f.readAdslData()

        self.setGraphVal('fritz_rate_down', 'current', data['gauges']['negotiatedRateRx'])
        self.setGraphVal('fritz_rate_down', 'capacity', data['gauges']['lineCapacityRx'])
        self.setGraphVal('fritz_rate_down', 'dslam_max', data['gauges']['dslamMaxRateRx'])
        self.setGraphVal('fritz_rate_down', 'dslam_min', data['gauges']['dslamMinRateRx'])
        
        self.setGraphVal('fritz_analog_down', 'latency', data['gauges']['latencyRx'])
        self.setGraphVal('fritz_analog_down', 'snr', data['gauges']['signalNoiseRatioRx'])
        self.setGraphVal('fritz_analog_down', 'inp', data['gauges']['impulseNoiseProtectionRx'])
        self.setGraphVal('fritz_analog_down', 'attenuation', data['gauges']['attenuationRx'])
        self.setGraphVal('fritz_analog_down', 'cutback', data['gauges']['powerCutbackRx'])

        self.setGraphVal('fritz_errors_down', 'fec_minute', data['gauges']['forwardErrorCorrectionsPerMinCpe'])
        self.setGraphVal('fritz_errors_down', 'crc_minute', data['gauges']['cyclicRedundancyChecksPerMinCpe'])
        if data['counters']['headerErrorControlCpe'] >= 0:
            self.setGraphVal('fritz_errors_down', 'hec', data['counters']['headerErrorControlCpe'] * 60)
        if data['counters']['errorSecondsCpe'] >= 0:
            self.setGraphVal('fritz_errors_down', 'es', data['counters']['errorSecondsCpe'] * 60)
        if data['counters']['severeErrorSecondsCpe'] >= 0:
            self.setGraphVal('fritz_errors_down', 'ses', data['counters']['severeErrorSecondsCpe'] * 60)
        if data['counters']['noCellDelineationCpe'] >= 0:
            self.setGraphVal('fritz_errors_down', 'ncd', data['counters']['noCellDelineationCpe'] * 60)
        if data['counters']['lossOfFramesCpe'] >= 0:
            self.setGraphVal('fritz_errors_down', 'frameLoss', data['counters']['lossOfFramesCpe'] * 60)
        if data['counters']['lossOfSignalCpe'] >= 0:
            self.setGraphVal('fritz_errors_down', 'signalLoss', data['counters']['lossOfSignalCpe'] * 60)


        self.setGraphVal('fritz_rate_up', 'current', data['gauges']['negotiatedRateTx'])
        self.setGraphVal('fritz_rate_up', 'capacity', data['gauges']['lineCapacityTx'])
        self.setGraphVal('fritz_rate_up', 'dslam_max', data['gauges']['dslamMaxRateTx'])
        self.setGraphVal('fritz_rate_up', 'dslam_min', data['gauges']['dslamMinRateTx'])
        
        self.setGraphVal('fritz_analog_up', 'latency', data['gauges']['latencyTx'])
        self.setGraphVal('fritz_analog_up', 'snr', data['gauges']['signalNoiseRatioTx'])
        self.setGraphVal('fritz_analog_up', 'inp', data['gauges']['impulseNoiseProtectionTx'])
        self.setGraphVal('fritz_analog_up', 'attenuation', data['gauges']['attenuationTx'])
        self.setGraphVal('fritz_analog_up', 'cutback', data['gauges']['powerCutbackTx'])

        self.setGraphVal('fritz_errors_up', 'fec_minute', data['gauges']['forwardErrorCorrectionsPerMinCoe'])
        self.setGraphVal('fritz_errors_up', 'crc_minute', data['gauges']['cyclicRedundancyChecksPerMinCoe'])
        if data['counters']['headerErrorControlCoe'] >= 0:
            self.setGraphVal('fritz_errors_up', 'hec', data['counters']['headerErrorControlCoe'] * 60)
        if data['counters']['errorSecondsCoe'] >= 0:
            self.setGraphVal('fritz_errors_up', 'es', data['counters']['errorSecondsCoe'] * 60)
        if data['counters']['severeErrorSecondsCoe'] >= 0:
            self.setGraphVal('fritz_errors_up', 'ses', data['counters']['severeErrorSecondsCoe'] * 60)
        if data['counters']['noCellDelineationCoe'] >= 0:
            self.setGraphVal('fritz_errors_up', 'ncd', data['counters']['noCellDelineationCoe'] * 60)
        if data['counters']['lossOfFramesCoe'] >= 0:
            self.setGraphVal('fritz_errors_up', 'frameLoss', data['counters']['lossOfFramesCoe'] * 60)
        if data['counters']['lossOfSignalCoe'] >= 0:
            self.setGraphVal('fritz_errors_up', 'signalLoss', data['counters']['lossOfSignalCoe'] * 60)
    
    
    def autoconf(self):
        """Implements Munin Plugin Auto-Configuration Option.
        
        @return: True if plugin can be  auto-configured, False otherwise.
                 
        """
        return False


def main():
    sys.exit(muninMain(MuninFritzPlugin, debug=True))


if __name__ == "__main__":
    main()
