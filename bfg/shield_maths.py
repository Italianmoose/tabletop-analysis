# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 20:23:01 2025

@author: HP EliteBook
"""
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from copy import deepcopy as copy
import seaborn as sns

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

class Weapon:
    def __init__(self, strength, rangee, wb=True):
        self.wb=wb
        self.strength = strength
        self.dice = dice.Dice(sides=6, cache=int(1e5))
        self.range = rangee
    
    def roll(self, tgt=4, case=0, frac=1):
        if self.wb:
            num = int(np.ceil(gtable.loc[self.strength, case] * frac))
            return sum([next(self.dice) >= tgt for x in range(num)])
        else:
            # print("Lance")
            num = int(np.ceil(self.strength * frac))
            output = sum([next(self.dice) >= 4 for x in range(num)])
            # print(num, output)
            return output
    
    def roll_with_reroll(self, tgt=4, case=0, frac=1):
        if self.wb:
            num = int(np.ceil(gtable.loc[self.strength, case] * frac))
            rolls = sum([next(self.dice) >= tgt for x in range(num)])
            num_failed = num - rolls
            rerolls = sum([next(self.dice) >= tgt for x in range(num_failed)])
            return rolls + rerolls
        else:
            num = int(np.ceil(self.strength * frac))
            rolls = sum([next(self.dice) >= 4 for x in range(num)])
            num_failed = num - rolls
            rerolls = sum([next(self.dice) >= 4 for x in range(num_failed)])
            return rolls + rerolls


profile_default = {
    "type": "cruiser",
    "hits": 8,
    "shields": 2,
    "armour":  {
        "prow": 5,
        "side": 5,
        "rear": 5,
    },
    "turrets": 2,
    "weapons": {
        "prow": [],
        "port": [],
        "starboard": [],
        "dorsal":[],
    },
    "ld": 7,
    "points": 180,
}


class Ship:
    def __init__(self, profile=profile_default):
        self.profile = profile
        self.order = None
        self.wep_frac = 1
        self.remaining_hits = self.profile['hits']
    
    def shoot(self, tgt, distance=30, firing_side='prow', tgt_facing='prow'):
        tgt_num = tgt.profile['armour'][tgt_facing]
        match tgt_facing.lower():
            case 'prow':
                col = 2
            case 'side':
                col = 4
            case 'rear':
                col = 3
            case _:
                raise ValueError(f"Unknown tgt facing: {tgt_facing}")
        if tgt.profile['type'].lower() == 'escort':
            col += 1
        elif tgt.profile['type'].lower() == 'defence':
            col = 1
        if distance > 30:
            col += 1
        elif distance <= 15:
            col -= 1
        if col > 5:
            col = 5
        elif col < 1:
            col = 0
        if self.remaining_hits < self.profile['hits'] // 2:
            frac = self.wep_frac / 2
        else:
            frac = self.wep_frac
        if self.order == 'lock on':
            return sum(
                [x.roll_with_reroll(tgt_num, col, frac=frac) for
                 x in self.profile.weapons[firing_side] if x.range >= distance]
            )
        elif self.order and self.order != "reload ordnance":
            frac /= 2
        # print(tgt_num, col, frac)
        return sum(
            [x.roll(tgt_num, col, frac=frac) for
             x in self.profile["weapons"][firing_side]
             if x.range >= distance
             ]
        )
        

tgt_facings = ["prow", "side", "rear"]


if __name__ == "__main__":
    profile_gothic = copy(profile_default)
    profile_gothic['weapons']['port'].append(Weapon(4, 30, wb=False))
    profile_gothic['weapons']['starboard'].append(Weapon(4, 30, wb=False))
    profile_gothic['armour']['prow'] = 6
    gothic = Ship(profile=profile_gothic)
    profile_lunar = copy(profile_default)
    profile_lunar['weapons']['port'].append(Weapon(2, 30, wb=False))
    profile_lunar['weapons']['port'].append(Weapon(6, 30, wb=True))
    profile_lunar['weapons']['starboard'].append(Weapon(2, 30, wb=False))
    profile_lunar['weapons']['starboard'].append(Weapon(6, 30, wb=True))
    profile_lunar['armour']['prow'] = 6
    lunar = Ship(profile=profile_lunar)
    num_tests = int(1e5)
    ranges = 15
    # print("Gothic")
    # Need to rearrange how these are done such that we can iterate through
    # cases, print the results, and then move onto the next case
    results_gothic = []
    for i in range(num_tests):
        gothic_shoot_lunar = [
            gothic.shoot(
                lunar, distance=ranges, firing_side='port', tgt_facing=x
            ) for x in tgt_facings
        ]
        results_gothic.append([float(x) for x in gothic_shoot_lunar])
    results_gothic = np.array(results_gothic)
    
    i = 0
    results = []
    for i in range(num_tests):
        lunar_shoot = [
            lunar.shoot(
                gothic, distance=ranges, firing_side='port', tgt_facing=x
            ) for x in tgt_facings
        ]
        results.append([float(x) for x in lunar_shoot])
    results = np.array(results)
    
    i = 0
    labels = ['gothic', *tgt_facings]
    result_final = np.concat([results_gothic[:, :1], results], axis=1)
    result_final_df = pd.DataFrame(result_final, columns=labels)
    for dataset in result_final_df.columns:
        bins = list(set(result_final_df.loc[:, dataset].values))
        bins.append(bins[-1] + 1)
        histogram = np.histogram(result_final_df.loc[:, dataset].values, bins=bins, density=True)
        total = result_final_df.loc[:, dataset].values.shape[0]
        probabilities = histogram[0]  # / total
        cdf_probabilities = np.cumsum(probabilities)
        # cdf_probabilities = [probabilities[0], *cdf_probabilities]
        print(f"{dataset} at <{ranges} cm")
        for binn, val in zip(bins[:-1], cdf_probabilities[:-1]):
            if (1 - val) > 0.01:
                print(f"{binn + 1:.0f}+: {1 - val:.2f} ", end='')
        print()

