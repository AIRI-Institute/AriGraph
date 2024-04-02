import torch
import networkx as nx
from transformers import AutoTokenizer, AutoModelForCausalLM

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
    

        associated_subgraph = self.get_associated_triplets(items + objects, steps = 1)
        log("Associated_subgraph: " + str(associated_subgraph))
        return associated_subgraph
    
class ExtendedGraphPagerankStrategy(ExtendedGraphSubgraphStrategy):
    def __init__(self, model, system_prompt, threshold = 0.02):
        super().__init__(model, system_prompt, threshold)
        self.G = nx.MultiGraph()
        
    def delete_triplets(self, triplets, locations):
        success = super().delete_triplets(triplets, locations)
        for triplet, succ in zip(triplets, success):
            if succ and self.str(clear_triplet(triplet)) in self.G:
                self.G.remove_node(self.str(clear_triplet(triplet)))
                
    def add_triplets(self, triplets):
        success = super().add_triplets(triplets)
        for triplet, succ in zip(triplets, success):
            if succ:
                node_name = self.str(clear_triplet(triplet))
                for existed_triplet in self.triplets:
                    if triplet[0] in existed_triplet or triplet[1] in existed_triplet:
                        self.G.add_edge(node_name, self.str(existed_triplet))
                        
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
    

        associated_subgraph = self.get_associated_triplets_pagerank(new_meta_triplets + new_items_triplets, max_len = 100)
        log("Associated_subgraph: " + str(associated_subgraph))
        return associated_subgraph
    
    def get_associated_triplets_pagerank(self, triplets, max_len):
        part = min(1., 0.4 * max_len / len(self.triplets) + 0.6)
        triplets = [clear_triplet(triplet) for triplet in triplets]
        personalization = {self.str(triplet): 1 / len(triplets) for triplet in triplets}
        done, max_iter = False, 100
        while not done:
            if max_iter > 3200:
                scores = personalization
                done = True
            try:
                scores = nx.pagerank(self.G, personalization=personalization, weight = None, alpha = 0.9, max_iter=max_iter, tol = 1e-3)
                done = True
            except:
                max_iter = int(max_iter * 2)
                
        sum_score = sum([value for value in scores.values()])
        scores = sorted([[value, key] for key, value in scores.items()], reverse=True)
        sorted_triplets, curr_sum = [], 0
        for score, triplet in scores:
            curr_sum += score
            sorted_triplets.append(triplet)
            if curr_sum / sum_score > part:
                break
        return sorted_triplets
    
class ExtendedGraphMixtralPagerankStrategy(ExtendedGraphPagerankStrategy):
    def __init__(self, model, system_prompt, threshold = 0.02):
        super().__init__(model, system_prompt, threshold)
        self.tokenizer = AutoTokenizer.from_pretrained("mistralai/Mixtral-8x7B-Instruct-v0.1")
        self.mixtral = AutoModelForCausalLM.from_pretrained("mistralai/Mixtral-8x7B-Instruct-v0.1", device_map = "auto", torch_dtype = torch.bfloat16)    
        self.device = list(self.mixtral.parameters())[0].device
        
    def t(self, text):
        return self.tokenizer.encode(text, add_special_tokens=False)    
        
    def generate(self, prompt):
        prompt = f"<s>[INST] {self.system_prompt} Hi [/INST] Hello! how can I help you</s>[INST] {prompt} [/INST]"
        inputs = self.tokenizer.encode(prompt, return_tensors="pt", add_special_tokens = False).to(self.device)
        outputs = self.mixtral.generate(inputs, max_new_tokens=1024, do_sample=True)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True), 0
    