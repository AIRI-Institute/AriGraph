import os
import json
import requests
from time import sleep
import numpy as np
from copy import deepcopy
from scipy.spatial.distance import cosine, euclidean
from InstructorEmbedding import INSTRUCTOR

from utils import *
from prompts import *

VPS_IP = "146.0.73.157"
port = 8000
API_KEY = "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"

class TripletGraph:
    # Triplets - list of pairs (triplet, triplet_embedding),
    # where triplet - ((subj, subj_emb), (obj, obj_emb), {"label": relation})
    
    # Items - list of pairs (item, item_emb)
    
    def __init__(self, model, system_prompt, threshold = 0.02):
        self.triplets, self.items, self.threshold = [], [], threshold
        self.model, self.system_prompt = model, system_prompt
        self.instructor = INSTRUCTOR('hkunlp/instructor-large')
        self.total_amount = 0
        
    def save(self, path):
        with open(path + "/TRIPLETS.json", "w") as file:
            json.dump(self.triplets, file)
        with open(path + "/ITEMS.json", "w") as file:
            json.dump(self.items, file)
        metainf = {"model": self.model, "threshold": self.threshold, "system_prompt": self.system_prompt}
        with open(path + "/METAINF.json", "w") as file:
            json.dump(metainf, file)
            
    def load(self, path):
        with open(path + "/TRIPLETS.json", "r") as file:
            self.triplets = json.load(file)
        with open(path + "/ITEMS.json", "r") as file:
            self.items = json.load(file)
        with open(path + "/METAINF.json", "r") as file:
            metainf = json.load(file)
            self.model, self.threshold, self.system_prompt = metainf["model"], metainf["threshold"], metainf["system_prompt"]
        
    def generate(self, prompt, t = 1, jsn = False):
        messages = [{"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}]

        response = requests.post(
            f"http://{VPS_IP}:{port}/openai_api",
            json={"api_key": API_KEY, "messages": messages, "model_type": self.model, "temperature": t, "jsn": jsn}
        )
        resp = response.json()["response"]
        usage = response.json()["usage"]
        cost = usage["completion_tokens"] * 3 / 100000 + usage["prompt_tokens"] * 1 / 100000
        self.total_amount += cost
        sleep(1)
        return resp, cost
    
    # Main function
    def update(self, observation, observations, goal, locations, curr_location, previous_location, action, log):        
         # Extracting triplets
        prompt = prompt_extraction.format(observation = observation, observations = observations)
        response, cost = self.generate(prompt)
        new_triplets_raw = process_triplets(response)
        new_triplets = self.exclude(new_triplets_raw)
        log("New triplets excluded: " + str(new_triplets))
        
        # Using subgraph
        # associated_subgraph = self.get_associated_triplets(items, steps = 2)
        
        #Using full graph
        associated_subgraph = self.get_all_triplets()
        
        # Replacing triplets
        prompt = prompt_refining.format(ex_triplets = associated_subgraph, new_triplets = new_triplets)
        response, cost = self.generate(prompt)
        predicted_outdated = parse_triplets_removing(response)
        log("Outdated triplets: " + response)
        
        # Updating graph
        self.delete_triplets(predicted_outdated, locations)
        if curr_location != previous_location:
            new_triplets_raw.append((curr_location, previous_location, {"label": find_direction(action)}))
        self.add_triplets(new_triplets_raw)
        
        associated_subgraph = self.get_all_triplets()
        log("Associated_subgraph: " + str(associated_subgraph))
        return associated_subgraph
        
        
    def get_embedding_local(self, text, entity = False):
        text = text.replace("\n", " ")
        instruction = "Represent the entity in the knowledge graph:" if entity else "Represent the triplet in the knowledge graph:" 
        embeddings = self.instructor.encode([[instruction, text]])
        return list(map(float, list(embeddings[0])))
    
    def is_equal(self, text1, text2, entity = False):
        embedding1, embedding2 = self.get_embedding_local(text1, entity), self.get_embedding_local(text2, entity)
        return euclidean(embedding1, embedding2) < self.threshold
    
    # For triplet without embeddings
    def str(self, triplet):
        return triplet[0] + ", " + triplet[2]["label"] + ", " + triplet[1]
    
    # For triplet with embeddings
    def str_self(self, triplet):
        return triplet[0][0][0] + ", " + triplet[0][2]["label"] + ", " + triplet[0][1][0]
    
    def contain(self, triplet, embedding, delete = False):
        ans = False
        for contained in self.triplets:
            ans = ans or euclidean(embedding, contained[1]) < self.threshold    
            if ans and delete:
                self.triplets.remove(contained)
                break        
        return ans
    
    # Contain for triplet without embedding
    def contain_raw(self, triplet, delete = False):
        embedding = self.get_embedding_local(self.str(triplet))
        return self.contain(triplet, embedding, delete)
    
    # Method for replacing evaluation
    def compute_stats(self, predicted, true, exclude_nav = False, locations = set()):
        n, n_right, recall = 0, 0, 0
        true_embeddings = [self.get_embedding_local(self.str(clear_triplet(true_triplet))) for true_triplet in true]
        for true_triplet in true:
            true_triplet = clear_triplet(true_triplet)
            if exclude_nav and check_loc(true_triplet, locations): 
                continue
            n_right += 1
        for pred_triplet in predicted:
            pred_triplet = clear_triplet(pred_triplet)
            pred_embedding = self.get_embedding_local(self.str(pred_triplet))
            # breakpoint()
            if not self.contain(pred_triplet, pred_embedding) or (exclude_nav and check_loc(pred_triplet, locations)):
                continue
            n += 1
            for true_embedding, true_triplet in zip(true_embeddings, true):
                true_triplet = clear_triplet(true_triplet)
                # breakpoint()
                if exclude_nav and check_loc(true_triplet, locations): 
                    continue
                if euclidean(true_embedding, pred_embedding) < self.threshold:
                    recall += 1
                    break
        return n, n_right, recall
    
    # Method for extracting + replacing evaluation (compare only existing of relation)
    def compare(self, true, exclude_nav = False, locations=set()):
        n, n_right, recall = 0, 0, 0
        true_embeddings = []
        # breakpoint()
        
        for true_triplet in true:
            true_triplet = clear_triplet(true_triplet)
            if exclude_nav and check_loc(true_triplet, locations): 
                continue
            n_right += 1
            true_embeddings.append((self.get_embedding_local(true_triplet[0], True), self.get_embedding_local(true_triplet[1], True), self.get_embedding_local(true_triplet[2]["label"], True)))
            
            
        for pred_triplet in self.triplets:
            if exclude_nav and check_loc(simplify(pred_triplet), locations):
                continue
            n += 1
            embedding_1, embedding_2 = pred_triplet[0][0][1], pred_triplet[0][1][1]
            for (true_embedding_1, true_embedding_2, true_rel_emb) in true_embeddings:
                if (euclidean(embedding_1, true_embedding_1) < self.threshold and \
                    euclidean(embedding_2, true_embedding_2) < self.threshold) or\
                    (euclidean(embedding_1, true_embedding_2) < self.threshold and \
                    euclidean(embedding_2, true_embedding_1) < self.threshold):
                    relation_emb = self.get_embedding_local(pred_triplet[0][2]["label"], True)
                    # if (euclidean(relation_emb, true_rel_emb) < self.threshold):    
                    recall += 1
                    true_embeddings.remove((true_embedding_1, true_embedding_2, true_rel_emb))
                    break
        # breakpoint()
        return n, n_right, recall
    
    def get_all_triplets(self):
        return [self.str_self(triplet) for triplet in self.triplets]
    
    def delete_all(self):
        self.triplets, self.items = [], []
    
    def add_item(self, item):
        embedding = self.get_embedding_local(item, entity = True)
        for existing_item in self.items:
            if euclidean(existing_item[1], embedding) < self.threshold:
                return existing_item[0]
        self.items.append((item, embedding))
        return item
    
    # Filling graph
    def add_triplets(self, triplets):
        for triplet in triplets:
            if triplet[2]["label"] == "free":
                continue
            triplet = clear_triplet(triplet)
            embedding = self.get_embedding_local(self.str(triplet))
            if not self.contain(triplet, embedding):
                embedding1, embedding2 = self.get_embedding_local(triplet[0], True), self.get_embedding_local(triplet[1], True)
                self.triplets.append(([(triplet[0], embedding1), (triplet[1], embedding2), triplet[2]], embedding))
                self.add_item(triplet[0])
                self.add_item(triplet[1])
                
    # Delete triplets exclude navigation ones            
    def delete_triplets(self, triplets, locations):
        for triplet in triplets:
            first, second = False, False
            for loc in locations:
                if self.is_equal(triplet[0], loc, True):
                    first = True
                if self.is_equal(triplet[1], loc, True):
                    second = True
            if first and second:
                continue
            embedding = self.get_embedding_local(self.str(triplet))
            self.contain(triplet, embedding, delete = True)
            
    # Associations by set of items. Step is a parameter for BFS
    def get_associated_triplets(self, items, steps = 1):
        associated_triplets = []
        visited_items = set()
        now = set()
        for triplet in self.triplets:
            for item in items:
                embedding = self.get_embedding_local(item, entity = True)
                if euclidean(embedding, triplet[0][0][1]) < self.threshold:
                    associated_triplets.append(self.str_self(triplet))
                    visited_items.add(triplet[0][0][0])
                    visited_items.add(triplet[0][1][0])
                    now.add(triplet[0][1][0])
                    break
                if euclidean(embedding, triplet[0][1][1]) < self.threshold:
                    associated_triplets.append(self.str_self(triplet))
                    visited_items.add(triplet[0][0][0])
                    visited_items.add(triplet[0][1][0])
                    now.add(triplet[0][0][0])
                    break
        
        if "itself" in now:
            now.remove("itself")
        for i in range(steps - 1):
            now_emb = [(it, self.get_embedding_local(it, entity = True)) for it in now]
            now = set()
            for triplet in self.triplets:
                for it, emb in now_emb:
                    if euclidean(emb, triplet[0][0][1]) < self.threshold and self.str_self(triplet) not in visited_items:
                        associated_triplets.append(self.str_self(triplet))
                        if triplet[0][1][0] not in visited_items:
                            now.add(triplet[0][1][0])
                        visited_items.add(triplet[0][0][0])
                        visited_items.add(triplet[0][1][0])
                        break
                    if euclidean(embedding, triplet[0][1][1]) < self.threshold and self.str_self(triplet) not in visited_items:
                        associated_triplets.append(self.str_self(triplet))
                        if triplet[0][0][0] not in visited_items:
                            now.add(triplet[0][0][0])
                        visited_items.add(triplet[0][0][0])
                        visited_items.add(triplet[0][1][0])
                        break
            if "itself" in now:
                now.remove("itself")          
        return associated_triplets
    
    # Exclude facts from 'triplets' which already in graph
    def exclude(self, triplets):
        new_triplets = []
        for triplet in triplets:
            triplet = clear_triplet(triplet)
            embedding = self.get_embedding_local(self.str(triplet))
            if not self.contain(triplet, embedding):
                new_triplets.append(self.str(triplet))
                
        return new_triplets
    
    # Compute useful shape of graph with only spatial information
    def compute_spatial_graph(self, locations):
        locations = deepcopy(locations)
        if "player" in locations:
            locations.remove("player")
        graph = {}
        for triplet in self.triplets:
            if triplet[0][2]["label"] == "free":
                continue
            if triplet[0][0][0] in locations and triplet[0][1][0] in locations:
                if triplet[0][0][0] in graph:
                    graph[triplet[0][0][0]]["connections"].append((triplet[0][2]["label"], triplet[0][1][0]))
                else:
                    graph[triplet[0][0][0]] = {"connections": [(triplet[0][2]["label"], triplet[0][1][0])]}
                
                if triplet[0][1][0] in graph:
                    graph[triplet[0][1][0]]["connections"].append(("reversed", triplet[0][0][0]))
                else:
                    graph[triplet[0][1][0]] = {"connections": [("reversed", triplet[0][0][0])]}
                    
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
        items = [item[0] for item in self.items]
        if A not in items or B not in items:
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
                