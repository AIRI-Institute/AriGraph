import re

from utils import *
from prompts import *
from prompts_v2 import *
from graphs.parent_without_emb import GraphWithoutEmbeddings

class DescriptionGraphBeamSearchStrategy(GraphWithoutEmbeddings):
    def __init__(self, model, system_prompt, threshold = 0.02):
        super().__init__(model, system_prompt, threshold)
        self.triplets_names = set()
        
    def str_with_step(self, triplet, step = None):
        if step is None:
            step = triplet[2]["step"]
        return f"Step {step}: " + triplet[0] + ", " + triplet[2]["label"] + ", " + triplet[1] 
        
    def update(self, observation, observations, plan, prev_subgraph, locations, curr_location, previous_location, action, step, log):
        prompt = prompt_exactly_describe_subgraph.format(observation=observation, observations=observations, plan=plan, subgraph = prev_subgraph)
        description, cost = self.generate(prompt, t = 0.)
        log("Subjective perception: " + description)
        
        example = [re.sub(r"Step \d+: ", "", triplet) for triplet in prev_subgraph]
        prompt = prompt_extraction_current.format(observation = description, example = example)
        response, cost = self.generate(prompt, t = 0.)
        new_triplets = process_triplets(response)
        visited = deepcopy(new_triplets)
        
        new_triplets_ = self.exclude(new_triplets)
        items = {self.add_item(triplet[0]) for triplet in new_triplets} | {self.add_item(triplet[1]) for triplet in new_triplets}
        new_triplets = self.triplets_to_str(new_triplets_)
        log("New triplets: " + str(new_triplets))
        
        associated_subgraph = self.get_associated_triplets(items, steps = 1)
        prompt = prompt_refining_items.format(ex_triplets = associated_subgraph, new_triplets = new_triplets)
        response, cost = self.generate(prompt, t = 0.)
        predicted_outdated = parse_triplets_removing(response)
        log("Outdated triplets: " + response)
        
        self.delete_triplets(predicted_outdated, locations)
        if curr_location != previous_location:
            new_triplets.append([curr_location, previous_location, {"label": find_direction(action)}])
            new_triplets.append([previous_location, curr_location, {"label": find_opposite_direction(action)}])
        self.add_triplets(new_triplets_, step)
        
        associated_subgraph = self.beam_search_on_triplets(items, description, visited, depth = 3, width = 7, step = step)
        log("Associated_subgraph: " + str(associated_subgraph))
        return associated_subgraph, description
        
    
    
    def triplets_to_str(self, triplets):
        return [self.str(triplet) for triplet in triplets]    
        
    def add_triplets(self, triplets, step):
        success = []
        for triplet in triplets:
            if triplet[2]["label"] == "free":
                success.append(False)
                continue
            triplet = clear_triplet(triplet)
            triplet[2]["step"] = step
            if self.str(triplet) not in self.triplets_names:
                self.triplets.append(triplet)
                self.triplets_names.add(self.str(triplet))
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
            if self.str(triplet) in self.triplets_names:
                for candidate in self.triplets:
                    if self.str(candidate) == self.str(triplet):
                        self.triplets.remove(candidate)
                        break
                self.triplets_names.remove(self.str(triplet))
                success.append(True)
            else:
                success.append(False)
        return success
    
    def exclude(self, triplets):
        new_triplets = []
        for triplet in triplets:
            triplet = clear_triplet(triplet)
            if triplet not in self.triplets:
                new_triplets.append(triplet)
                
        return new_triplets
    
    def beam_search_on_triplets(self, items, description, visited, depth, width, step):
        items = set(items)
        visited = {self.str_with_step(clear_triplet(triplet), step) for triplet in visited}
        chosen = set()
        for step in range(depth):
            candidates = [self.str_with_step(triplet) for triplet in self.triplets 
                          if (triplet[0] in items or triplet[1] in items) and self.str_with_step(triplet) not in visited]
            for triplet in candidates:
                visited.add(triplet)
            if not candidates:
                break
            prompt = prompt_choose_triplets.format(descr = description, triplets = chosen, candidates = candidates, number = width)
            response, cost = self.generate(prompt, t = 0.)
            filtered_candidates = process_candidates(response)
            items = {self.add_item(triplet[0]) for triplet in filtered_candidates} | {self.add_item(triplet[1]) for triplet in filtered_candidates}
            for triplet in filtered_candidates:
                chosen.add(self.str_with_step(triplet))
        chosen = list(chosen)
        return chosen
            