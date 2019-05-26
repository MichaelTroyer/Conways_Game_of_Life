# -*- coding: utf-8 -*-
"""
Created on Sat May 25 13:38:42 2019

@author: mtroyer

Conway's Game of Life - using Python coroutines

adapted from Brett Slatkin's Effective Python: Item 40

This is a real brain bender..

"""
from collections import namedtuple
from numpy.random import choice


ALIVE = '*'
EMPTY = '-'

TICK = object()

Query = namedtuple('Query', ('y', 'x'))
Transition = namedtuple('Transition', ('y', 'x', 'state'))


class Grid(object):
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.rows = []
        for _ in range(self.height):
            self.rows.append([EMPTY] * self.width)
            
    def __str__(self):
        s = ''
        for row in self.rows:
            s += '|' + ''.join(row) + '|\n'
        return s
    
    def __repr__(self):
        return 'Grid({}, {})'.format(self.height, self.width)
    
    def populate(self, n_alive=10):
        xs = choice(range(self.width), n_alive)
        ys = choice(range(self.height), n_alive)
        cells = zip(xs, ys)
        for x, y in cells:
            self.assign(y, x, ALIVE)
                                           
    # query and assign use modulo to connect edges of grid
    def query(self, y, x):
        return self.rows[y % self.height][x % self.width]
    
    def assign(self, y, x, state):
        self.rows[y % self.height][x % self.width] = state

        
def game_logic(state, neighbors):
    if state == ALIVE:
        # Will stay alive if 2 or 3 neighbors
        if neighbors < 2:
            return EMPTY  # Die: too few
        elif neighbors > 3:
            return EMPTY  # Die: too many
    else:
        if neighbors == 3:
            return ALIVE  # Regenerate
    return state


def count_neighbors(y, x):
    # Count_neighbors is initialized with a x,y location
    # calls to send() expect a state and return the next query
    n_ = yield Query(y + 1, x + 0)
    ne = yield Query(y + 1, x + 1)
    e_ = yield Query(y + 0, x + 1)
    se = yield Query(y - 1, x + 1)
    s_ = yield Query(y - 1, x + 0)
    sw = yield Query(y - 1, x - 1)
    w_ = yield Query(y + 0, x - 1)
    nw = yield Query(y + 1, x - 1)
    # send() calls after this raise StopIteration and return value
    neighbors = [n_, ne, e_, se, s_, sw, w_, nw]
    return sum([1 for state in neighbors if state == ALIVE])


def step_cell(y, x):
    # current cell state
    state = yield Query(y, x)
    # Get neighbor counts
    neighbors = yield from count_neighbors(y, x)
    next_state = game_logic(state, neighbors)
    yield Transition(y, x, next_state)


def simulator(height, width):
    while True:
        for y in range(height):
            for x in range(width):
                yield from step_cell(y, x)
        yield TICK


def next_generation(grid, sim):
    # Initialize the next (empty) grid
    next_grid = Grid(grid.height, grid.width)
    # Progress to first 'yield' which will yield Query(0, 0)
    item = next(sim)
    # TICK is a sentinal value to indicate end of simulation
    while item is not TICK:
        if isinstance(item, Query):
            # Get the state of cell y, x
            state = grid.query(item.y, item.x)
            # send the state of the query coordinates
            # first to sim, which sends to step cell, 
            # which sends to count neighbors, which
            # will pass query items back up from neighbors 
            # until all the neighbors are accounted for and a 
            # transition object is returned.
            item = sim.send(state)
        # If is a transition
        else:
            next_grid.assign(item.y, item.x, item.state)
            item = next(sim)
    return next_grid


def step_generations(height=10, width=10, n_generations=10):
    grid = Grid(height, width)
    sim = simulator(height, width)
    n_alive = int((height * width) / 5.0)
    grid.populate(n_alive)
    print('Starting Grid')
    print(grid)
    for gen in range(1, n_generations+1):
        print('Generation {}'.format(gen))
        grid = next_generation(grid, sim)
        print(grid)
        
        
if __name__ == '__main__':
    step_generations(width=50, n_generations=20)
        