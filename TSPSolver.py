#!/usr/bin/python3
import time

from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

from TSPClasses import *
import heapq



class TSPSolver:
	def __init__( self, gui_view ):
		self._scenario = None

	def setupWithScenario( self, scenario ):
		self._scenario = scenario


	''' <summary>
		This is the entry point for the default solver
		which just finds a valid random tour.  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of solution, 
		time spent to find solution, number of permutations tried during search, the 
		solution found, and three null values for fields not used for this 
		algorithm</returns> 
	'''

	def defaultRandomTour( self, time_allowance=60.0 ):
		results = {}
		cities = self._scenario.getCities()
		ncities = len(cities)
		foundTour = False
		count = 0
		bssf = None
		start_time = time.time()
		while not foundTour and time.time()-start_time < time_allowance:
			# create a random permutation
			perm = np.random.permutation( ncities )
			route = []
			# Now build the route using the random permutation
			for i in range( ncities ):
				route.append( cities[ perm[i] ] )
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


	''' <summary>
		This is the entry point for the greedy solver, which you must implement for 
		the group project (but it is probably a good idea to just do it for the branch-and
		bound project as a way to get your feet wet).  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number of solutions found, the best
		solution found, and three null values for fields not used for this 
		algorithm</returns> 
	'''

	def greedy( self,time_allowance=60.0 ):
		results = {}
		cities = self._scenario.getCities().copy()
		ncities = len(cities)
		# Pick a random city to start at.
		startIndex = random.randint(0, ncities - 1)
		startCity = cities[startIndex]
		cities.pop(startIndex)
		route = [startCity]
		start_time = time.time()
		# While the route is incomplete, and there is still time...
		while len(route) < ncities and time.time()-start_time < time_allowance:
			# Find the city with the shortest distance from the end of the path.
			minCity = None
			minIndex = None
			for i in range(len(cities)):
				currentCity = route[-1]
				# If no city has been found yet, the minCity is the first city on the list.
				if(minCity == None):
					minCity = cities[i]
					minIndex = i
				# Otherwise, if the current city is closer, set it as the minimum.
				elif currentCity.costTo(minCity) > currentCity.costTo(cities[i]):
					minCity = cities[i]
					minIndex = i
			route.append(cities.pop(minIndex))
		# If the route is incomplete (because of a time-out, or because there are no remaining valid paths),
		# then add all remaining cities to the route.
		if len(route) != ncities:
			while len(cities) > 0:
				route.append(cities.pop())
		# Stop the timer and return results.
		end_time = time.time()
		bssf = TSPSolution(route)
		results['cost'] = bssf.cost
		results['time'] = end_time - start_time
		results['count'] = 1
		results['soln'] = bssf
		results['max'] = None
		results['total'] = None
		results['pruned'] = None
		return results


	''' <summary>
		This is the entry point for the branch-and-bound algorithm that you will implement
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number solutions found during search (does
		not include the initial BSSF), the best solution found, and three more ints: 
		max queue size, total number of states created, and number of pruned states.</returns> 
	'''

	def branchAndBound( self, time_allowance=60.0 ):
		cities = self._scenario.getCities()
		ncities = len(cities)
		bssf = None
		boundCost = math.inf
		start_time = time.time()
		# Run the greedy algorithm 10 times to generate an initial solution to work with. There's no guarantee that
		# greedy will produce a viable result, but testing showed that it would usually produce a viable result
		# within 3-4 runs.
		for i in range(10):
			greedySolution = self.greedy()
			if greedySolution['cost'] < boundCost:
				boundCost = greedySolution['cost']
				bssf = greedySolution['soln']
		# Compose the initial cost array, using numpy arrays.
		defaultMatrix = []
		for i in range(ncities):
			row = []
			for j in range(ncities):
				if i == j:
					row.append(math.inf)
				else:
					row.append(cities[i].costTo(cities[j]))
			defaultMatrix.append(row)
		matrix = np.array(defaultMatrix)
		rootState = reduceMatrix(matrix)
		minCost = rootState['cost']
		# Choose a random city to start in.
		initIndex = random.randint(0, ncities-1)
		rootState = TreeState(minCost, rootState['matrix'], [], initIndex)
		# Two priority queues are being used here: first, a queue that is sorted by depth, then bound, then queue
		# insertion order, then a queue sorted by bound/(depth + 1), then insertion order. The first queue is used for
		# a depth-first search to find a viable solution, and then the more balanced queue is used to explore alternate
		# possible solutions.
		depthFirstTree = [(len(rootState.routeSoFar) * -1, rootState.getBound(), 0, rootState)]
		balancedTree = [(rootState.getBound()/(len(rootState.routeSoFar) + 1), 0, rootState)]
		heapq.heapify(depthFirstTree)
		heapq.heapify(balancedTree)
		# Metrics for the algorithm are set up.
		maxQueueSize = 1
		branchesPruned = 0
		statesCreated = 1
		statesAdded = 1
		numSolutions = 0
		dfsSolutionFound = False
		# While a dfs alternative to greedy has not been found, and there are still states to consider,
		# and there is still time...
		while not dfsSolutionFound and len(depthFirstTree) > 0 and time.time()-start_time < time_allowance:
			# Pop the next state of the dfs queue/
			currentBranch = heapq.heappop(depthFirstTree)
			currentState = currentBranch[-1]
			# Remove the corresponding state from the balanced queue.
			balancedTree.remove((currentState.getBound()/(len(currentState.routeSoFar) + 1), currentBranch[-2], currentState))
			heapq.heapify(balancedTree)
			# If the current state already visits every city, then check to see if it is a better solution than bssf.
			if len(currentState.getRoute()) == ncities:
				# If it is a better solution, then update bssf, increment the number of solutions, and exit the while loop.
				if currentState.getBound() < boundCost:
					bssf = TSPSolution(currentState.getRoute())
					boundCost = currentState.getBound()
					numSolutions += 1
					dfsSolutionFound = True
			# Otherwise, get all the children for the current state and start pruning.
			else:
				children = self.expandState(currentState)
				# Update statesCreated with the number of children provided by the last expansion.
				statesCreated += len(children)
				# For every child state...
				for state in children:
					# If the child would be worse or no better than our bssf, prune it.
					if state.getBound() >= boundCost:
						branchesPruned += 1
					# Otherwise, add it to the priority queues.
					else:
						heapq.heappush(depthFirstTree, (len(state.getRoute()) * -1, state.getBound(), statesAdded, state))
						# depthFirstTree.append((len(state.getRoute()) * -1, state.getBound(), statesAdded, state))
						heapq.heappush(balancedTree, (state.getBound()/(len(state.getRoute()) + 1), statesAdded, state))
						# Update the number of states added to the queue; this is used to keep track of queue insertion order.
						statesAdded += 1
						# balancedTree.append((state.getBound(), state))
						# Update the maximum queue size.
						maxQueueSize = max(maxQueueSize, len(depthFirstTree))
		# This loop is functionally identical to the above loop; however, it only deals with the balanced queue,
		# not with the dfs queue.
		while len(balancedTree) > 0 and time.time()-start_time < time_allowance:
			currentState = heapq.heappop(balancedTree)[-1]
			if len(currentState.getRoute()) == ncities:
				if currentState.getBound() < boundCost:
					numSolutions += 1
					bssf = TSPSolution(currentState.getRoute())
					boundCost = currentState.getBound()
			else:
				children = self.expandState(currentState)
				statesCreated += len(children)
				for state in children:
					if state.getBound() >= boundCost:
						branchesPruned += 1
					else:
						heapq.heappush(balancedTree, (state.getBound()/(len(state.getRoute()) + 1), statesAdded, state))
						statesAdded += 1
						# balancedTree.append((state.getBound(), state))
						maxQueueSize = max(maxQueueSize, len(balancedTree))
		# Package the results and return them.
		results = {'cost': bssf.cost, 'time': time.time() - start_time, 'count': numSolutions, 'soln': bssf,
				   'max': maxQueueSize, 'total': statesCreated, 'pruned': branchesPruned}
		return results

	def expandState(self, state):
		"""
		Given a state, produces all viable children of that state.
		:param state: A TreeState object containing the state of the search tree.
		:return: An array of TreeState objects that describe all viable children of the current state.
		"""
		output = []
		# The only row of the cost matrix being considered is the row corresponding to the city currently being visited.
		row = state.getMatrix()[state.getLastCity()]
		# For every city in this row...
		for i in range(len(row)):
			# If there is a path from the current city to the target city...
			if row[i] != math.inf:
				# The bound of the child will be the parent's bound + the cost of the path to the child + the cost of
				# the child's cost matrix.
				parentBound = state.getBound()
				pathCost = row[i]
				tempMatrix = state.getMatrix().copy()
				# Because this is a square matrix, operations can be done on columns and rows in the same loop.
				for j in range(len(row)):
					# Replace every item in the row with infinity.
					tempMatrix[state.getLastCity(), j] = math.inf
					# Replace every item in the column with infinity.
					tempMatrix[j, i] = math.inf
				# Replace the path from the child to the parent with infinity.
				tempMatrix[i, state.getLastCity()] = math.inf
				results = reduceMatrix(tempMatrix)
				newBound = parentBound + pathCost + results['cost']
				tempRoute = state.getRoute().copy()
				tempRoute.append(self._scenario.getCities()[i])
				child = TreeState(newBound, results['matrix'], tempRoute, i)
				output.append(child)
		return output


	''' <summary>
		This is the entry point for the algorithm you'll write for your group project.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number of solutions found during search, the 
		best solution found.  You may use the other three field however you like.
		algorithm</returns> 
	'''

	def fancy( self,time_allowance=60.0 ):
		pass


class TreeState:
	"""
	A simple container class for the members of a state in the search tree.
	"""
	def __init__(self, bound, costMatrix, routeSoFar, lastCityVisited):
		self.bound = bound						# The sum of the old reduced matrix, the path to get here, and the new reduced matrix.
		self.costMatrix = costMatrix			# The cost matrix of the tree at this point.
		self.routeSoFar = routeSoFar			# An array of City objects, where the order of the array describes the route so far.
		self.lastCityVisited = lastCityVisited  # The index of the last city visited, used when expanding a state.

	def getBound(self):
		return self.bound

	def getMatrix(self):
		return self.costMatrix

	def getRoute(self):
		return self.routeSoFar

	def getLastCity(self):
		return self.lastCityVisited


'''
	Given a matrix, returns a reduced form of that matrix, as well as the minimum cost found during reduction.
'''


def reduceMatrix(matrix):
	# Begin by copying the parent matrix and setting the reduction cost to 0
	output = matrix.copy()
	cost = 0
	# For each row in the matrix...
	for i in range(len(matrix)):
		row = output[i]
		# Find the minimum value in that row.
		minVal = min(row)
		# If the minimum value is infinite, then that corresponds to a city that has already been visited, and so
		# this row is skipped. Otherwise, add the minimum value to the cost, and subtract the minimum value from
		# every element in the row.
		if minVal != math.inf:
			cost += minVal
		for j in range(len(row)):
			if row[j] != math.inf:
				row[j] = row[j] - minVal
	# For each column in the matrix...
	for i in range(len(matrix)):
		column = output[:, i]
		# Find the minimum value in that column.
		minVal = min(column)
		# If the minimum value is infinite, then that corresponds to a city that has already been visited, and so
		# this column is skipped. Otherwise, add the minimum value to the cost, and subtract the minimum value from
		# every element in the column.
		if minVal != math.inf:
			cost += minVal
		for j in range(len(column)):
			if column[j] != math.inf:
				column[j] = column[j] - minVal
	results = {'matrix': output, 'cost': cost}
	return results
