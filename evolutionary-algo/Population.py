# -*- coding: utf-8 -*-
"""
Created on Thu May 27 21:07:55 2021

@author: Bjarne Gerdes
"""
import uuid


def f(x, y):
    """
    Function that will be optimized

    Parameters
    ----------
    x : float
        Value for parameter x.
    y : float
        Value for parameter x.

    Returns
    -------
    float
        Function value for f(x,y).
    """
    
    if (x**2 + y**2) <= 2:
        return (1-x)**2 + 100*((y - x**2)**2)
        
    else:
        return 10**8



class PopulationInstance:
    
    def __init__(self, x, y, parent_1_uuid, parent_2_uuid, parent_1_share, parent_2_share):
        """
        Represents a an individual. 

        Parameters
        ----------
        x : float
            x-Value of the individual x from f(x,y).
        y : float
            y-Value of the individual y from f(x,y).
        parent_1_uuid : str
            Identifier of one parent of the individual.
        parent_2_uuid : str
            Identifier of the other parent of the individual.
        parent_1_share : float
            Share of the parent 1 on the x and y values.
        parent_2_share : float
            Share of the parent 2 on the x and y values.

        Returns
        -------
        None.

        """
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
        """
        Function that defines the fitness of the individual.

        Parameters
        ----------
        f : function
            Function that will be optimized.

        Returns
        -------
        float
            fitness of the individual f(x,y)

        """
        self.fitness_value = f(self.x, self.y)
        return self.fitness_value
