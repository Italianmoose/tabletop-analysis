# -*- coding: utf-8 -*-
"""
Created on Sun Apr 23 13:02:35 2023

@author: itali
"""

import numpy as np
from matplotlib import pyplot as plt

import dice

if __name__ == '__main__':
    d12_data_1 = dice.Dice(sides=6, cache=100000).rolls
    d12_data_2 = dice.Dice(sides=6, cache=100000).rolls
    bins = list(range(1, 14))
    d12_pair = d12_data_1 + d12_data_2
    plt.hist(d12_pair, bins=bins, alpha=0.5)
    plt.xlim([2, 12])
    plt.xticks(list(range(1, 25)))