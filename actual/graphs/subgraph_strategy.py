from parent_graph import TripletGraph
from prompts import *
from utils import *

class SubgraphStrategy(TripletGraph):
    def __init__(self, model, system_prompt, threshold = 0.02):
        super().__init__(model, system_prompt, threshold) 
        
    def update(self, observation, observations, goal, locations, curr_location, previous_location, action, log):
        prompt = prompt_extracting_items.format(observation = observation, observations = observations[-1:], goal = goal)
        items = process_crucial_items(self.generate(prompt))
        log("Crucial items: " + str(items))
                
         # Extracting triplets
        prompt = prompt_extraction.format(observation = observation, observations = observations[-1:])
        response = self.generate(prompt)
        new_triplets_raw = process_triplets(response)
        new_triplets = self.exclude(new_triplets_raw)
        log("New triplets excluded: " + str(new_triplets))
        
        # Using subgraph
        associated_subgraph = self.get_associated_triplets(items, steps = 2)
        
        #Using full graph
        # associated_subgraph = self.get_all_triplets()
        
        # Replacing triplets
        prompt = prompt_refining.format(ex_triplets = associated_subgraph, new_triplets = new_triplets)
        response = self.generate(prompt)
        predicted_outdated = parse_triplets_removing(response)
        log("Outdated triplets: " + response)
        
        # Updating graph
        self.delete_triplets(predicted_outdated, locations)
        if curr_location != previous_location:
            new_triplets_raw.append((curr_location, previous_location, {"label": find_direction(action)}))
        self.add_triplets(new_triplets_raw)
        
        associated_subgraph = self.get_associated_triplets(items, steps = 2)
        log("Associated_subgraph: " + str(associated_subgraph))
        return associated_subgraph