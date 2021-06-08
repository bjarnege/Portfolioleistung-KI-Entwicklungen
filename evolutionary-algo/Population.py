# -*- coding: utf-8 -*-
"""
Created on Thu May 27 21:07:55 2021

@author: Bjarne Gerdes
"""
import uuid
import numpy as np


def f(x, y):
    
    if (x**2 + y**2) <= 2:
        return (1-x)**2 + 100*((y - x**2)**2)
        
    else:
        return 10**8



class PopulationInstance:
    
    def __init__(self, x, y, parent_1_uuid, parent_2_uuid, parent_1_share, parent_2_share):
        # parameters of the instance
        self.x = x
        self.y = y
        
        # store data about parents
        self.parent_1_uuid = parent_1_uuid
        self.parent_1_share = parent_1_share
        self.parent_2_uuid = parent_2_uuid
        self.parent_2_share = parent_2_share

        # initialize uuid of the instance
        self.uuid = str(uuid.uuid4())
        
        # track if instance is alive
        self.is_alive = True
        
    def fitnessFunction(self, f):
        self.fitness_value = f(self.x, self.y)
        return self.fitness_value
