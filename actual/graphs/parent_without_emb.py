import os
import json
import requests
from time import sleep
import numpy as np
from copy import deepcopy
from scipy.spatial.distance import cosine, euclidean

from utils import *
from prompts import *
from parent_graph import TripletGraph

class GraphWithoutEmbeddings(TripletGraph):
    def __init__(self, model, system_prompt, threshold = 0.02):
        super().__init__(model, system_prompt, threshold)
        
    # For triplet without embeddings
    def str(self, triplet):
        return triplet[0] + ", " + triplet[2]["label"] + ", " + triplet[1]
    
    def get_all_triplets(self):
        return [self.str(triplet) for triplet in self.triplets]
    
    def delete_all(self):
        self.triplets, self.items = [], []
        
    def add_item(self, item):
        item = item.lower()
        if item in self.items:
            return item
        self.items.append(item)
        return item
    
    # Filling graph
    def add_triplets(self, triplets):
        success = []
        for triplet in triplets:
            if triplet[2]["label"] == "free":
                success.append(False)
                continue
            triplet = clear_triplet(triplet)
            if triplet not in self.triplets:
                self.triplets.append(triplet)
                success.append(True)
            else:
                success.append(False)
        return success
                
    # Delete triplets exclude navigation ones            
    def delete_triplets(self, triplets, locations):
        success = []
        for triplet in triplets:
            if triplet[0] in locations and triplet[1] in locations:
                success.append(False)
                continue
            if triplet in self.triplets:
                self.triplets.remove(triplet)
                success.append(True)
            else:
                success.append(False)
        return success
            
    # Associations by set of items. Step is a parameter for BFS
    def get_associated_triplets(self, items, steps = 1):
        items = deepcopy(items)
        associated_triplets = []
        visited_items = set()
        now = set()
        for i in range(steps):
            for triplet in self.triplets:
                for item in items:
                    item = item.lower()
                    if item == triplet[0] and triplet[1] not in visited_items:
                        associated_triplets.append(self.str(triplet))
                        visited_items.add(triplet[0])
                        visited_items.add(triplet[1])
                        now.add(triplet[1])
                        break
                    if item == triplet[1] and triplet[0] not in visited_items:
                        associated_triplets.append(self.str(triplet))
                        visited_items.add(triplet[0])
                        visited_items.add(triplet[1])
                        now.add(triplet[0])
                        break      
            if "itself" in now:
                now.remove("itself")  
            items = now
        return associated_triplets
    
    # Exclude facts from 'triplets' which already in graph
    def exclude(self, triplets):
        new_triplets = []
        for triplet in triplets:
            triplet = clear_triplet(triplet)
            if triplet not in self.triplets:
                new_triplets.append(self.str(triplet))
                
        return new_triplets
    
    # Compute useful shape of graph with only spatial information
    def compute_spatial_graph(self, locations):
        locations = deepcopy(locations)
        if "player" in locations:
            locations.remove("player")
        graph = {}
        for triplet in self.triplets:
            if triplet[2]["label"] == "free":
                continue
            if triplet[0] in locations and triplet[1] in locations:
                if triplet[0] in graph:
                    graph[triplet[0]]["connections"].append((triplet[2]["label"], triplet[1]))
                else:
                    graph[triplet[0]] = {"connections": [(triplet[2]["label"], triplet[1])]}
                
                if triplet[1] in graph:
                    graph[triplet[1]]["connections"].append(("reversed", triplet[0]))
                else:
                    graph[triplet[1]] = {"connections": [("reversed", triplet[0])]}
                    
        for loc in graph:
            connections = deepcopy(graph[loc]["connections"])
            connected_loc = [connection[1] for connection in connections if check_conn(connection[0])]
            for connection in connections:
                if connection[1] in connected_loc and connection[0] == "reversed":
                    graph[loc]["connections"].remove(connection)
        return graph
    
    # Find shortest path between A and B if both in locations
    def find_path(self, A, B, locations):
        if A == 'Kids" Room':
            A = "Kids' Room"
        if B == 'Kids" Room':
            B = "Kids' Room"
        if A == B:
            return "You are already there"
        if A not in self.items or B not in self.items:
            return "Destination is unknown. Please, choose another destination or explore new paths and locations."
        spatial_graph = self.compute_spatial_graph(locations)
        current_set = {A}
        future_set = set()
        total_set = {A}
        found = False
        while len(current_set) > 0:
            for loc in current_set:
                for child in spatial_graph[loc]["connections"]:
                    if child[1] not in total_set:
                        future_set.add(child[1])
                        total_set.add(child[1])
                        spatial_graph[child[1]]["parent"] = loc
                        if child[1] == B:
                            found = True
                            break
                if found:
                    break
            if found:
                break
            current_set = future_set
            future_set = set()
        if not found:
            return "Destination isn't available according to had knowledges. Please, choose another destination or explore new paths and locations."
        path = []
        current_loc = B
        while current_loc != A:
            parent = spatial_graph[current_loc]["parent"]
            relation = find_relation(spatial_graph, parent, current_loc, True)
            path.append(relation)
            current_loc = parent
        return list(reversed(path))