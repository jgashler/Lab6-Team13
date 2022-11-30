#!/usr/bin/python3

from which_pyqt import PYQT_VER

if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT4':
    from PyQt4.QtCore import QLineF, QPointF
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import time
import numpy as np
from TSPClasses import *
import heapq
import itertools
import random


def swap_elements(el1, el2):
    return el2, el1


class TSPSolver:
    def __init__(self, gui_view):
        self._scenario = None

    def setupWithScenario(self, scenario):
        self._scenario = scenario

    def defaultRandomTour(self, time_allowance=60.0):
        results = {}
        cities = self._scenario.getCities()
        ncities = len(cities)
        foundTour = False
        count = 0
        bssf = None
        start_time = time.time()
        while not foundTour and time.time() - start_time < time_allowance:
            # create a random permutation
            perm = np.random.permutation(ncities)
            route = []
            # Now build the route using the random permutation
            for i in range(ncities):
                route.append(cities[perm[i]])
            bssf = TSPSolution(route)
            count += 1
            if bssf.cost < np.inf:
                # Found a valid route
                foundTour = True
        end_time = time.time()
        results['cost'] = bssf.cost if foundTour else math.inf
        results['time'] = end_time - start_time
        results['count'] = count
        results['soln'] = bssf
        results['max'] = None
        results['total'] = None
        results['pruned'] = None
        return results

    def greedy(self, time_allowance=60.0):
        pass

    def branchAndBound(self, time_allowance=60.0):
        pass

    def fancy(self, time_allowance=60.0):
        cities = self._scenario.getCities()
        ncities = len(cities)
        count = 0

        # TODO: actually implement greedy tour and use its solution here
        soln = self.defaultRandomTour(time_allowance)['soln']

        start = time.time()

        # TODO: for some reason, adding this iteration loop makes it so the final solution does not draw lines. works otherwise
        for iteration in range(2000):
            # TODO: improve randomization. this helps, but is not perfect
            for city in range(random.randint(0, ncities), ncities):
                for neighbor in range(ncities):
                    route_to_check = soln.route

                    # swap two paths
                    temp = route_to_check[city]
                    route_to_check[city] = route_to_check[neighbor]
                    route_to_check[neighbor] = temp

                    route_to_check = TSPSolution(route_to_check)

                    # if better than current solution, replace
                    if route_to_check.cost < soln.cost:
                        soln = route_to_check
                        count += 1

        finish = time.time()

        return {'cost': soln.cost, 'time': finish - start, 'count': count, 'soln': soln, 'max': None, 'total': None,
                'pruned': None}

    def fancy3(self, time_allowance=60):
        cities = self._scenario.getCities()
        ncities = len(cities)
        count = 0

        soln = self.defaultRandomTour(time_allowance)['soln']

        start = time.time()

        for c in range(100):
            for city in range(ncities):
                for neighbor1 in range(ncities):
                    for neighbor2 in range(ncities):
                        routes = []

                        route1, route2, route3 = soln.route, soln.route, soln.route
                        route1[city], route1[neighbor1] = swap_elements(route1[neighbor1], route1[city])  # 0 1
                        route2[city], route2[neighbor2] = swap_elements(route2[neighbor2], route2[city])  # 0 2
                        route3[neighbor1], route3[neighbor2] = swap_elements(route3[neighbor2], route3[neighbor1])  # 1 2

                        routes.append(TSPSolution(route1))
                        routes.append(TSPSolution(route2))
                        routes.append(TSPSolution(route3))

                        for route in routes:
                            if route.cost < soln.cost:
                                soln = route
                                count += 1

        finish = time.time()

        return {'cost': soln.cost, 'time': finish - start, 'count': count, 'soln': soln, 'max': None, 'total': None,
                'pruned': None}
