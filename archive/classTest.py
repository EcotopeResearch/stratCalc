# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 16:10:20 2021

@author: scott
"""

class Dog:

    def __init__(self, name, num):
        self.name = name
        self.num = num
        self.tricks = []    # creates a new empty list for each dog
        self.sounds = []
        self.sound = float

    def add_trick(self, trick):
        self.tricks.append(trick)
        
    def add_sound(self):
        #self.sounds.append(sound)
        print('yipppy')
        
    def calc(self):
        n = self.num
        print(n*2)
        self.sound = n
        