from volttron.platform.transactions.point import Point

class PolyLine:
    def __init__(self) -> None:
        self.points = []
        self.norm_points = []

    def add(self, point: Point) -> None:
        self.points.append(point)

    def normalize(self, p_coeff: float, q_coeff: float) -> None:
        for point in self.points:
            self.norm_points.append(Point(point.p*p_coeff, point.q*q_coeff))
    
    def vectorize(self) -> list:
        output = []
        for point in self.points:
            output.append([point.q, point.p])
        return output

    def delete(self) -> None:
        self.points.clear()
        self.norm_points.clear()

    def is_empty(self) -> bool:
        return len(self.points) == 0
        

