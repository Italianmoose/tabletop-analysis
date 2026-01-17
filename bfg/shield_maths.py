# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 20:23:01 2025

@author: HP EliteBook
"""
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

import dice

gtable = {
    0: [  # Left Column
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
        11, 12, 13, 14, 15, 16, 17, 18,
        19, 20
    ],
    1: [  # Defences
        1, 2, 3, 4, 5, 5, 6, 7, 8, 9, 10,
        11, 12, 13, 14, 14, 15, 16, 17, 18
    ],
    2: [  # Closing Capitals
        1, 1, 2, 3, 4, 4, 5, 6, 6, 7, 8, 8,
        9, 10, 11, 11, 12, 13, 13, 14
    ],
    3: [  # Moving Away Capitals
        1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7,
        7, 8, 8, 9, 9, 10, 10
    ],
    4: [  # Abeam Capitals
        0, 1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 4,
        5, 5, 5, 6, 6, 6, 7, 7
    ],
    5: [  # Ordnance/Abeam Escorts
        0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2,
        3, 3, 3, 3, 3, 4, 4, 4
    ]
}

gtable = pd.DataFrame(gtable)
gtable.set_index(0, inplace=True)


if __name__ == "__main__":
    N = int(1e7)
    fp = 6
    tgt = 5  # Gunnery armour
    shields = 0
    col = 3
    dice_toroll = gtable.loc[fp, col]
    die = np.array([dice.Dice(sides=6, cache=N).rolls for x in range(dice_toroll)])
    # plt.hist(die)
    results = die >= tgt
    num_hits_guns = np.sum(results, axis=0)
    num_hits_guns = 0
    fp = 4
    tgt = 4
    dice_toroll = gtable.loc[fp, col]
    # die = np.array([dice.Dice(sides=6, cache=N).rolls for x in range(dice_toroll)])
    die = np.array([dice.Dice(sides=6, cache=N).rolls for x in range(fp)])
    results = die >= tgt
    num_hits_lances = np.sum(results, axis=0)
    # num_hits_lances = 0
    num_shield = np.clip(num_hits_guns + num_hits_lances, 0, shields)
    
    num_hull = np.clip(num_hits_guns + num_hits_lances - shields, 0, np.inf)
# =============================================================================
#     plt.figure("Lunar")
#     plt.hist(num_hull, bins=int(np.max(num_hull) + np.max(num_shield)) + 1, alpha=0.5)
#     plt.hist(num_shield, bins=int(np.max(num_hull) + np.max(num_shield)) + 1, alpha=0.5)
# =============================================================================
    print("Lunar")
    fom_sum = 0
    for i in range(max(num_hull.astype(int))):
        one_hull = np.count_nonzero(num_hull == i + 1)
        fom_sum += (i + 1) * one_hull / (results.shape[1])
        print(f"Probability of {i + 1} hit(s): {one_hull / (results.shape[1]):.3f}. FoM: {(i + 1) * one_hull / (results.shape[1]):.3f}")
    print(f"FoM Sum: {fom_sum:.3f}")
    
# =============================================================================
#     fp = 4
#     tgt = 4
#     die = np.array([dice.Dice(sides=6, cache=N).rolls for x in range(fp)])
#     results = die >= tgt
#     num_hits_lances = np.sum(results, axis=0)
#     num_shield = np.clip(num_hits_lances, 0, shields)
#     
#     num_hull = np.clip(num_hits_lances - shields, 0, np.inf)
# # =============================================================================
# #     plt.figure("Gothic")
# #     plt.hist(num_hull, bins=int(np.max(num_hull) + np.max(num_shield)) + 1, alpha=0.5)
# #     plt.hist(num_shield, bins=int(np.max(num_hull) + np.max(num_shield)) + 1, alpha=0.5)
# # =============================================================================
#     print("Gothic")
#     for i in range(max(num_hull.astype(int))):
#         one_hull = np.count_nonzero(num_hull == i + 1)
#         print(f"Probability of {i + 1} hit(s): {one_hull / (results.shape[1]) * 100:.2f}%")
# =============================================================================
