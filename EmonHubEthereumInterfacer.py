"""class EmonHubEthereumInterfacer
"""
import time
import json
import urllib2
import httplib
from pydispatch import dispatcher
from emonhub_interfacer import EmonHubInterfacer

class EmonHubEthereumInterfacer(EmonHubInterfacer):

    def __init__(self, name):
        # Initialization
        super(EmonHubEthereumInterfacer, self).__init__(name)

        self._name = name

        self._settings = {
            'subchannels':['ch1'],
            'pubchannels':['ch2'],

            'wallet': "",
            'senddata': 1,
            'sendstatus': 0
        }

        self.buffer = []
        self.lastsent = time.time()
        self.lastsentstatus = time.time()

    def receiver(self, cargo):

        # Create a frame of data in "emonCMS format"
        f = []
        try:
            f.append(float(cargo.timestamp))
            f.append(cargo.nodeid)
            for i in cargo.realdata:
                f.append(i)
            if cargo.rssi:
                f.append(cargo.rssi)
            self._log.debug(str(cargo.uri) + " adding frame to buffer => "+ str(f))
        except:
            self._log.warning("Failed to create emonCMS frame " + str(f))

        # Append to bulk post buffer
        self.buffer.append(f)

    def action(self):

        now = time.time()

        if int(self._settings['sendstatus']):
            self.sendstatus()

    def sendstatus(self):
        if not 'wallet' in self._settings.keys() or str.__len__(str(self._settings['wallet'])) != 32 \
                or str.lower(str(self._settings['wallet'])) == 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx':
            return

        # Connect to the light wallet
        post_url = self._settings['url']+'/myip/set.json?wallet='

        # Print info log
        self._log.info("sending: " + post_url + self._settings['wallet'])

        # add wallet
        post_url = post_url + self._settings['wallet']
        # send request
        reply = self._send_post(post_url,None)

    def set(self, **kwargs):
        for key,setting in self._settings.iteritems():
            if key in kwargs.keys():
                # replace default
                self._settings[key] = kwargs[key]

        # Subscribe to internal channels
        for channel in self._settings["subchannels"]:
            dispatcher.connect(self.receiver, channel)
            self._log.debug(self._name+" Subscribed to channel' : " + str(channel))
