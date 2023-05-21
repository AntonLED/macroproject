from volttron.platform.transactions.poly_line import PolyLine
from volttron.platform.transactions.point import Point


class Auction():
    def __init__(self, name) -> None:
        self.name = name

    def get_result(self, self_demand_curve: PolyLine, bidders_curves: list[Point]) -> Point:
        try:
            aggregated_bidders_curve = PolyLine.combine_segments(bidders_curves)
            return PolyLine.intersection(self_demand_curve, aggregated_bidders_curve)
        except BaseException:
            return None
