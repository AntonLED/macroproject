import numpy as np
import cvxopt as opt
from cvxopt import matrix, spmatrix, sparse
from cvxopt.solvers import qp, options
from cvxopt import blas

class Solver():
    def __init__(self, rorm=0.0, price=1.0, power=1.0) -> None:
        self.rorm = rorm
        self.price = price
        self.power = power

    def get_price(self, curve, qs):
        #qs can be array
        ps = np.array([next((curve[1][curve[0].index(x)] for x in curve[0] if x > q),
                            0.0) for q in qs])
        return ps

    def solve(self, curves):
        """
        Desription of MPO problem and its solution is described here
        in section IV:
        J. C. Bedoya, M. Ostadijafari, C. -C. Liu and A. Dubey,
        "Decentralized Transactive Energy for Flexible Resources in
        Distribution Systems," in IEEE Transactions on Sustainable Energy,
        vol. 12, no. 2, pp. 1009-1019, April 2021,
        doi: 10.1109/TSTE.2020.3029977.
        Here is the realization of said solution algorithm.
        """
        newcurves = [np.array([[q / self.power for q in curve[0]],
                               [p / self.price for p in curve[1]]])
                     for curve in curves]
        N = 20*max([len(curve[0]) for curve in curves])
        L = len(curves)
        q_max = max(max(curve[0]) for curve in curves)
        random_qs = np.random.uniform(0, q_max, (L, N))
        random_prices = np.array([self.get_price(curves[i], random_qs[i])
                                  for i in range(L)])
        random_rorms = random_prices - 1
        mean_rorms = np.mean(random_rorms, axis=1)
        dif_matrix = np.matrix(random_rorms - mean_rorms[:, np.newaxis]).transpose()
        cov_matrix = np.matmul(dif_matrix.transpose(), dif_matrix) / N
        #we get to minimization algorithm
        n = L
        r = matrix(np.zeros(n))
        Q = matrix(cov_matrix)
        A = matrix(np.ones(n)).T
        b = matrix(1.0)
        G = np.concatenate( (-1.0 * mean_rorms[:, np.newaxis].transpose(), np.identity(n),
                            -1.0 * np.identity(n)))
        G = matrix(G)
        h = np.array([-self.rorm] + [1.0] * L + [0.0] * L)
        h = matrix(h)
        options['show_progress'] = False
        w = qp(Q, -r, G, h, A, b)['x']
        return [[weight * self.power, self.price] for weight in w]
