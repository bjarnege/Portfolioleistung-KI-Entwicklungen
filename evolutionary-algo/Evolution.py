# -*- coding: utf-8 -*-
"""
Created on Thu May 27 21:10:51 2021

@author: Bjarne Gerdes
"""
import random
import numpy as np
import pandas as pd
from Population import PopulationInstance


class Evolution:
    
    
    def __init__(self, f, N_population):
        self.f = f
        self.N_population = N_population
        
        self.population_alive = []
        self.population_history = []
        
        
    def initiatePopulation(self, population_start_x, population_start_y):
        
        
        for n in range(0, self.N_population):
            # initiate instance with random gaussian values
            if population_start_x == None and population_start_y == None:
                x,y = random.uniform(-10, 10), random.uniform(-10, 10)
            
            instance = PopulationInstance(x, y, None, None, None, None)

                    
            # calculate fitness of this instance and append instance to population
            instance.fitnessFunction(self.f)
            self.population_alive.append(instance)
            
    
    def selectPopulation(self, n_population_after, select_type, threshold_var):
        # read fitness values of each instance 
        instances_fitness_values = pd.DataFrame(([(instance, instance.fitness_value)\
                                                      for instance in self.population_alive]))
 
        if select_type == "threshold":
            # select all that are below \mu + \sigma*threshold_var
            threshold_value = instances_fitness_values[1].mean() + instances_fitness_values[1].var()*threshold_var
            
            instances_fitness_values["is_alive"] = instances_fitness_values[1] <= threshold_value
            
        if select_type == "top_n":
            # calculate rank of fitness and select top n
            instances_fitness_values["is_alive"] = instances_fitness_values[1].rank(method="first") <= n_population_after
        
        # eleminate all dead instances:
        for row in instances_fitness_values.values:
            if row[2] == False:
                self.population_alive.remove(row[0])
                self.population_history.append(row[0])
                                
    def selectCrossoverPairs(self, pairing_type):
        pairs_needed = self.N_population - len(self.population_alive)
        pairs = []
        
        if pairing_type == "error_based":
            # calculate distribution of fitness values
            error_distribution = [instance.fitness_value for instance in self.population_alive]
            error_distribution = [fitness_value/sum(error_distribution) for fitness_value in error_distribution]
            
        # parameter that avoids getting stuck in the while loop when the number of combinations
        # isn't sufficient.
        i = 0
        while len(pairs) <= pairs_needed:
            i += 1

            
            if pairing_type == "random":
                pair_combination = (random.sample(self.population_alive, 2))
            
            if pairing_type == "error_based":
                pair_combination = random.choices(self.population_alive, weights=error_distribution, k=2)

                
            
            
            # inbreeding control:
            check_0 = pair_combination[0].uuid in (pair_combination[1].parent_1_uuid, pair_combination[1].parent_2_uuid)
            check_1 = pair_combination[1].uuid in (pair_combination[0].parent_1_uuid, pair_combination[0].parent_2_uuid)
            check_2 = pair_combination[0].uuid ==  pair_combination[1].uuid
            
            if not any([check_0, check_1, check_2]):
                pairs.append(pair_combination)
            
            if i >= 100:
                break

        return pairs
       
       
    def crossoverCombination(self, crossover_type, parent_1, parent_2):
        
        
        if crossover_type == "linear":
            parent_1_share = parent_2_share = .5

        if crossover_type ==  "error_based":
            parent_1_share = 1 - parent_1.fitness_value/(parent_1.fitness_value + parent_2.fitness_value)
            parent_2_share = 1 - parent_1_share

        if crossover_type == "random_uniform":
            parent_1_share = random.uniform(0, 1)
            parent_2_share = 1 - parent_1_share

        if crossover_type == "random_gaussian":
            parent_1_gaus_val = np.random.normal(0,1)
            parent_2_gaus_val = np.random.normal(0,1)
            parent_1_share = parent_1_gaus_val/(parent_1_gaus_val+parent_2_gaus_val)
            parent_2_share = 1 - parent_1_share
                            
            
        x = (parent_1_share*parent_1.x + parent_2_share*parent_2.x)
        y = (parent_1_share*parent_1.y + parent_2_share*parent_2.y)
                            
        return x, y, parent_1_share, parent_2_share


    def mutate(self, x, y):
        
        # calculate standart deviation of gaussian distribution by:
        std = 0.1#*(((abs(x)+abs(y))/2)**(1/4))
            
        return x+np.random.normal(0, std), y+np.random.normal(0, std)
            
    def proceeOneIter(self, n_population_after, select_type, pairing_type, crossover_type, threshold_stds):
        # choose which instances will be eliminated based on the select type
        self.selectPopulation(n_population_after, select_type, threshold_stds)
        
        # select which instance swill be recombined baised on the pairing_type
        pairs = self.selectCrossoverPairs(pairing_type)
        
        # calculate the x and y values for the new instance based on the crossover_type
        for parent_1, parent_2 in pairs:
            x, y, parent_1_share, parent_2_share = self.crossoverCombination(crossover_type, parent_1, parent_2)
            
            # add gaussian mutation to x and y
            x, y = self.mutate(x, y)
            
            # initiate new instance
            child_instance = PopulationInstance(x, y, parent_1.uuid, parent_2.uuid, parent_1_share, parent_2_share)
            
            # calculate fitness for instance and store instance as alive
            child_instance.fitnessFunction(self.f)
            self.population_alive.append(child_instance)
            
    
    def populationStats(self, iteration):
        df_population = pd.DataFrame([(instance.x, instance.y, instance.fitness_value) for instance in self.population_alive], columns=["x", "y", "f(x,y)"])
        # drop inf values
        df_population = df_population[df_population["f(x,y)"] < 10**8]
        df_stats = df_population.mean()
        df_stats["Iteration"] = iteration
        return df_stats
        
    def process(self, n_iters, n_population_after, select_type, pairing_type, crossover_type, threshold_stds=None,
                population_start_x=None, population_start_y=None):
        
        self.initiatePopulation(population_start_x, population_start_x)
        
        self.iter_stats = pd.DataFrame()
        
        
        for i in range(n_iters):
            self.proceeOneIter( n_population_after, select_type, pairing_type, crossover_type, threshold_stds)
            
            self.iter_stats = self.iter_stats.append(self.populationStats(i),  ignore_index=True )
            
        
        self.iter_stats["select_type"] = select_type
        self.iter_stats["pairing_type"] = pairing_type
        self.iter_stats["crossover_type"] = crossover_type

        return self.iter_stats
