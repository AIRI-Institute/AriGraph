

from utils import *
from prompts import *
from prompts_v2 import *
from graphs.parent_without_emb import GraphWithoutEmbeddings
from contriever import Retriever

class ContrieverGraph(GraphWithoutEmbeddings):
    def __init__(self, model, system_prompt, threshold = None, topk = None, device = "cpu"):
        super().__init__(model, system_prompt, 0.1)
        self.retriever = Retriever(device)
        self.threshold, self.topk = threshold, topk
        
    def update(self, observation, observations, plan, locations, curr_location, previous_location, action, log, step, items):        
         # Extracting triplets
        prompt = prompt_extraction.format(observation = observation, observations = observations)
        response, cost = self.generate(prompt)
        new_triplets_raw = process_triplets(response)
        
        new_triplets = self.exclude(new_triplets_raw)
        log("New triplets: " + str(new_triplets))
        
        items_ = list({triplet[0] for triplet in new_triplets_raw} | {triplet[1] for triplet in new_triplets_raw})
        associated_subgraph = self.get_associated_triplets(items_, steps = 1)
        prompt = prompt_refining_items.format(ex_triplets = associated_subgraph, new_triplets = new_triplets)
        response, cost = self.generate(prompt, t = 0.2)
        predicted_outdated = parse_triplets_removing(response)
        self.delete_triplets(predicted_outdated, locations)
        log("Outdated triplets: " + response)
       
        if curr_location != previous_location:
            new_triplets_raw.append((curr_location, previous_location, {"label": find_direction(action)}))
            new_triplets_raw.append([previous_location, curr_location, {"label": find_opposite_direction(action)}])  


        self.add_triplets(new_triplets_raw)
        
        results = self.retriever.search(
            key_strings=self.get_all_triplets(),
            query_strings=items,
            similarity_threshold=self.threshold, 
            topk=self.topk            
        )
        associated_subgraph = []
        for result in results["strings"]:
            associated_subgraph += result
        log("Associated subgraph: " + str(associated_subgraph))    
        
        return associated_subgraph