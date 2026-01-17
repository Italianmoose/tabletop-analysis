# -*- coding: utf-8 -*-
"""
Created on Sat Apr 22 17:33:31 2023

@author: itali

Bin covering algorithm from:
https://github.com/erelsgl/prtpy
"""

import numpy as np
import pandas as pd
import prtpy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from pathlib import Path
import sys
sys.path.append(str(Path.cwd().parent / "dice"))
import dice

class Test:
    def __init__(self, tgt_val: int=6):
        self.tgt_val = tgt_val
    
    def do(self, values, opp_vals=None):
        # Do a test with the input values and return the number of successes
        # Assumption is this is being done with d12s so no value should be
        # greater than 12
        values_tmp = np.array(values)
        successes = 0
        assert np.all(values_tmp <= 12)
        assert np.all(values_tmp > 0)
        if opp_vals:
            # Opposed test
            opp_vals_tmp = np.array(opp_vals)
            assert np.all(opp_vals_tmp <= 12)
            assert np.all(opp_vals_tmp > 0)
            successes -= np.count_nonzero(opp_vals_tmp == 12)
            values_tmp = np.setdiff1d(values_tmp, opp_vals_tmp)

        # Check for lucky 12s
        successes += np.count_nonzero(values_tmp == 12)

        # Cheating and using a bin-covering algorithm
        combos = prtpy.pack(
            algorithm=prtpy.covering.threequarters,
            binsize=self.tgt_val, items=values_tmp)
        successes += len(combos)
        
        return successes


class TestArray:
    def __init__(self, max_tgt_val: int, sides: int=12):
        self.max_tgt_val = max_tgt_val
        self.array = [Test(tgt_val=i+1) for i in range(max_tgt_val)]
        self.sides = sides
    
    def get_results(self, val: int, num_tests: int):
        # Get the results of the tests using val dice
        def roll_dice(dice):
            return [next(x) for x in dice]
        dice_list = [dice.Dice(sides=self.sides) for i in range(val)]
        results = np.zeros((len(self.array), num_tests), dtype=int)
        for i in range(num_tests):
            results[:, i] = [x.do(roll_dice(dice_list)) for x in self.array]
        results = pd.DataFrame(
            results.T, columns=[str(i+1) for
                                i in range(self.max_tgt_val)]).describe(
                                    percentiles=(0.05, 0.25, 0.5, 0.75, 0.95))
        return results.loc[("5%", "25%", "50%", "75%", "95%"), :]
    
    def get_results_array(self, max_val: int=10, num_tests: int=100):
        names = [str(i+1) for i in range(max_val)]
        results = [self.get_results(i+1, num_tests) for i in range(max_val)]
        return pd.concat(results, axis=1, keys=names, names=(
            "number of dice", "target score"))
            

def plot_results(results):
    pc25 = results.loc["25%"].unstack(level=1)
    pc50 = results.loc["50%"].unstack(level=1)
    pc75 = results.loc["75%"].unstack(level=1)
    x = pc25.columns.astype(int)
    y = pc25.index.astype(int)
    X,Y = np.meshgrid(x,y)
    Z_1 = pc25.values
    Z_2 = pc50.values
    Z_3 = pc75.values
    fig = plt.figure()
    ax = fig.add_subplot(131, projection='3d')
    ax1 = fig.add_subplot(132, projection='3d')
    ax2 = fig.add_subplot(133, projection='3d')
    ax.plot_surface(X, Y, Z_1)
    ax1.plot_surface(X, Y, Z_2)
    ax2.plot_surface(X, Y, Z_3)
    ax.set_xlabel("Target Score")
    ax.set_ylabel("Number of dice")
    ax.set_zlabel("Number of successes")
    ax.set_title("25%")
    ax1.set_xlabel("Target Score")
    ax1.set_ylabel("Number of dice")
    ax1.set_zlabel("Number of successes")
    ax1.set_title("50%")
    ax2.set_xlabel("Target Score")
    ax2.set_ylabel("Number of dice")
    ax2.set_zlabel("Number of successes")
    ax2.set_title("75%")
    plt.tight_layout()
    return pc25


if __name__ == '__main__':
    test_test = Test(tgt_val=10)
    values = [11, 10, 7, 5, 2, 4, 12]
    opp_vals = [11]
    # print(test_test.do(values, opp_vals=opp_vals))
    test_TestArray = TestArray(24, sides=6)
    # test_results = test_TestArray.get_results(5, 1000)
    test_results_arr = test_TestArray.get_results_array(
        max_val=6, num_tests=1000)
    test = plot_results(test_results_arr)
    
