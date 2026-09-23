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
        self.dice = dice.Dice(sides=6, cache=int(1e7))
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
        if not self.wb:
            tgt = 4
            num = self.strength
        else:
            num = int(np.ceil(gtable.loc[self.strength, case] * frac))
        rolls = sum([next(self.dice) >= tgt for x in range(num)])
        num_failed = num - rolls
        rerolls = sum([next(self.dice) >= tgt for x in range(num_failed)])
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
    "title": "",
}


class Ship:
    def __init__(self, profile=profile_default):
        self.profile = profile
        self.order = None
        self.wep_frac = 1
        self.remaining_hits = self.profile['hits']
    
    def shoot(self, tgt, distance=30, firing_side='prow', tgt_facing='prow',
              blast=False):
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
        if blast:
            col += 1
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
                 x in self.profile["weapons"][firing_side] if x.range >= distance]
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
    locked_on = False
    blast = True
    # ---- Gothic
    profile_gothic = copy(profile_default)
    profile_gothic['weapons']['port'].append(Weapon(4, 30, wb=False))
    profile_gothic['weapons']['starboard'].append(Weapon(4, 30, wb=False))
    profile_gothic['armour']['prow'] = 6
    profile_gothic['title'] = 'Gothic'
    gothic = Ship(profile=profile_gothic)
    # ---- Lunar
    profile_lunar = copy(profile_default)
    profile_lunar['weapons']['port'].append(Weapon(2, 30, wb=False))
    profile_lunar['weapons']['port'].append(Weapon(6, 30, wb=True))
    profile_lunar['weapons']['starboard'].append(Weapon(2, 30, wb=False))
    profile_lunar['weapons']['starboard'].append(Weapon(6, 30, wb=True))
    profile_lunar['armour']['prow'] = 6
    profile_lunar['title'] = 'Lunar'
    lunar = Ship(profile=profile_lunar)
    # ---- Dominator
    profile_dominator = copy(profile_default)
    profile_dominator['weapons']['port'].append(Weapon(12, 30, wb=True))
    profile_dominator['weapons']['starboard'].append(Weapon(12, 30, wb=True))
    profile_dominator['armour']['prow'] = 6
    profile_dominator['title'] = 'Dominator'
    dominator = Ship(profile=profile_dominator)
    # ---- Carnage
    profile_carnage = copy(profile_default)
    profile_carnage['weapons']['port'].append(Weapon(6, 45, wb=True))
    profile_carnage['weapons']['starboard'].append(Weapon(6, 45, wb=True))
    profile_carnage['weapons']['port'].append(Weapon(4, 60, wb=True))
    profile_carnage['weapons']['starboard'].append(Weapon(4, 60, wb=True))
    profile_carnage['weapons']['port'].append(Weapon(6, 60, wb=True))
    profile_carnage['title'] = 'Carnage'
    carnage = Ship(profile=profile_carnage)
    # ---- Slaughter
    profile_slaughter = copy(profile_default)
    profile_slaughter['weapons']['port'].append(Weapon(8, 30, wb=True))
    profile_slaughter['weapons']['starboard'].append(Weapon(8, 30, wb=True))
    profile_slaughter['weapons']['port'].append(Weapon(2, 30, wb=True))
    profile_slaughter['weapons']['starboard'].append(Weapon(2, 30, wb=True))
    profile_slaughter['weapons']['port'].append(Weapon(6, 30, wb=True))
    profile_slaughter['title'] = 'Slaughter'
    slaughter = Ship(profile=profile_slaughter)
    # ---- 6+ prow target
    profile_imperial_tgt = copy(profile_default)
    profile_imperial_tgt['armour']['prow'] = 6
    profile_imperial_tgt['title'] = '6+ prow target'
    imperial_tgt = Ship(profile=profile_imperial_tgt)
    # ---- 5+ prow target
    profile_chaos_tgt = copy(profile_default)
    profile_chaos_tgt['title'] = '5+ prow target'
    chaos_tgt = Ship(profile=profile_chaos_tgt)
    # ---- 4+ armour escort
    profile_escort = copy(profile_default)
    profile_escort['armour']['prow'] = 4
    profile_escort['armour']['side'] = 4
    profile_escort['armour']['rear'] = 4
    profile_escort['type'] = 'escort'
    profile_escort['title'] = '4+ escort'
    escort_tgt = Ship(profile=profile_escort)
    # ---- Ork target
    profile_ork = copy(profile_default)
    profile_ork['armour']['prow'] = 6
    profile_ork['armour']['side'] = 5
    profile_ork['armour']['rear'] = 4
    profile_ork['title'] = 'Ork'
    ork_tgt = Ship(profile=profile_ork)
    # ---- Space Marine target
    profile_marine = copy(profile_default)
    profile_marine['armour']['prow'] = 6
    profile_marine['armour']['side'] = 6
    profile_marine['armour']['rear'] = 6
    profile_marine['title'] = 'Marine'
    marine_tgt = Ship(profile=profile_marine)
    
    num_tests = int(1e4)
    ranges = [15, 30, 45, 60]
    # ranges = [15]
    tgts = [
        imperial_tgt,
        chaos_tgt,
        escort_tgt,
        ork_tgt,
        marine_tgt,
    ]
    firing_ships = [
        gothic,
        lunar,
        dominator,
        carnage,
        slaughter,
    ]
    # tgt_facings = ['rear']
    if locked_on:
        for sheep in firing_ships:
            sheep.order = 'lock on'
    results = []
    for sheep in firing_ships:
        # sheep.order = 'lock on'
        for targeet in tgts:
            for rangee in ranges:
                for face in tgt_facings:
                    interim_result = [sheep.shoot(
                        targeet,
                        distance=rangee,
                        firing_side='port',
                        tgt_facing=face,
                        blast=blast,
                    ) for x in range(num_tests)]
                    min_hits = min(interim_result)
                    min_hits_range = list(range(min_hits, 1))
                    bins = list(set(interim_result).union(min_hits_range))
                    # bins.append(bins[-1] + 1)
                    # histogram = np.histogram(interim_result, bins=bins, density=True)
                    histogram = np.array([np.count_nonzero(interim_result == x) for x in bins]).astype(float) / len(interim_result)
                    # total = len(interim_result)
                    probabilities = histogram #[0]  # / total
                    cdf_probabilities = np.cumsum(probabilities)
                    results.append(
                        {
                            'ship' : sheep.profile['title'],
                            'target': targeet.profile['title'],
                            'facing': face,
                            'range': str(rangee),
                            'results': {x + 1: 1 - y for x, y in zip(bins[:-1], cdf_probabilities[:-1])},
                        }
                    )
    results_df = pd.DataFrame(results)
    output = {}
    for ship in set(results_df.ship):
        for tgt in set(results_df.target):
            results_tmp = results_df.loc[(results_df.ship == ship) & (results_df.target == tgt)]
            results_tmp.reset_index(inplace=True, drop=True)
            results_tmp.drop(['ship', 'target'], axis=1, inplace=True)
            df = results_tmp.drop('results', axis=1).join(pd.DataFrame(results_tmp.results.values.tolist()))
# =============================================================================
#             try:
#                 df = df[~np.isnan(df.loc[:, 1])]
#             except KeyError:
#                 pass
# =============================================================================
            df.sort_values(["facing", "range"], axis=0, inplace=True)
            numerical_columns = df.columns[2:]
            df = df.loc[:, list(df.columns[:2]) + sorted(numerical_columns)]
            # df.fillna(0.0, inplace=True)
            # print(results_df.loc[(results_df.ship == ship) & (results_df.target == tgt)])
            output[f"{ship} vs. {tgt}"] = df
            print(f"{ship} vs. {tgt}", f"{'Locked on' if locked_on else ''}", f"{'with blast marker' if blast else ''}")
            print(df.to_markdown(index=False, floatfmt=".2f"))
    for key, value in output.items():
        print(key, f"{'Locked on' if locked_on else ''}", f"{'with blast marker' if blast else ''}")
        print(value.loc[:, ["facing", "range", 3]].to_markdown(index=False, floatfmt=".2f"))
# =============================================================================
#     # print("Gothic")
#     # Need to rearrange how these are done such that we can iterate through
#     # cases, print the results, and then move onto the next case
#     results_gothic = []
#     for i in range(num_tests):
#         gothic_shoot_lunar = [
#             gothic.shoot(
#                 lunar, distance=ranges, firing_side='port', tgt_facing=x
#             ) for x in tgt_facings
#         ]
#         results_gothic.append([float(x) for x in gothic_shoot_lunar])
#     results_gothic = np.array(results_gothic)
#     
#     i = 0
#     results = []
#     for i in range(num_tests):
#         lunar_shoot = [
#             lunar.shoot(
#                 gothic, distance=ranges, firing_side='port', tgt_facing=x
#             ) for x in tgt_facings
#         ]
#         results.append([float(x) for x in lunar_shoot])
#     results = np.array(results)
#     
#     i = 0
#     labels = ['gothic', *tgt_facings]
#     result_final = np.concat([results_gothic[:, :1], results], axis=1)
#     result_final_df = pd.DataFrame(result_final, columns=labels)
#     for dataset in result_final_df.columns:
#         bins = list(set(result_final_df.loc[:, dataset].values))
#         bins.append(bins[-1] + 1)
#         histogram = np.histogram(result_final_df.loc[:, dataset].values, bins=bins, density=True)
#         total = result_final_df.loc[:, dataset].values.shape[0]
#         probabilities = histogram[0]  # / total
#         cdf_probabilities = np.cumsum(probabilities)
#         # cdf_probabilities = [probabilities[0], *cdf_probabilities]
#         print(f"{dataset} at <{ranges} cm")
#         for binn, val in zip(bins[:-1], cdf_probabilities[:-1]):
#             if (1 - val) > 0.01:
#                 print(f"{binn + 1:.0f}+: {1 - val:.2f} ", end='')
#         print()
# 
# =============================================================================
