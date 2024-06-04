import numpy as np
from time import sleep
import requests

from utils import *
from prompts import *
from prompts_v2 import *
from graphs.contriever_graph import ContrieverGraph
from contriever import Retriever
from retriever_search_drafts import graph_retr_search

class ContrieverGraphNew(ContrieverGraph):
    def __init__(self, model, system_prompt):
        super().__init__(model, system_prompt, 0.1)
        
    def update(self, observation, observations, plan, prev_subgraph, locations, curr_location, previous_location, action, step, items1, log):
        cost = 0
        cost_descr = 0
        #prompt = prompt_summ_simple1.format(observation=observation, observations=observations, plan=plan, subgraph = prev_subgraph)
        #description, cost_descr = self.generate(prompt, t = 0.)
        #log("Subjective perception: " + description)
        
        example = [re.sub(r"Step \d+: ", "", triplet) for triplet in prev_subgraph]
        prompt = prompt_extraction_current.format(observation = observation, example = example)
        response, cost_extract = self.generate(prompt, t = 0.)
        new_triplets_raw = process_triplets(response)
        
        new_triplets = self.exclude(new_triplets_raw)
        new_triplets_str = self.convert(new_triplets_raw)
        
        log("New triplets: " + str(new_triplets))
        
        items_ = {self.add_item(triplet[0]) for triplet in new_triplets_raw} | {self.add_item(triplet[1]) for triplet in new_triplets_raw}
        
        #items_ = list({triplet[0] for triplet in new_triplets_raw} | {triplet[1] for triplet in new_triplets_raw})
        
        associated_subgraph = self.get_associated_triplets1(items_, steps = 1)
        words_to_exclude = ['west', 'east', 'south', 'north', 'associated with', 'used for', 'to be']
        associated_subgraph = [item for item in associated_subgraph if not any(word in item for word in words_to_exclude)]


        print("delete_subgr", associated_subgraph)
        prompt = prompt_refining_items.format(ex_triplets = associated_subgraph, new_triplets = new_triplets)
        response, cost_refine = self.generate(prompt, t = 0.)
        predicted_outdated = parse_triplets_removing(response)
        print('predicted_outdated', predicted_outdated)
        self.delete_triplets(predicted_outdated, locations)
        log("Outdated triplets: " + response)
       
        if "go to" not in action:
            if curr_location != previous_location:
                new_triplets_raw.append([curr_location, previous_location, {"label": find_direction(action)}])
                new_triplets_raw.append([previous_location, curr_location, {"label": find_opposite_direction(action)}])

        self.add_triplets(new_triplets_raw)
        
        # associated_subgraph = self.reasoning(items)  
        #self.expand_graph(threshold = 0.58)
        #associated_subgraph = self.beam_search_on_triplets(items, observation, plan, deepcopy(new_triplets_), depth = 4, width = 7, log = log)
 
        #associated_subgraph = self.get_associated_triplets(items1, steps =2)
        #associated_subgraph = self.extended_bfs_dict(items1)
        

        triplets = self.triplets_to_str(self.triplets)
        associated_subgraph = set()
        
        #retrieve for dict of items

        for query, depth in items1.items():  # items1 is now a dictionary
            # Optionally, you can include verbose output here
            # print(f"QUERY: {query}, MAX_DEPTH: {depth}")
            results = graph_retr_search(
                query, triplets, self.retriever, max_depth=depth,  # Use the value from the dictionary for max_depth
                topk=6,
                post_retrieve_threshold=0.75,  # for base contriever
                verbose=2
            )
            associated_subgraph.update(results)

        """
        #retrieve for list of items
        for query in items1: #items[22][-5:]:
            #print(f"QUERY: {query}")
            results = graph_retr_search(
                query, triplets, retriever, max_depth=2,
                topk=6,
                post_retrieve_threshold=0.7, # for base contriever
                verbose=2
            )
            associated_subgraph.update(results)
            #print(f'triplets total: {len(results)}')
            #print("#######################################\n")
        """
        #associated_subgraph = [item for item in associated_subgraph if 'associated with' not in item]        
        
        #log("Associated_subgraph: " + str(associated_subgraph))
        
        #Exclude triplets from the current observation
        associated_subgraph = tuple(element for element in associated_subgraph if element not in new_triplets_str)
        
        return associated_subgraph, cost, new_triplets_str
    
    def triplets_to_str(self, triplets):
        return [self.str(triplet) for triplet in triplets]  
    
    def convert(self, triplets):
        new_triplets = []
        for triplet in triplets:
            triplet = clear_triplet(triplet)
            new_triplets.append(self.str(triplet))
                
        return new_triplets