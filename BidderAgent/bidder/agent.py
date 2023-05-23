"""
Agent documentation goes here.
"""

__docformat__ = 'reStructuredText'

import logging
import sys
import numpy as np
import random
from volttron.platform.agent import utils
from volttron.platform.vip.agent import Agent, Core, PubSub
from volttron.platform.transactions.topics import DEMAND_BID_TOPIC, BID_OFFER_TOPIC, MARKET_CLEARING_TOPIC, MARKET_STATE_TOPIC
from volttron.platform.transactions.mpo_solver import Solver

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

    name = config.get("name", "BidderAgent")
    rorm = config.get("rorm", 0.0)
    price = config.get("price", 1.0)
    power = config.get("power", 0.0)

    if not config:
        _log.info("Using Agent defaults for starting configuration.")

    return Asker(name, rorm, price, power, **kwargs)


class Asker(Agent):
    def __init__(self, name="BidderAgent", rorm=0.0, price=1.0, power=0.0, **kwargs):
        super(Asker, self).__init__(**kwargs)
        self.name = name
        self.state = IDLE
        self.rorm = rorm
        self.price = price
        self.avail_power = power
        self.solver = Solver(rorm, price, power)
        self.curves = {}

    @Core.receiver("onstart")
    def onstart(self, sender, **kwargs):
        """
        Here we are making some routine while agent starting
        """
        self.state = INGAME

    @PubSub.subscribe("pubsub", MARKET_STATE_TOPIC)
    def market_state_callback(self, peer, sender, bus, topic, headers, message):
        if message == "bid-offer" and self.state == INGAME:
            tmp_curves = [curve for curve in self.curves.values()]
            results = self.perform_mpo(tmp_curves)
            for asker_name, asker_results in zip(list(self.curves.keys()), results):
                msg = {}
                msg["from"] = self.name 
                msg["to"] = asker_name
                msg["data"] = asker_results
                self.vip.pubsub.publish(
                    peer="pubsub", 
                    topic=BID_OFFER_TOPIC,
                    message=msg
                )
            # results = self.solver.solve(self.curves.values())
            # _log.debug("\n\n\n" + str(self.curves.values()) + "\n\n\n")
            # for idx, asker_name in enumerate(self.curves.keys()):
            #     msg = {}
            #     msg["from"] = self.name
            #     msg["to"] = asker_name
            #     msg["data"] = results[idx]
            #     self.vip.pubsub.publish(
            #         peer="pubsub",
            #         topic=BID_OFFER_TOPIC,
            #         message=msg
            #     )
            # self.curves.clear()


    @PubSub.subscribe("pubsub", DEMAND_BID_TOPIC)
    def demand_bid_callback(self, peer, sender, bus, topic, headers, message):
        """
        Here we are recieve P-Q curve from asker (sender).
        
        Then, we should perform MPO optimization and 
        send results to THIS asker.   
        """
        if message["to"] == "all":
            # curve = []
            # for q, p in zip(message["data"][0], message["data"][1]):
            #     curve.append([round(q, 2), round(p, 2)])
            self.curves[message["from"]] = message["data"]
            # msg = {}
            # msg["from"] = self.name
            # msg["to"] = message["from"]
            # msg["data"] = self.perform_mpo(message["data"])
            # self.vip.pubsub.publish(
            #     peer="pubusb",
            #     topic=BID_OFFER_TOPIC,
            #     message=msg
            # )
    
    @PubSub.subscribe("pubsub", MARKET_CLEARING_TOPIC)
    def market_clearing_callback(self, peer, sender, bus, topic, headers, message):
        """
        Here we are recieve pair of values (power, corresponding price)
        that asker sender will buy from this bidder.

        Then, we should infrom asker that this bidder is recieved this message. 
        This is done for correctly begin transactive cycle by askers again.
        """
        pass

    def perform_mpo(self, curves):
        """
        Here we are solving Markorvitz Portfolio Optimization problem and returns results        
        """
        # return [1.0, -1.0]
        return self.solver.solve(curves)
    

def main():
    utils.vip_main(asker, 
                   version=__version__)


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
