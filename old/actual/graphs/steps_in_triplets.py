import os
import json
import requests
import torch
import transformers
from time import sleep
import numpy as np
from copy import deepcopy
from random import shuffle
from scipy.spatial.distance import cosine, euclidean

from utils import *
from prompts import *
from graphs.parent_without_emb import GraphWithoutEmbeddings
from prompts_v2 import *
class StepsInTripletsGraph(GraphWithoutEmbeddings):
    def __init__(self, model, system_prompt, threshold = 0.02):
        super().__init__(model, system_prompt, threshold)
        self.triplets_names = set()
        
    def add_triplets(self, triplets, step):
        for triplet in triplets:
            if triplet[2]["label"] == "free":
                continue
            triplet = clear_triplet(triplet)
            triplet[2]["step"] = step
            if self.str(triplet) not in self.triplets_names:
                self.triplets.append(triplet)
                self.triplets_names.add(self.str(triplet))
            else:
                for existed_triplet in self.triplets:
                    if self.str(existed_triplet) == self.str(triplet):
                        existed_triplet[2]["step"] = step
                
    def str_with_step(self, triplet):
        step = triplet[2]["step"]
        return f"Step {step}: " + triplet[0] + ", " + triplet[2]["label"] + ", " + triplet[1]
    
    def triplets_to_str(self, triplets):
        return [self.str(triplet) for triplet in triplets] 
            
    def update(self, observation, observations, plan, locations, curr_location, previous_location, action, log, step, items):        
         # Extracting triplets
        prompt = prompt_extraction.format(observation = observation, observations = observations)
        response, cost = self.generate(prompt)
        new_triplets_raw = process_triplets(response)
        
        new_triplets = self.exclude(new_triplets_raw)
        log("New triplets: " + str(new_triplets))
        
        items_ = list({triplet[0] for triplet in new_triplets_raw} | {triplet[1] for triplet in new_triplets_raw})
        associated_subgraph = self.get_associated_triplets(items_, steps = 1, without_step = True)
        prompt = prompt_refining_items.format(ex_triplets = associated_subgraph, new_triplets = new_triplets)
        response, cost = self.generate(prompt, t = 0.2)
        predicted_outdated = parse_triplets_removing(response)
        self.delete_triplets(predicted_outdated, locations)
        log("Outdated triplets: " + response)
       
        if curr_location != previous_location:
            new_triplets_raw.append((curr_location, previous_location, {"label": find_direction(action)}))
            new_triplets_raw.append([previous_location, curr_location, {"label": find_opposite_direction(action)}])  


        self.add_triplets(new_triplets_raw, step)
        # associated_subgraph = self.beam_search_on_triplets(items, observation + "\nPlan: " + plan, visited = {}, depth = 2, width = 8, log = log)
        associated_subgraph = self.get_associated_triplets(items, steps = 2)
        return associated_subgraph[:30]
    
    def get_conseq(self, actions):
        names = np.unique([action[0] for action in actions])
        acts_with_cons = {}
        for action in names:
            last_step = max([act[1] for act in actions if act[0] == action])
            acts_with_cons[action] = [self.str_with_step(triplet) for triplet in self.triplets if triplet[2]["step"] == last_step + 1]
        return acts_with_cons
    
    def get_associated_triplets(self, items, steps = 2, without_step = False):
        items_ = deepcopy([string.lower() for string in items])
        associated_triplets = []
        now = set()
        for i in range(steps):
            for item in items_:
                for triplet in self.triplets:   
                    for_check = self.str(triplet) if without_step else self.str_with_step(triplet)                
                    if (item == triplet[0] or item == triplet[1]) and for_check not in associated_triplets:
                        associated_triplets.append(for_check)
                        if item == triplet[0]:
                            now.add(triplet[1])
                        if item == triplet[1]:
                            now.add(triplet[0])    
                    
            if "itself" in now:
                now.remove("itself")  
            items_ = list(now)
        return associated_triplets
    
    def exclude(self, triplets):
        new_triplets = []
        for triplet in triplets:
            triplet = clear_triplet(triplet)
            if self.str(triplet) not in self.triplets_names:
                new_triplets.append(self.str(triplet))
                
        return new_triplets
    
    def beam_search_on_triplets(self, items, description, visited, depth, width, log):
        items = set(items)
        visited = {self.str_with_step(clear_triplet(triplet)) for triplet in visited}
        chosen = set()
        for step in range(depth):
            candidates = [self.str_with_step(triplet) for triplet in self.triplets 
                          if (triplet[0] in items or triplet[1] in items) and self.str_with_step(triplet) not in visited]
            log("Length of candidates: " + str(len(candidates)))
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
    
class LLaMAStepsInTripletsGraph(StepsInTripletsGraph):
    def __init__(self, model, system_prompt, pipeline, threshold = 0.02):
        super().__init__(model, system_prompt, threshold)
        self.pipeline = pipeline
        
    def generate(self, prompt, jsn = False, t = 0.2):
        print("Prompt: ", prompt)
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt},
        ]

        prompt = self.pipeline.tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
        )

        terminators = [
            self.pipeline.tokenizer.eos_token_id,
            self.pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]
        
        outputs = self.pipeline(
            prompt,
            max_new_tokens=2048,
            eos_token_id=terminators,
            do_sample=True,
            temperature=t,
            top_p=0.9,
        )
        print("response: ", outputs[0]["generated_text"])
        return outputs[0]["generated_text"][len(prompt):], 0
    