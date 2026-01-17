# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 19:35:43 2024

@author: itali
"""

from dice import Dice
import random

class Game:
    def __init__(self, game_map):
        self.map = game_map
    
    def play_turn(self, pwin=0.5, pmajor=0.5):
        valid_choices = [x for x in self.map.systems.values() if x.infestation]
        battle_location = self.map.systems[random.choice(valid_choices).name]
        print(f"Game in {battle_location}")
        if random.random() < (pwin):
            if random.random() < (pmajor):
                print("Is a major win")
                battle_location.infestation += 1
            else:
                print("Is a minor win")
                battle_location.infestation += 0
        else:
            if random.random() < (1-pmajor):
                print("Is a major loss")
                battle_location.infestation -= 2
            else:
                print("Is a minor loss")
                battle_location.infestation -= 1
        self.map.check_infestation()
        print("Turn done --------------")
        for entry in self.map.systems.values():
            print(entry)

class Map:
    def __init__(self):
        self.systems = {}
    
    def add_system(self, system):
        self.systems[system.name] = system
        
    def form_map(self):
        paths = {x.name: [] for x in self.systems.values()}
        for entry in self.systems.values():
            for links in entry.linked_to:
                paths[links].append(entry.name)
        for key, value in paths.items():
            self.systems[key].linked_to += value
        for value in self.systems.values():
            value.linked_to = list(set(value.linked_to))
        # Clear out disconnected systems
        for key in paths:
            if not self.systems[key].linked_to:
                del self.systems[key]
    
    def get_links(self, system_name):
        output = []
        for system in self.systems.values():
            if system_name in system.linked_to:
                output.append(system.name)
        return output
    
    def check_infestation(self):
        infestation_change = {x.name: 0 for x in self.systems.values()}
        d6 = Dice(sides=6)
        for system in self.systems.values():
            if system.infestation >= 6 and not system.lost:
                print(f"System {system.name} is lost")
                system.lost = True
            elif system.infestation < 0:
                system.infestation = 0
            
            if next(d6) >= 6:
                if not system.lost:
                    print(f"System {system.name} gains infestation")
                    infestation_change[system.name] += 1
            
            for i in range(system.infestation):
                roll = next(d6)
                
                if roll <= 2:
                    spread = random.choice(
                        self.get_links(system.name))
                    print(f"Infestation spreads from {system.name} to {spread}")
                    infestation_change[system.name] -= 1
                    infestation_change[spread] += 1
        for key, value in infestation_change.items():
            self.systems[key].infestation += value
            if self.systems[key].infestation >= 6 and not system.lost:
                print(f"System {system.name} is lost")
                system.lost = True
            if self.systems[key].infestation <= 0:
                self.systems[key].infestation = 0
    
    def initialise_infestation(self):
        first_system = random.choice(list(self.systems.keys()))
        d3 = Dice(sides=3)
        print("First system is:")
        print(self.systems[first_system])
        print("--------------")
        linked_systems = self.get_links(first_system)
        self.systems[first_system].infestation += next(d3)
        for entry in linked_systems:
            self.systems[entry].infestation += next(d3)

class System:
    def __init__(self, name, linked_to):
        self.name = name
        if name in linked_to:
            linked_to.remove(name)
        self.linked_to = linked_to
        self.infestation = 0
        self.lost = False
    
    def __str__(self):
        return f"{self.name} linked to {self.linked_to} with infestation {self.infestation} and is {'lost' if self.lost else 'not lost'}"


if __name__ == "__main__":
    system_names = ["a", "b", "c", "d", "e", "f", "g"]
    system_links = [[random.choice(system_names) for x 
                     in range(random.randint(1, 2))] for
                    y in system_names]
    maps = Map()
    for name, links in zip(system_names, system_links):
        maps.add_system(System(name, links))
    maps.form_map()
    
    maps.initialise_infestation()
    for entry in maps.systems.values():
        print(entry)
    game = Game(maps)
    for i in range(12):
        print(f"Turn {i} ----------")
        game.play_turn(pwin=0.75, pmajor=0.5)