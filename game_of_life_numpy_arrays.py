# -*- coding: utf-8 -*-
"""
Created on Sat May 25 13:38:42 2019

@author: mtroyer

Conway's Game of Life - using  nnumpy arrays
"""


import numpy as np


ALIVE = '*'
EMPTY = '-'


class Grid(object):
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.grid = np.array([EMPTY] * (height*width)).reshape(height, width)
        
    def populate(self, alive_proportion):
        alive_prop = alive_proportion
        empty_prop = 1 - alive_proportion
        self.grid = np.random.choice(
                [ALIVE, EMPTY],
                self.height * self.width,
                p=[alive_prop, empty_prop]
                ).reshape(self.height, self.width)
        
    def __getitem__(self, idx):
        return self.grid[idx]

    def __setitem__(self, idx, setvalue):
        self.grid[idx] = setvalue
        
    def __repr__(self):
        return 'Grid(height={}, width={})'.format(self.height, self.width)
        
    def __str__(self):
        s = ''
        for row in self.grid:
            r = ''.join([str(val) for val in row]) + '\n'
            s+= r
        return s
#        return '\n'.join([str(row) for row in self.grid])

    def copy(self):
        new_grid = Grid(self.height, self.width)
        new_grid.grid = self.grid.copy()
        return new_grid


def update(grid):
    new_grid = grid.copy()
    w = grid.width
    h = grid.height 
    for i in range(h):  # rows
        for j in range(w):  # cols
            # Current cell state
            cell_state = grid[i, j]
            # Neighbor states
            # grid[i, j] is grid[row, col]
            n_ = grid[(i-1) % h, j]
            ne = grid[(i-1) % h, (j+1) % w]
            e_ = grid[i, (j+1) % w]
            se = grid[(i+1) % h, (j+1) % w]
            s_ = grid[(i+1) % h, j]
            sw = grid[(i+1) % h, (j-1) % w]
            w_ = grid[i, (j-1) % w]
            nw = grid[(i-1) % h, (j-1) % w]
            # compute 8-neghbor sum
            # use modulo to connect grid edges
            # i.e. a Toroidal boundary
            neighbors = [n_, ne, e_, se, s_, sw, w_, nw]
            living_neighbors = sum([1 for n in neighbors if n == ALIVE])
            # apply Conway's rules
            if cell_state  == ALIVE:
                if (living_neighbors < 2) or (living_neighbors > 3):
                    new_grid[i, j] = EMPTY  # Died
                if living_neighbors == 3:
                    new_grid[i, j] = ALIVE  # Staying alive
            else:
                if living_neighbors == 3:  # Regenerate
                    new_grid[i, j] = ALIVE
                    
    return new_grid


def game_of_life(height, width, starting_proportion=0.2, n_iterations=5, **kwargs):
    # TODO: kwargs - add predetermined shapes
    grid = Grid(height, width)
    grid.populate(starting_proportion)
    print('Starting Grid')
    print(grid)
    for iteration in range(1, n_iterations+1):
        print('Round: {}'.format(iteration))
        grid = update(grid)
        print(grid)
    return grid
    



if __name__ == '__main__':
    gol = game_of_life(20,20, n_iterations=20)
