# -*- coding: utf-8 -*-
"""
Created on Thu May 27 21:13:08 2021

@author: Bjarne Gerdes
"""

import pandas as pd
import plotly.io as pio
from pyvis.network import Network
pio.renderers.default = 'browser'

class NetworkPlot:

    def __init__(self, evolution_iteration):
        """
        This class takes a whole evoluition class, after the evolution-process has been
        finished.

        It will create a network graph out of this in order to visualize the
        relations between the indivudalis.        

        Parameters
        ----------
        evolution_iteration : class
            Instance of the Evolution.Evolution-Class.

        Returns
        -------
        None.

        """
        self.evolution_iteration = evolution_iteration
        
    def transform(self):
        """
        Create a df that will contain all instances with their parents and their 
        parents share.

        Returns
        -------
        None.

        """
        all_instances = self.evolution_iteration.population_alive + self.evolution_iteration.population_history
        df_all_instances = pd.DataFrame([(instance.fitness_value, instance.x, instance.y, instance.uuid,\
                          instance.parent_1_uuid, instance.parent_1_share,\
                          instance.parent_2_uuid, instance.parent_2_share)
                          for instance in all_instances], columns=["f(x,y)", "x", "y", "Uuid","Parent 1 Uuid",\
                                                                   "Parent 1 Erbanteil","Parent 2 Uuid",\
                                                                   "Parent 2 Erbanteil"])                                               
        self.df_all_instances = df_all_instances
        
    def plot(self):
        """
        Create the network plot

        Returns
        -------
        None.

        """
        # initialize the network graph
        net = Network(height='100%', width='100%', bgcolor='#222222',\
                      layout=False,font_color='white')
            
        # define a json with plotting parameters
        net.set_options("""
var options = {
  "nodes": {
    "shape": "circle"
  },
  "edges": {
    "arrows": {
      "from": {
        "enabled": true,
        "scaleFactor": 0.95
      }
    },
    "color": {
      "inherit": true
    },
    "scaling": {
      "max": 1
    },
    "smooth": false
  },
  "physics": {
    "hierarchicalRepulsion": {
      "centralGravity": 0,
      "nodeDistance": 275
    },
    "minVelocity": 0.75,
    "solver": "hierarchicalRepulsion"
  }
}""")
        #net.show_buttons()
        
        # add each inividual to the network
        for index, row in self.df_all_instances.iterrows():
            net.add_node(row["Uuid"], row["Uuid"], title=f"f(x,y) = {row['f(x,y)']}", size=1+int(10/row["f(x,y)"]))            
            try:
                net.add_node(row["Parent 1 Uuid"], row["Parent 1 Uuid"], title=row["Parent 1 Uuid"]) 
                net.add_edge(row["Uuid"], row["Parent 1 Uuid"], value=1/row["Parent 1 Erbanteil"])
                
                net.add_node(row["Parent 2 Uuid"], row["Parent 2 Uuid"], title=row["Parent 2 Uuid"])            
                net.add_edge(row["Uuid"], row["Parent 2 Uuid"], value=1/row["Parent 2 Erbanteil"])
            except:
                None
        neighbor_map = net.get_adj_list()
        
        # add neighbor data to node hover data
        for node in net.nodes:
            node['title'] += ' Neighbors:<br>' + '<br>'.join(neighbor_map[node['id']])
            node['value'] = len(neighbor_map[node['id']])
        
        # plot the network
        net.show('networkgraph.html')
        