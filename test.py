from volttron.platform.transactions.poly_line import PolyLine
from volttron.platform.transactions.point import Point
import matplotlib.pyplot as plt 


curve1 = PolyLine()
curve2 = PolyLine()

curve1.add(Point(0, 0))
curve1.add(Point(1, 1))
curve2.add(Point(0, 0.5))
curve2.add(Point(1, 0.5))
curve = PolyLine.uniform([curve1, curve2])

# plt.plot(curve1.vectorize()[0], curve1.vectorize()[1])
# plt.plot(curve2.vectorize()[0], curve2.vectorize()[1])
# plt.plot(curve.vectorize()[0], curve.vectorize()[1])
# plt.show()

print(PolyLine.intersection(curve1, curve))