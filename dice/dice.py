# -*- coding: utf-8 -*-
"""
Created on Sat Apr 22 13:19:58 2023

@author: itali
"""

from collections.abc import Generator

import numpy as np


class Dice(Generator):
    def __init__(self, sides: int=6,
                 cache: int=10000):
        # Creates a dice and sets up a big reference table of rolls
        self.sides = sides
        self.rolls = np.random.randint(1, high=sides+1, size=cache)
        self.__i = 0
        self.cache_size = cache
    
    def send(self, value):
        try:
            self.__i += 1
            return self.rolls[self.__i-1]
        except IndexError:
            # we've run out of rolls. Make more!
            self.rolls = np.random.randint(1, high=self.sides,
                                           size=self.cache_size)
            self.__i = 0
            return self.rolls[self.__i]
    
    def throw(self, typ, val=None, tb=None):
        super().throw(typ, val, tb)

if __name__ == '__main__':
    test_die = Dice(sides=12)
    for i in range(6):
        print(next(test_die))