import numpy as np


class State:

    nstates = 0

    def __init__(self, city=None, parent=None):
        """Creates a new State from a parent State. The new state has a fully 
        updated and reduced cost matrix. O(n^2) time and space. """
        # Increment the static counter of number of states
        State.nstates += 1
        if city == None:
            self.lowerbound = np.inf
            return
        self.city = city
        self.parent = parent
        self.scenario = city._scenario
        # Inherit and update data from the parent state
        if parent != None:
            self.path = parent.path + [city]
            self.cost_mat = np.copy(parent.cost_mat)
            # Remove inviable routes from the cost matrix: O(n)
            self.block_paths()
            # Reduce the cost matrix: O(n^2)
            self.reduce_cost_matrix()
        # No parent, so generate data from scenario
        else:
            self.path = [city]
            # Generate a basic cost matrix from the scenario: O(n^2)
            self.cost_mat = self.gen_cost_matrix()
            # Reduce the cost matrix: O(n^2)
            self.reduce_cost_matrix()
        # Determine which cities are unvisited: O(n^2)
        self.remaining_cities = list(set(self.scenario._cities)-set(self.path))

    def gen_cost_matrix(self):
        """Generate a base cost matrix from the scenario (only used for "root"
        states which have no parent)."""
        cities = self.scenario._cities
        # Initialize a matrix: O(n^2)
        cost_mat = np.zeros((len(cities), len(cities)))
        # Fill the matrix with cost values: O(n^2)
        for i, city1 in enumerate(cities):
            for j, city2 in enumerate(cities):
                cost_mat[i,j] = city1.costTo(city2)
        return cost_mat

    def block_paths(self):
        """Remove inviable paths from the cost matrix. O(n)"""
        # Get indices of the current and parent cities
        city_ind = self.scenario.index_of_city[self.city]
        parent_ind = self.scenario.index_of_city[self.parent.city]
        # Block paths from the parent city
        self.cost_mat[parent_ind,:] = np.inf
        # Block paths to the current city
        self.cost_mat[:,city_ind] = np.inf
        # Block the path from the current to the parent
        self.cost_mat[city_ind,parent_ind] = np.inf
        

    def reduce_cost_matrix(self):
        """ Reduce the cost matrix. O(n^2)"""
        # Obtain a vector of min values from each column: O(n^2)
        col_min = self.cost_mat.min(axis=0)
        # Replace infinities with zeros: O(n)
        col_min[col_min==np.inf] = 0
        reduction_cost = col_min.sum()
        # Subtract the min value from each column: O(n^2)
        self.cost_mat = self.cost_mat - col_min
        # Do the same for the rows: O(n^2)
        row_min = self.cost_mat.min(axis=1, keepdims = True)
        row_min[row_min==np.inf] = 0
        reduction_cost += row_min.sum()
        self.cost_mat = self.cost_mat - row_min
        # Lowerbound is sum of parent cost, reduction cost, and cost from parent to current. 
        if self.parent == None:
            self.lowerbound = reduction_cost
        else:
            city_ind = self.scenario.index_of_city[self.city]
            parent_ind = self.scenario.index_of_city[self.parent.city]
            self.lowerbound = (self.parent.get_lowerbound() + 
                        self.parent.cost_mat[parent_ind, city_ind]+ 
                        reduction_cost)
    def expand(self):
        """Retrieve all child states of the current state. Worst case O(n^3)."""
        return [State(city, self) for city in self.remaining_cities]

    def is_solution(self):
        """Determine whether or not the State is a solution to the TSP 
        problem. O(1)"""
        # Path length must equal n, and have a valid route back to start
        if len(self.path) == len(self.city._scenario._cities):
            if self.path[-1].costTo(self.path[0]) != np.inf:
                return True
        return False

    def get_priority(self):
        """Get priority for the min queue"""
        return self.lowerbound / len(self.path)

    def get_lowerbound(self):
        """Get the lowerbound cost of a complete tour based on this state"""
        return self.lowerbound

    def __lt__(self, other):
        """Return true if the priority of this state is less than the 
        priority of another state (implemented for compatibility with hepaq)"""
        return self.get_priority() < other.get_priority()






class Scenario():
    def __init__(self, cost_matrix):
        self.cost_mat = cost_matrix
        self._cities = [
            City(self, 0, 'A'),
            City(self, 1, 'B'),
            City(self, 2, 'C'),
            City(self, 3, 'D')
        ]
        self.index_of_city = {city:i for i, city in enumerate(self._cities)}
    
    def cost_from_to(self, city1, city2):
        return self.cost_mat[city1, city2]

class City():
    def __init__(self, scenario, id, name):
        self._scenario = scenario
        self._name = name
        self.id = id

    def costTo(self, other):
        return self._scenario.cost_from_to(self.id, other.id)



if __name__ == "__main__":
    pass


