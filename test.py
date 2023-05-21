from volttron.platform.transactions.auction import Auction, PolyLine, Point
import matplotlib.pyplot as plt 

auct = Auction("test")

curve1 = PolyLine()
curve2 = PolyLine()
curve3 = PolyLine()

_curve = PolyLine()

_curve.add(Point(0.0, 1.0+0.5))
_curve.add(Point(0.4, 1.0+0.5))
_curve.add(Point(0.4*1.0001, 0.8+0.5))
_curve.add(Point(1.0, 0.8+0.5))
_curve.add(Point(1.0*1.0001, 0.1))


curve1.add(Point(0, 1-0.15))
curve1.add(Point(1, 1-0.15))
curve2.add(Point(0, 0.5-0.15))
curve2.add(Point(0.5, 0.5-0.15))
curve3.add(Point(0, 4-0.15))
curve3.add(Point(0.2, 4-0.15))
curve = PolyLine.combine_segments([curve1, curve2, curve3])

print('\n')
print(auct.get_result(_curve, [curve1, curve2, curve3]))
print('\n')

plt.grid()
# plt.plot(curve1.vectorize()[0], curve1.vectorize()[1])
# plt.plot(curve2.vectorize()[0], curve2.vectorize()[1])
# plt.plot(curve3.vectorize()[0], curve3.vectorize()[1])
plt.plot(curve.vectorize()[0], curve.vectorize()[1])

# plt.plot(_curve.vectorize()[0], _curve.vectorize()[1], 'bo')
plt.plot(_curve.vectorize()[0], _curve.vectorize()[1])

plt.show()

