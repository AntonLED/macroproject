import numpy as np
from volttron.platform.transactions.point import Point


def remove(duplicate: list) -> list:
    final_list = []
    for num in duplicate:
        if num not in final_list:
            final_list.append(num)
    return final_list

def cmp(a, b):
    return (a > b) - (a < b)

class PolyLine:
    def __init__(self):
        self.points = []
        self.xs = None
        self.ys = None
        self.xsSortedByY = None
        self.ysSortedByY = None
        self._min_x = None
        self._max_x = None
        self._min_y = None
        self._max_y = None

    def add(self, point: Point) -> None:
        if self.points is None:
            self.points = []
        if len(self.points) > 0:
            for p in reversed(self.points):
                if p.x == point.x and p.y == point.y:
                    return
        doSort = False
        if len(self.points) > 0:
            doSort = True

        self.points.append(point)
        if doSort:
            self.points.sort(key=lambda point: point.x, reverse=True)
        self.xs = None
        self.ys = None
        if point.x is not None and point.y is not None:
            self._min_x = PolyLine.min(self._min_x, point.x)
            self._min_y = PolyLine.min(self._min_y, point.y)
            self._max_x = PolyLine.max(self._max_x, point.x)
            self._max_y = PolyLine.max(self._max_y, point.y)

    def contains_none(self) -> None:
        result = False
        if self.points is not None and len(self.points) > 0:
            for p in self.points:
                if p.x is None or p.y is None:
                    result = True
        return result

    @staticmethod
    def min(x1, x2):
        if x1 is None:
            return x2
        if x2 is None:
            return x1
        return min(x1, x2)

    @staticmethod
    def max(x1, x2):
        if x1 is None:
            return x2
        if x2 is None:
            return x1
        return max(x1, x2)

    @staticmethod
    def sum(x1, x2):
        if x1 is None:
            return x2
        if x2 is None:
            return x1
        return x1 + x2

    @staticmethod
    def uniform(curves: list[Point]):
        # we return a new PolyLine which is a composite (summed horizontally) of inputs
        composite = PolyLine()
        if len(curves) < 2:
            if isinstance(curves[0], list):
                for point in curves[0]:
                    composite.add(Point(point[0], point[1]))
                return composite
            return curves[0]
        # find the range defined by the curves
        ys=[]
        for curve in curves:
            ys = ys + curve.vectorize()[1]

        ys = remove(ys)

        ys.sort(reverse=True)
        for y in ys:
            xt = None
            for curve in curves:
                x = curve.x(y)
                if x is not None:
                    xt = x if xt is None else xt + x
            composite.add(Point(xt, y))
        return composite

    def x(self, y):
        if not self.points:
            return None
        if y is None:
            return None
        self.vectorize()
        r = np.interp(y, self.ysSortedByY, self.xsSortedByY)
        return None if np.isnan(r) else r

    def y(self, x):
        if not self.points:
            return None
        if x is None:
            return None
        self.vectorize()
        r = np.interp(x, self.xs, self.ys)
        return None if np.isnan(r) else r

    # probably replace w/ zip()
    def vectorize(self) -> tuple:
        if not self.points:
            return None, None
        if (self.xs == None or self.ys == None):
            xs = [None] * len(self.points)
            ys = [None] * len(self.points)
            c = 0
            for p in self.points:
                xs[c] = p.x
                ys[c] = p.y
                c += 1
            self.xs = xs
            self.ys = ys
            if self.ys[0] < self.ys[-1]:
                self.xsSortedByY = self.xs
                self.ysSortedByY = self.ys
            else:
                self.xsSortedByY = self.xs[::-1]
                self.ysSortedByY = self.ys[::-1]
        return self.xs, self.ys

    def tuppleize(self) -> list:
        if not self.points:
            return None
        ps = [None] * len(self.points)
        c = 0
        for p in self.points:
            ps[c] = p.tuppleize()
            c += 1
        return ps

    def min_y(self):
        return self._min_y

    def max_y(self):
        return self._max_y

    def min_x(self):
        return self._min_x

    def max_x(self):
        return self._max_x

    @staticmethod
    def determinant(point1: Point, point2: Point) -> float:
        return point1.x * point2.y - point1.y * point2.x
    
    @staticmethod
    def segment_intersection(line1: list[Point], line2: list[Point]) -> tuple:
        xdiff = Point(line1[0].x - line1[1].x, line2[0].x - line2[1].x)
        ydiff = Point(line1[0].y - line1[1].y, line2[0].y - line2[1].y)
        div = PolyLine.determinant(xdiff, ydiff)
        if div == 0:
            return None, None
        d = Point(PolyLine.determinant(line1[0], line1[1]), PolyLine.determinant(line2[0], line2[1]))
        x = PolyLine.determinant(d, xdiff) / div
        y = PolyLine.determinant(d, ydiff) / div
        return x, y

    @staticmethod
    def ccw(p1: Point, p2: Point, p3: Point):
        return (p3.y - p1.y) * (p2.x - p1.x) > (p2.y - p1.y) * (p3.x - p1.x)

    @staticmethod
    def segment_intersects(l1: list[Point], l2: list[Point]) -> bool:
        if l1[0].x is None or l1[0].y is None or l1[1].x is None or l1[1].y is None:
            return False
        if l2[0].x is None or l2[0].y is None or l2[1].x is None or l2[1].y is None:
            return False
        if (PolyLine.ccw(l1[0], l2[0], l2[1]) != PolyLine.ccw(l1[1], l2[0], l2[1])
            and PolyLine.ccw(l1[0], l1[1], l2[0]) != PolyLine.ccw(l1[0], l1[1], l2[1])):
            return True
        if (l1[0].x == l2[0].x and l1[0].y == l2[0].y) or (l1[0].x == l2[1].x and l1[0].y == l2[1].y):
            return True
        if (l1[1].x == l2[0].x and l1[1].y == l2[0].y) or (l1[1].x == l2[1].x and l1[1].y == l2[1].y):
            return True

    @staticmethod
    def between(a: Point, b: Point, c: Point) -> bool:
        if (a.x is None or a.y is None or b.x is None or b.y is None or c.x is None or c.y is None):
            return None
        crossproduct = (c.y - a.y) * (b.x - a.x) - (c.x - a.x) * (b.y - a.y)
        if abs(crossproduct) > 1e-12:
            return False
        dotproduct = (c.x - a.y) * (b.x - a.x) + (c.y - a.y) * (b.y - a.y)
        if dotproduct < 0:
            return False
        squaredlengthba = (b.x - a.x) * (b.x - a.x) + (b.y - a.y) * (b.y - a.y)
        if dotproduct > squaredlengthba:
            return False
        return True

    @staticmethod
    def intersection(pl_1, pl_2) -> tuple:
        pl_1 = pl_1.points
        pl_2 = pl_2.points
        # we have two points
        if len(pl_1) == 1 and len(pl_2) == 1:
            if pl_1[0][0] == pl_2[0][0] and pl_1[0][1] == pl_2[0][1]:
                quantity = pl_1[0][0]
                price = pl_1[0][1]
                return quantity, price
        # we have one point and line segments
        elif len(pl_1) == 1 or len(pl_2) == 1:
            if len(pl_1) == 1:
                point = pl_1[0]
                line = pl_2
            else:
                point = pl_2[0]
                line = pl_1
            for j, pl_2_1 in enumerate(line[:-1]):
                pl_2_2 = line[j + 1]
                if PolyLine.between(pl_2_1, pl_2_2, point):
                    quantity = point[0]
                    price = point[1]
                    return quantity, price
        # we have line segments
        elif len(pl_1) > 1 and len(pl_2) > 1:
            for i, pl_1_1 in enumerate(pl_1[:-1]):
                pl_1_2 = pl_1[i + 1]
                for j, pl_2_1 in enumerate(pl_2[:-1]):
                    pl_2_2 = pl_2[j + 1]
                    if PolyLine.segment_intersects((pl_1_1, pl_1_2), (pl_2_1, pl_2_2)):
                        quantity, price = PolyLine.segment_intersection((pl_1_1, pl_1_2), (pl_2_1, pl_2_2))
                        return quantity, price
        p1_qmax = max([point[0] for point in pl_1])
        p1_qmin = min([point[0] for point in pl_1])

        p2_qmax = max([point[0] for point in pl_2])
        p2_qmin = min([point[0] for point in pl_2])

        p1_pmax = max([point[1] for point in pl_1])
        p2_pmax = max([point[1] for point in pl_2])

        p1_pmin = min([point[1] for point in pl_1])
        p2_pmin = min([point[1] for point in pl_2])

        if p1_pmax <= p2_pmax and p1_pmax <=p2_pmin:
            quantity = p1_qmin
            price = p2_pmax

        elif p2_pmin <=p1_pmin and p2_pmax <=p1_pmin:
            quantity = p1_qmax
            price = p2_pmin

        elif p2_qmax >= p1_qmin and p2_qmax >= p1_qmax:
            quantity = np.mean([point[0] for point in pl_1])
            price = np.mean([point[1] for point in pl_1])

        elif p2_qmin <= p1_qmin and p2_qmin <= p1_qmax:
            quantity = p2_qmax
            price = p1_pmax

        else:
            price = None
            quantity = None

        return quantity, price
