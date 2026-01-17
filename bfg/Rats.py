# -*- coding: utf-8 -*-
"""
Created on Sun Apr  6 09:32:33 2025

@author: HP EliteBook
"""

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

import dice

rng = np.random.default_rng()

imperial = {
    "Cobra": 30,
    "Viper": 35,
    "Sword": 35,
    "Havoc": 35,
    "Falchion": 35,
    "Firestorm": 40,
    "Siluria": 110,
    "Dauntless": 110,
    "Defiant": 120,
    "Endurance": 110,
    "Endeavour": 110,
    "Lunar": 180,
    "Gothic": 180,
    "Tyrant": 185,
    "Dominator": 190,
    "Dictator": 220,
    "Overlord": 220,
    "Armageddon": 235,
    "Mercury": 255,
    "Jovian": 260,
    "Dominion": 260,
    "Mars": 270,
    "Avenger": 200,
    "Exorcist": 230,
    "Vengeance": 230,
    "Vanquisher": 300,
    "Oberon": 335,
    "Victory": 345,
    "Retribution": 345,
    "Emperor": 365,
    "Apocalypse": 365,
}


class RAT:
    def __init__(self):
        self.members = {}
        self.dice = [dice.Dice(sides=6) for x in [1, 2]]
        
    def get(self):
        roll = sum([next(x) for x in self.dice])
        member = self.members[int(roll)]
        return member.choose()

class RATEntry:
    def __init__(self, members):
        self.members = members
    
    def choose(self):
        selection = rng.choice(self.members)

        output = self._parse_selection(selection)
        output = self._flatten_list(output)
        if isinstance(output, str):
            output = [str(output)]
        return output
    
    def _parse_selection(self, selection):
        if "+" in selection:
            select_split = selection.split("+")
            return [self._parse_selection(x) for x in select_split]
        elif "*" in selection:
            select_split = selection.split("*")
            output = [
                select_split[1] for x in range(int(select_split[0]))
                ]
            return [self._parse_selection(x) for x in output]
        else:
            return [selection]
    
    def _flatten_list(self, data):
        if isinstance(data, list):
            if len(data) == 1:
                return data[0]
            else:
                return [self._flatten_list(x) for y in data for x in y]
        else:
            return data


GothicCruisers_small = RATEntry(["Lunar", "Gothic", "Dominator", "Tyrant"])
GothicDestroyers_small = RATEntry(["4*Cobra"])
GothicMixed_small = RATEntry((["2*Cobra+2*Sword"]))
GothicFrigates_small = RATEntry(["3*Sword+1*Firestorm"])
GothicLC_small = RATEntry(["Dauntless+1*Sword"])
GothicBC_small = RATEntry(["Dictator", "Overlord"])

RATGothicSmall = RAT()
RATGothicSmall.members = {
    2: GothicLC_small,
    3: GothicDestroyers_small,
    4: GothicMixed_small,
    5: GothicMixed_small,
    6: GothicFrigates_small,
    7: GothicCruisers_small,
    8: GothicCruisers_small,
    9: GothicFrigates_small,
    10: GothicLC_small,
    11: GothicBC_small,
    12: GothicBC_small,
    }

cruisers = ["Lunar", "Gothic", "Dominator", "Tyrant", "Dictator"]
GothicCruisers = RATEntry(["+".join([x, y]) for x in cruisers for y in cruisers])
GothicDestroyers = RATEntry(["6*Cobra"])
GothicMixed = RATEntry(["2*Cobra+2*Sword"])
GothicFrigates = RATEntry(["4*Sword+2*Firestorm"])
GothicLC = RATEntry(["2*Dauntless"])
GothicBC = RATEntry(["Dictator+3*Sword", "Overlord+3*Sword",
                     "Dictator+Dauntless", "Overlord+Dauntless"])
GothicBCGCBB = RATEntry(["Mars+2*Sword", "Overlord+2*Sword"])
GothicFC = RATEntry(["Emperor", "Retribution+Sword"])

RATGothic = RAT()
RATGothic.members = {
    2: GothicFC,
    3: GothicMixed,
    4: GothicFrigates,
    5: GothicLC,
    6: GothicCruisers,
    7: GothicCruisers,
    8: GothicBC,
    9: GothicBCGCBB,
    10: GothicBCGCBB,
    11: GothicFC,
    12: GothicFC,
    }

if __name__ == "__main__":
    game_size = 500  # pts
    sel = []
    fleet_size = 0
    i = 0
    while fleet_size < game_size - 50 and i < 50:
        new_sel = RATGothicSmall.get()
        new_sel_value = sum([imperial[x] for x in new_sel])
        if fleet_size + new_sel_value < game_size - 50:
            sel += new_sel
            fleet_size += new_sel_value
        i += 1
    print(sel)
    print(sum([imperial[x] for x in sel]), i)
    
    
    game_size = 1500
    sel = []
    fleet_size = 0
    i = 0
    while fleet_size < game_size - 150 and i < 50:
        new_sel = RATGothic.get()
        new_sel_value = sum([imperial[x] for x in new_sel])
        if fleet_size + new_sel_value < game_size - 50:
            sel += new_sel
            fleet_size += new_sel_value
        i += 1
    print(sel)
    print(sum([imperial[x] for x in sel]), i)
    
    print("Cruiser swap selection:")
    print(GothicCruisers_small.choose())