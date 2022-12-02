#!/usr/bin/python3

from which_pyqt import PYQT_VER

if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT4':
    from PyQt4.QtCore import QLineF, QPointF
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

from TSPClasses import *
import random


def swap_elements(el1, el2):
    temp = el1
    el1 = el2
    el2 = temp
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
        count = 0
        cities = self._scenario.getCities()
        ncities = len(cities)
        done = False
        soln = None

        start = time.time()

        while time_allowance > time.time() - start and not done:
            count += 1
            visited = [False] * ncities
            start_point = np.random.randint(0, ncities)
            route = [cities[start_point]]
            visited[start_point] = True
            next_point = None
            visit = False

            for i in range(ncities - 1):
                next_point = None
                next_dist = np.inf
                for j in range(ncities):
                    if j != i and not visited[j]:
                        if route[i].costTo(cities[j]) < next_dist:
                            next_dist = route[i].costTo(cities[j])
                            next_point = cities[j]
                            visit = j
                if next_point is None:
                    break
                else:
                    route.append(next_point)
                    visited[visit] = True

            soln = TSPSolution(route)
            if soln.cost < np.inf and next_point is not None:
                done = True

        finish = time.time()

        return {'cost': soln.cost, 'time': finish - start, 'count': count, 'soln': soln, 'max': None, 'total': None,
                'pruned': None}

    def branchAndBound(self, time_allowance=60.0):
        pass

    def fancy2(self, time_allowance=60):
        cities = self._scenario.getCities()
        ncities = len(cities)
        count = 0
        soln = self.greedy(time_allowance)['soln']
        improved = True
        iters = 0

        start = time.time()

        while time_allowance > time.time() - start and improved:
            iters += 1
            improved = False
            for i in range(ncities-1):
                for j in range(i+1, ncities):
                    route = TSPSolution(soln.route[:i] + list(reversed(soln.route[i:j + 1])) + soln.route[j + 1:])
                    if route.cost < soln.cost:
                        soln = route
                        improved = True
                        count += 1

        finish = time.time()

        return {'cost': soln.cost, 'time': finish - start, 'count': count, 'soln': soln, 'max': None, 'total': None,
                'pruned': None}

    def fancy3(self, time_allowance=60):
        cities = self._scenario.getCities()
        ncities = len(cities)
        count = 0

        soln = self.greedy(time_allowance)['soln']

        start = time.time()

        improved = True
        iters = 0

        while time_allowance > time.time() - start and improved:
            iters += 1
            improved = False
            for i in range(ncities-2):
                for j in range(i+1, ncities-1):
                    for k in range(j+1, ncities):
                        routes = [TSPSolution(soln.route[:i] + list(reversed(soln.route[i:j + 1])) + soln.route[j + 1:]),
                                  TSPSolution(soln.route[:i] + list(reversed(soln.route[i:k + 1])) + soln.route[k + 1:]),
                                  TSPSolution(soln.route[:j] + list(reversed(soln.route[j:k + 1])) + soln.route[k + 1:])]
                        for route in range(3):
                            routes.append(TSPSolution(list(reversed(routes[route].route))))
                        for route in routes:
                            if route.cost < soln.cost:
                                soln = route
                                improved = True
                                count += 1

        finish = time.time()

        return {'cost': soln.cost, 'time': finish - start, 'count': count, 'soln': soln, 'max': None, 'total': None,
                'pruned': None}

    def old_fancy2(self, time_allowance=60.0):
        cities = self._scenario.getCities()
        ncities = len(cities)
        count = 0

        soln = self.greedy(time_allowance)['soln']

        start = time.time()

        iter_since_update = 0
        done = False

        while time_allowance > time.time() - start and not done:
            start_city = random.randint(0, ncities)
            for city in range(start_city - ncities, start_city - 1):
                for neighbor in range(ncities):
                    route_to_check = soln.route

                    # swap two paths and convert to class TSPSolution
                    route_to_check[city], route_to_check[neighbor] = swap_elements(route_to_check[neighbor], route_to_check[city])
                    route_to_check = TSPSolution(route_to_check)

                    # if better than current soln, replace
                    if route_to_check.cost < soln.cost:
                        soln = route_to_check
                        count += 1
                        print(soln.cost, iter_since_update) # for debug
                        iter_since_update = 0
                    else:
                        iter_since_update += 1

                        if iter_since_update > 300000:
                            done = True
                            break

        finish = time.time()

        return {'cost': soln.cost, 'time': finish - start, 'count': count, 'soln': soln, 'max': None, 'total': None,
                'pruned': None}

    def old_fancy3(self, time_allowance=60):
        cities = self._scenario.getCities()
        ncities = len(cities)
        count = 0

        soln = self.greedy(time_allowance)['soln']

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
