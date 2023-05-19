from point import Point

class PolyLine:
    def __init__(self) -> None:
        self.points = []
        self.norm_points = []

    def add(self, point: Point) -> None:
        self.points.append(point)

    def normalize(self, p_coeff: float, q_coeff: float) -> None:
        for point in self.points:
            self.norm_points.append(Point(point.x*p_coeff, point.y*q_coeff))

    def get_prices(self) -> list:
        prices_tmp = []
        for point in self.points:
            prices_tmp.append(point.x)
        return prices_tmp

    def get_quants(self) -> list:
        quants_tmp = []
        for point in self.points:
            quants_tmp.append(point.y)
        return quants_tmp

    def is_empty(self) -> bool:
        return len(self.points) == 0
        

