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
from volttron.platform.vip.agent import Agent, Core, PubSub
from volttron.platform.transactions.topics import DEMAND_BID_TOPIC, BID_OFFER_TOPIC, MARKET_CLEARING_TOPIC, MARKET_STATE_TOPIC
from volttron.platform.transactions.auction import Auction
from volttron.platform.transactions.poly_line import PolyLine
from volttron.platform.transactions.point import Point

IDLE = False
INGAME = True

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
        self.name = name
        self.is_scheduler = False
        self.state = IDLE
        self.auction = Auction(name)
        self.curve = PolyLine()
        self.bid_offer_results = {}
        self.market_clearing_results = {}

    @Core.receiver("onstart")
    def onstart(self, sender, **kwargs):
        """
        Here we are making some routine while agent starting
        """
### THIS ONLY IF THIS AGENT IS FIRST
        self.vip.pubsub.publish(        #
            peer="pubusb",              #
            topic=MARKET_STATE_TOPIC,   #   
            message="demand-bid"        #
        )                               #
### THIS SECTION IS SKIPPED IN OTHER CASES

    @PubSub.subscribe("pubsub", BID_OFFER_TOPIC)
    def bid_offer_callback(self, peer, sender, bus, topic, headers, message):
        self.bid_offer_results[message["from"]] = [message["data"][0], message["data"][1]] 
        # here we are begin performing SPSBA to take market winners...
            # ...
        # ...and send SPSBA results to bidders
        self.market_clearing_results[message["from"]] = [1.0 + random.random(), 6.0 + random.random()]

    @PubSub.subscribe("pubsub", MARKET_STATE_TOPIC)
    def market_state_callback(self, peer, sender, bus, topic, headers, message):
        if sender == self.name:
            self.is_scheduler = True
        else:
            self.is_scheduler = False
        if message == "demand-bid":
            # where begin the trading cycle 
            self.state = INGAME
            self.demand_bid_trigger()
            if self.is_scheduler:
                time.sleep(5.0)
                self.vip.pubsub.publish(
                    peer="pubusb",
                    topic=MARKET_STATE_TOPIC,
                    message="bid-offer"
                )                
        elif message == "bid-offer":
            # where we are waiting for response from bidders
            self.bid_offer_trigger()
            if self.is_scheduler:
                time.sleep(5.0)
                self.vip.pubsub.publish(
                    peer="pubusb",
                    topic=MARKET_STATE_TOPIC,
                    message="market-clearing"
                )  
        elif message == "market-clearing":
        # were we are sending market clearing messages
            self.market_clearing_trigger()

    def update_curve(self):
        quants = np.linspace(0, 2, 10)
        prices = -1 * quants + 2
        if self.curve.points:
            self.curve.delete()
        for p, q in zip(prices, quants):
            self.curve.add(Point(q, p))

    def demand_bid_trigger(self):
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

    def bid_offer_trigger(self):
        pass

    def market_clearing_trigger(self):
        for bidder_name in self.market_clearing_results.keys():
            msg = {}
            msg["from"] = self.name
            msg["to"] = bidder_name
            msg["data"] = self.market_clearing_results[bidder_name]
            self.vip.pubsub.publish(
                peer="pubusb",
                topic=MARKET_CLEARING_TOPIC,
                message=msg
            )
        self.state = IDLE
        time.sleep(np.random.uniform(1.0, 5.0))
        # здесь возможно пройдет callback и мы теперь станем не IDLE
        if self.state == IDLE:
            self.vip.pubsub.publish(
                peer="pubusb",
                topic=MARKET_STATE_TOPIC,
                message="demand-bid"
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
