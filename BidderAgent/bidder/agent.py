"""
Agent documentation goes here.
"""

__docformat__ = 'reStructuredText'

import logging
import sys
import numpy as np
import random
from volttron.platform.agent import utils
from volttron.platform.vip.agent import Agent, Core
from volttron.platform.transactions.topics import DEMAND_BID_TOPIC, BID_OFFER_TOPIC, MARKET_CLEARING_TOPIC, MARKET_STATE_TOPIC

_log = logging.getLogger(__name__)
utils.setup_logging()
__version__ = "0.1"


def asker(config_path, **kwargs):
    try:
        config = utils.load_config(config_path)
    except Exception:
        config = {}

    name = config.get("name", "BidderAgent")

    if not config:
        _log.info("Using Agent defaults for starting configuration.")

    return Asker(name, **kwargs)


class Asker(Agent):
    def __init__(self, name="BidderAgent", **kwargs):
        super(Asker, self).__init__(**kwargs)
        self.name = name

    @Core.receiver("onstart")
    def onstart(self, sender, **kwargs):
        """
        Here we are making some routine while agent starting
        """
        # subsribing to needed topics
        self.vip.pubsub.subscribe(
            peer="pubsub",
            prefix=DEMAND_BID_TOPIC,
            callback=self.demand_bid_callback
        )       
        self.vip.pubsub.subscribe(
            peer="pubsub",
            prefix=MARKET_CLEARING_TOPIC, 
            callback=self.market_clearing_callback
        )
        self.vip.pubsub.subscribe(
            peer="pubsub",
            prefix=MARKET_STATE_TOPIC,
            callback=self.market_state_callback
        )

    def demand_bid_callback(self, peer, sender, bus, topic, headers, message):
        """
        Here we are recieve P-Q curve from asker (sender).
        
        Then, we should perform MPO optimization and 
        send results to THIS asker.   
        """
        if message["to"] == "all":
            msg = {}
            msg["from"] = self.name
            msg["to"] = message["from"]
            msg["data"] = self.perform_mpo()
            self.vip.pubsub.publish(
                peer="pubusb",
                topic=BID_OFFER_TOPIC,
                message=msg
            )

    def market_clearing_callback(self, peer, sender, bus, topic, headers, message):
        """
        Here we are recieve pair of values (power, corresponding price)
        that asker sender will buy from this bidder.

        Then, we should infrom asker that this bidder is recieved this message. 
        This is done for correctly begin transactive cycle by askers again.
        """
        pass

    def market_state_callback(self, peer, sender, bus, topic, headers, message):
        pass

    def perform_mpo(self):
        """
        Here we are solving Markorviz Portfolio Optimization problem and returns results
        """
        return [1.0 + random.random(), -1.0 + random.random()]
    

def main():
    utils.vip_main(asker, 
                   version=__version__)


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
