from prompts import *
from prompts_v2 import *
from utils import *

from parent_graph import TripletGraph
from graphs.parent_without_emb import GraphWithoutEmbeddings

class ExtendedGraphSubgraphStrategy(GraphWithoutEmbeddings):
    def __init__(self, model, system_prompt, threshold = 0.02):
        super().__init__(model, system_prompt, threshold)
        
    def update_items(self, obs):
        prompt = prompt_extraction_current.format(observation = obs)
        response, cost = self.generate(prompt)
        new_triplets = process_triplets(response)
        items = {self.add_item(triplet[0]) for triplet in new_triplets} | {self.add_item(triplet[1]) for triplet in new_triplets}
        return new_triplets, list(items)
    
    def update_metainf(self, summary):
        prompt = prompt_extraction_summary.format(observation = summary)
        response, cost = self.generate(prompt)
        new_triplets = process_triplets(response)
        objects = {self.add_item(triplet[0]) for triplet in new_triplets} | {self.add_item(triplet[1]) for triplet in new_triplets}
        return new_triplets, list(objects)
    
    def update(self, obs, summaries, locations, curr_location, previous_location, action, log):
        new_items_triplets, items = self.update_items(obs)
        new_items_triplets_ = self.exclude(new_items_triplets)
        log("New triplets items: " + str(new_items_triplets_))
        
        new_meta_triplets, objects = [], []
        for summary in summaries:
            if summary is None:
                continue
            temp_triplets, temp_objs = self.update_metainf(summary)
            new_meta_triplets += temp_triplets
            objects += temp_objs
        new_meta_triplets_ = self.exclude(new_meta_triplets)
        log("New triplets meta: " + str(new_meta_triplets_))
            
        predicted_items_outdated = []
        if new_items_triplets:
            associated_subgraph = self.get_associated_triplets(items, steps = 1)
            prompt = prompt_refining_items.format(ex_triplets = associated_subgraph, new_triplets = new_items_triplets_)
            response, cost = self.generate(prompt)
            predicted_items_outdated = parse_triplets_removing(response)
            log("Outdated triplets items: " + response)
        
        predicted_meta_outdated = []
        if new_meta_triplets:
            associated_subgraph = self.get_associated_triplets(objects, steps = 1)
            prompt = prompt_refining_meta.format(ex_triplets = associated_subgraph, new_triplets = new_meta_triplets_)
            response, cost = self.generate(prompt)
            predicted_meta_outdated = parse_triplets_removing(response)
            log("Outdated triplets meta: " + response)
        
        self.delete_triplets(predicted_items_outdated + predicted_meta_outdated, locations)
        if curr_location != previous_location:
            new_meta_triplets.append([curr_location, previous_location, {"label": find_direction(action)}])
        self.add_triplets(new_meta_triplets + new_items_triplets)
    

        associated_subgraph = self.get_associated_triplets(items + objects, steps = 2)
        log("Associated_subgraph: " + str(associated_subgraph))
        return associated_subgraph