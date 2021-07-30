# -*- coding: utf-8 -*-
"""
Created on Thu May 27 21:09:32 2021

@author: Bjarne Gerdes
"""
import plotly.io as pio
pio.renderers.default = 'browser'

from Population import f
from Evolution import  Evolution
import pandas as pd
import numpy as np
import random

class ProcessAllVariants:
    
    def __init__(self, select_type = ["threshold", "top_n"],
                 pairing_type = ["random", "error_based"],
                 crossover_type = ["linear", "error_based", "random_uniform", "random_gaussian"],
                 f=f, N_population = 40, n_iters = 10, n_population_after = 10, threshold_stds = 2):
        """
        This class is used to test each combination of parameters and visualize their training process.
        
        The used parameters won't be exaplained in detail, but one can find a extensive documentation 
        in the file "Evolution.py".

        Parameters
        ----------
            The used parameters won't be exaplained in detail, but one can find a extensive documentation 
            in the file "Evolution.py".

        Returns
        -------
        None.

        """
        # store the relevant parameters
        self.select_type = select_type
        self.pairing_type = pairing_type
        self.crossover_type = crossover_type
        self.f = f
        self.N_population = N_population
        self.n_iters = n_iters
        self.n_population_after = n_population_after
        self.threshold_stds = threshold_stds
        
        # initialized list, that store the results of each pair of parameters.
        self.runs = []
        self.runs_evol = []
        
        # inital x and y values to avoid random generation and enable to compare the runs
        self.population_start_x = [random.uniform(-10, 10) for _ in range(self.N_population)]
        self.population_start_y = [random.uniform(-10, 10) for _ in range(self.N_population)]
        
    def processAll(self):
        """
        Processing loop, that will perform the evolutionary algorithm
        by testing all defined combinations above.

        Returns
        -------
        None.

        """
        # processing loop
        for st in self.select_type:
            for pt in self.pairing_type:
                for ct in self.crossover_type:
                    evol = Evolution(self.f, self.N_population)
                    self.runs.append(evol.process(self.n_iters, self.n_population_after, st, pt, ct, self.threshold_stds))
                    self.runs_evol.append(evol)
                    
    def plotRuns(self):
        """
        This function is used to create a plot of each combination of parameters.
        

        Returns
        -------
        None.

        """
        # Create DataFrame for each type
        df_evaluations = pd.concat(self.runs)
        df_evaluations["Kriterien"] = "Selektionkriterium: " + df_evaluations["select_type"] +\
                        " Paarungskriterium: "+df_evaluations["pairing_type"] +\
                        " Crossover-Kriterium: "+df_evaluations["crossover_type"]
        self.df_evaluations = df_evaluations
        
        # plot the data
        data = [dict(
          type = 'line',
          x = df_evaluations["Iteration"],
          y = df_evaluations["f(x,y)"],
          mode = 'line',
          transforms = [dict(type = 'groupby',groups = df_evaluations["Kriterien"])])]
        
        # manipulate the plot by added axis titles.
        layout = dict( title="Durchschnittliche Fitness pro Iteration",
                      xaxis={"title":{"text": "Anzahl an Iterationen"}},
                      yaxis={"title":{"text": "Durchschnittlicher f(x,y) der Population"}})
       
        fig_dict = dict(data=data, layout=layout)
        
        # show the plot on the browser
        pio.show(fig_dict, validate=False)