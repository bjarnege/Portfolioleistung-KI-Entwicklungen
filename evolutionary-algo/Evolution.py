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
        """
        Initialize the evolutionary Algorithm

        Parameters
        ----------
        f : function
            Function that takes two parameters x and y and
            needs to be optimized.
        N_population : int
            Describe the size of the population.
            S.t. every iteration ensure 100 that N_population many
            instances will be alive.

        Returns
        -------
        None.

        """
        self.f = f
        self.N_population = N_population
        
        self.population_alive = []
        self.population_history = []
        
        
    def initiatePopulation(self, population_start_x=None, population_start_y=None):
        """
        Initialize the first population with random uniformly distributed
        parametervalues for x and y

        Parameters
        ----------
        population_start_x : list
            List of random values like the ones created in the for-loop.
            This and the following value can be used in order to have the same starting values
            for multiple instances of these class. Which allows to make parametercobinations
            compareable.
            Default None.
        population_start_y : list
            List of random values like the ones created in the for-loop. Default None.

        Returns
        -------
        None.

        """
        
        for n in range(0, self.N_population):
            # initiate instance with random gaussian values
            if population_start_x == None and population_start_y == None:
                x,y = random.uniform(-10, 10), random.uniform(-10, 10)
            
            instance = PopulationInstance(x, y, None, None, None, None)

                    
            # calculate fitness of this instance and append instance to population
            instance.fitnessFunction(self.f)
            self.population_alive.append(instance)
            
    
    def selectPopulation(self, n_population_after, select_type, threshold_var):
        """
        This function defines how the living individuals will be eliminated 
        in order to enforce a survival of the fittest approach.

        Parameters
        ----------
        n_population_after : int
            Population that needs to be alive after the elimination process.
            Which self.N_population - n_population_after Individuals will be
            killed each iteration.
            
            This parameter will only affect the model, if:
                select_type = "top_n"

        threshold_var : float
            A weighting parameter which will be multipled with the σ**2 of the fitness value of the instances.
            And is used to eliminate all instances that are worse than:
                
                μ +  σ**2 * threshold_var
             
            This parameter will only affect the model, if:
                select_type = "threshold"
           
        select_type : str
            Takes two possible options:
                threshold -> Filtering based on a threshold defined by 
                μ +  σ**2 * threshold_var of the fitness values
                
                or
                
                top_n -> Only the top_n individuals with the best fitness
                will be used for reproduction. The rest will be
                eliminated.


        Returns
        -------
        None.

        """
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
        
        # eliminate all dead instances:
        for row in instances_fitness_values.values:
            if row[2] == False:
                self.population_alive.remove(row[0])
                self.population_history.append(row[0])
                                
    def selectCrossoverPairs(self, pairing_type):
        """
        This function is used to select which pairs of instances
        will be used for reproduction.

        Parameters
        ----------
        pairing_type : str
            This parameter defines how the pairs will be choosen.
            
            Let's take a look at the possible options:
                
                error_based -> The probability that a inividual will be used
                                as a part of a pair is defined by:
                                    fitness of the individual / sum of all fitness values
                                    
                                    Which means the better the fitness, the larger
                                    the probability that a induvidual will be
                                    selected for reproduction.
                                    
                random -> Choose a pair random.
            

        Returns
        -------
        pairs : TYPE
            DESCRIPTION.

        """
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
            # enfore no reproduction between siblings and parents and their childs.
            check_0 = pair_combination[0].uuid in (pair_combination[1].parent_1_uuid, pair_combination[1].parent_2_uuid)
            check_1 = pair_combination[1].uuid in (pair_combination[0].parent_1_uuid, pair_combination[0].parent_2_uuid)
            check_2 = pair_combination[0].uuid ==  pair_combination[1].uuid
            
            if not any([check_0, check_1, check_2]):
                pairs.append(pair_combination)
            
            # Force the while loop to stop when there not enough possible pairs left.
            # This will avoid falling in an endless loop if only inbreeds left.
            if i >= 100:
                break

        return pairs
       
       
    def crossoverCombination(self, crossover_type, parent_1, parent_2):
        """
        After the crossover pairs have been selected  (output of selectCrossoverPairs),
        this function will be used to calculate the share of each parent (Elemenet of the pair),
        while calculating the x,y values. Can be seen as a heritage calculations.

        Parameters
        ----------
        crossover_type : str
            Defines how the share will be calculated, one can
            choose between four possible options:
                
                linear -> 50% of each parent
                
                error_based -> based on their fitness values.
                                Example:
                                    Let's say parent one got a fitness of 3 and parent two got
                                    fitness of 7, then share of parent one wold be 70% and of 
                                    parent two would be 30%.
                                    
                random_uniform -> Choose a random value of the share
                                    based on a  uniform distribution from 0 to 1
            
                random_gaussian -> Choose a random value of the share
                                    based on a  standard normal distribution.
                                    
        parent_1 : class
            Individual which will be used as parent of the new created child individual
        parent_2 : class
            Individual which will be used as parent of the new created child individual

        Returns
        -------
        x : float
            x value of the child individual.
        y : float
            y value of the child individual.
        parent_1_share : float
            Share of parent 1 on the x and y values of the child individual.
        parent_2_share : float
            Share of parent 2 on the x and y values of the child individual.

        """
        
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
        """
        After the share of each parent is calculated the
        values of the parameters x and y will be manipulated
        by adding a gaussian distributed value with std of 0.1

        Parameters
        ----------
        x : float
            x value of the child individual.
        y : float
            y value of the child individual.

        Returns
        -------
        x,y : tuple
            Tuple with mutated x and y values.

        """
        # calculate standart deviation of gaussian distribution by:
        std = 0.1#*(((abs(x)+abs(y))/2)**(1/4))
            
        return x+np.random.normal(0, std), y+np.random.normal(0, std)
            
    def proceeOneIter(self, n_population_after, select_type, pairing_type, crossover_type, threshold_var):
        """
        Processes one iteration by passing the needed parameters through  every of the function above.
        

        Parameters
        ----------
        n_population_after : int
            See documentation of self.selectPopulation.
        select_type : str
            See documentation of self.selectPopulation.
        pairing_type : str
            See documentation of self.selectCrossoverPairs.
        crossover_type : str
            See documentation of self.crossoverCombination.
        threshold_var : str
            See documentation of self.selectPopulation.

        Returns
        -------
        None.

        """
        # choose which instances will be eliminated based on the select type
        self.selectPopulation(n_population_after, select_type, threshold_var)
        
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
        """
        Calculate statistics about the instances x,y and f(x,y) values to 
        visualize the training prozess later

        Parameters
        ----------
        iteration : int
            Iteration of the algorithm.

        Returns
        -------
        df_stats : pandas.DataFrame
            Statistics for each itteration.

        """
        df_population = pd.DataFrame([(instance.x, instance.y, instance.fitness_value) for instance in self.population_alive], columns=["x", "y", "f(x,y)"])
        # drop inf values
        df_population = df_population[df_population["f(x,y)"] < 10**8]
        df_stats = df_population.mean()
        df_stats["Iteration"] = iteration
        return df_stats
        
    def process(self, n_iters, n_population_after, select_type, pairing_type, crossover_type, threshold_var=None,
                population_start_x=None, population_start_y=None):
        """
        Processes the whole evolutionary algorithm.

        Parameters
        ----------
        n_iters : int
            Iteration that are executed to optimize the fitness falues.
        n_population_after : int
            See documentation of self.selectPopulation.
        select_type : str
            See documentation of self.selectPopulation.
        pairing_type : str
            See documentation of self.selectCrossoverPairs.
        crossover_type : str
            See documentation of self.crossoverCombination.
        threshold_var : str
            See documentation of self.selectPopulation.
        population_start_x : list, optional
            See documentation of self.selectPopulation.
        population_start_y : list, optional
            See documentation of self.selectPopulation.

        Returns
        -------
        pd.DataFrame
            Statistics about all iterations that can be used for plotting
            the progress of the evolution.

        """
        # create starting values
        self.initiatePopulation(population_start_x, population_start_x)
        self.iter_stats = pd.DataFrame()
        
        # process the iterations and calculate their stats.
        for i in range(n_iters):
            self.proceeOneIter( n_population_after, select_type, pairing_type, crossover_type, threshold_var)
            self.iter_stats = self.iter_stats.append(self.populationStats(i),  ignore_index=True )
            
        # store further relevant informations in the stats-df.
        self.iter_stats["select_type"] = select_type
        self.iter_stats["pairing_type"] = pairing_type
        self.iter_stats["crossover_type"] = crossover_type

        return self.iter_stats
