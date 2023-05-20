from volttron.platform.transactions.auction import Auction, PolyLine, Point
import matplotlib.pyplot as plt 

auct = Auction("test")

curve1 = PolyLine()
curve2 = PolyLine()

_curve = PolyLine()
_curve.add(Point(0, 1))
_curve.add(Point(0.5, 1))
_curve.add(Point(0.5, 0.8))
_curve.add(Point(1.0, 0.8))
_curve.add(Point(1.0, 0.3))
_curve.add(Point(1.5, 0.3))
_curve.add(Point(2.0, 0.3))
_curve.add(Point(2.0, 0.1))


curve1.add(Point(0, 0))
curve1.add(Point(1, 1))
curve2.add(Point(0, 0.5))
curve2.add(Point(1, 0.5))
curve = PolyLine.uniform([curve1, curve2])

print('\n')
print(auct.get_result(_curve, [curve1, curve2]))
print('\n')

# plt.plot(curve1.vectorize()[0], curve1.vectorize()[1])
# plt.plot(curve2.vectorize()[0], curve2.vectorize()[1])
plt.grid()
plt.plot(curve.vectorize()[0], curve.vectorize()[1])
plt.plot(_curve.vectorize()[0], _curve.vectorize()[1])
plt.show()

