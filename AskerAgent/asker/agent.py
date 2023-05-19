"""
Agent documentation goes here.
"""

__docformat__ = 'reStructuredText'

import logging
import sys
import numpy as np
import time
import random
from volttron.platform.agent import utils
from volttron.platform.vip.agent import Agent, Core
from volttron.platform.transactions.topics import DEMAND_BID_TOPIC, BID_OFFER_TOPIC, MARKET_CLEARING_TOPIC, MARKET_STATE_TOPIC
from volttron.platform.transactions.auction import Auction
from volttron.platform.transactions.poly_line import PolyLine
from volttron.platform.transactions.point import Point

_log = logging.getLogger(__name__)
utils.setup_logging()
__version__ = "0.1"


def asker(config_path, **kwargs):
    try:
        config = utils.load_config(config_path)
    except Exception:
        config = {}

    name = config.get("name", "AskerAgent")

    if not config:
        _log.info("Using Agent defaults for starting configuration.")

    return Asker(name, **kwargs)


class Asker(Agent):
    def __init__(self, name="AskerAgent", **kwargs):
        super(Asker, self).__init__(**kwargs)
        self.name = "askeragent-0.1_1"
        self.ids = ["bidderagent-0.1_1"]
        self.bids_count = len(self.ids)
        self.auction = Auction(name)
        self.curve = PolyLine()

    @Core.receiver("onstart")
    def onstart(self, sender, **kwargs):
        # subsribing to needed topics
        self.vip.pubsub.subscribe(
            peer="pubsub",
            prefix=BID_OFFER_TOPIC,
            callback=self.bid_offer_callback
        )       
        self.vip.pubsub.subscribe(
            peer="pubsub",
            prefix=MARKET_STATE_TOPIC, 
            callback=self.market_state_callback
        )
        # starting trading process: sending P-Q polyline to all bidders
        self.update_curve()
        msg = {}
        msg["from"] = self.name
        msg["to"] = "all"
        msg["data"] = self.curve.vectorize()
        self.vip.pubsub.publish(
            peer="pubusb",
            topic=DEMAND_BID_TOPIC,
            message=msg
        )

    def update_curve(self):
        quants = np.linspace(0, 2, 10)
        prices = -1 * quants + 2
        if self.curve.points:
            self.curve.delete()
        for p, q in zip(prices, quants):
            self.curve.add(Point(q, p))

    def bid_offer_callback(self, peer, sender, bus, topic, headers, message):
        # here we are begin performing SPSBA to take market winners...
        msg = {}
        msg["from"] = self.name 
        msg["to"] = message["from"]
        msg["data"] = [1.0 + random.random(), 6.0 + random.random()]
        # ...and send SPSBA results to bidders
        self.vip.pubsub.publish(
            peer="pubsub", 
            topic=MARKET_CLEARING_TOPIC,
            message=msg
        )

    def market_state_callback(self, peer, sender, bus, topic, headers, message):
        # check sender's ID
        if message["from"] in self.ids and message["data"] == "Accepted":
            self.bids_count -= 1
        # beginning trading process again
        if self.bids_count == 0:   
            self.bids_count = len(self.ids)
            time.sleep(5.0)
            self.update_curve()
            msg = {}
            msg["from"] = self.name
            msg["to"] = "all"
            msg["data"] = self.curve.vectorize()
            self.vip.pubsub.publish(
                peer="pubusb",
                topic=DEMAND_BID_TOPIC,
                message=msg
            )


def main():
    utils.vip_main(asker, 
                   version=__version__)


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
