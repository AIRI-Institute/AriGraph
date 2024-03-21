import os
import json
import numpy as np
from copy import deepcopy
from scipy.spatial.distance import cosine
from InstructorEmbedding import INSTRUCTOR

# Must be with emb!
def check_loc(triplet, locations):
    return triplet[0] in locations and triplet[1] in locations

def simplify(triplet):
    return (triplet[0][0][0], triplet[0][1][0],  {"label": triplet[0][2]["label"] })

def check_conn(connection):
    return "north" in connection or "south" in connection or "east" in connection or "west" in connection

def clear_triplet(triplet):
    if triplet[0] == "I":
        triplet = ("inventory", triplet[1], triplet[2])
    if triplet[1] == "I":
        triplet = (triplet[0], "inventory", triplet[2])
    if triplet[0] == "P":
        triplet = ("player", triplet[1], triplet[2])
    if triplet[1] == "P":
        triplet = (triplet[0], "player", triplet[2])
    return triplet

def find_relation(spatial_graph, parent, loc, first):
    reverse = {
        "north": "south", "south": "north", "east": "west", "west": "east"
    }
    for connection in spatial_graph[parent]["connections"]:
        if connection[1] == loc:
            if "north" in connection[0]:
                return "south"
            if "east" in connection[0]:
                return "west"
            if "south" in connection[0]:
                return "north"
            if "west" in connection[0]:
                return "east"
            if "reversed" in connection[0] and first:
                return reverse[find_relation(spatial_graph, loc, parent, False)]

class TripletGraph:
    def __init__(self, threshold = 0.02):
        self.triplets, self.items, self.threshold = [], [], threshold
        self.instructor = INSTRUCTOR('hkunlp/instructor-large')
        
    def get_embedding_local(self, text, entity = False):
        text = text.replace("\n", " ")
        instruction = "Represent the entity in the knowledge graph:" if entity else "Represent the triplet in the knowledge graph:" 
        embeddings = self.instructor.encode([[instruction, text]])
        return list(map(float, list(embeddings[0])))
    
    def is_equal(self, text1, text2, entity = False):
        embedding1, embedding2 = self.get_embedding_local(text1, entity), self.get_embedding_local(text2, entity)
        return cosine(embedding1, embedding2) < self.threshold
    
    def str(self, triplet):
        return triplet[0] + ", " + triplet[2]["label"] + ", " + triplet[1]
    
    def str_self(self, triplet):
        return triplet[0][0][0] + ", " + triplet[0][2]["label"] + ", " + triplet[0][1][0]
    
    def contain(self, triplet, embedding, delete = False):
        ans = False
        for contained in self.triplets:
            ans = ans or cosine(embedding, contained[1]) < self.threshold    
            if ans and delete:
                self.triplets.remove(contained)
                break        
        return ans
    
    def contain_raw(self, triplet, delete = False):
        embedding = self.get_embedding_local(self.str(triplet))
        return self.contain(triplet, embedding, delete)
    
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
                if cosine(true_embedding, pred_embedding) < self.threshold:
                    recall += 1
                    break
        return n, n_right, recall
    
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
                if (cosine(embedding_1, true_embedding_1) < self.threshold and \
                    cosine(embedding_2, true_embedding_2) < self.threshold) or\
                    (cosine(embedding_1, true_embedding_2) < self.threshold and \
                    cosine(embedding_2, true_embedding_1) < self.threshold):
                    relation_emb = self.get_embedding_local(pred_triplet[0][2]["label"], True)
                    # if (cosine(relation_emb, true_rel_emb) < self.threshold):    
                    recall += 1
                    break
        # breakpoint()
        return n, n_right, recall
    
    def get_all_triplets(self):
        return [self.str_self(triplet) for triplet in self.triplets]
    
    def add_item(self, item):
        embedding = self.get_embedding_local(item, entity = True)
        for existing_item in self.items:
            if cosine(existing_item[1], embedding) < self.threshold:
                return existing_item[0]
        self.items.append((item, embedding))
        return item
    
    def add_triplets(self, triplets):
        for triplet in triplets:
            triplet = clear_triplet(triplet)
            embedding = self.get_embedding_local(self.str(triplet))
            if not self.contain(triplet, embedding):
                embedding1, embedding2 = self.get_embedding_local(triplet[0], True), self.get_embedding_local(triplet[1], True)
                self.triplets.append(([(triplet[0], embedding1), (triplet[1], embedding2), triplet[2]], embedding))
                self.add_item(triplet[0])
                self.add_item(triplet[1])
                
    def delete_triplets(self, triplets):
        for triplet in triplets:
            embedding = self.get_embedding_local(self.str(triplet))
            self.contain(triplet, embedding, delete = True)
            
    def get_associated_triplets(self, items):
        associated_triplets = []
        for triplet in self.triplets:
            for item in items:
                embedding = self.get_embedding_local(item, entity = True)
                if cosine(embedding, triplet[0][0][1]) < self.threshold or cosine(embedding, triplet[0][1][1]) < self.threshold:
                    associated_triplets.append(self.str_self(triplet))
                    break
        return associated_triplets
    
    def exclude(self, triplets):
        new_triplets = []
        for triplet in triplets:
            triplet = clear_triplet(triplet)
            embedding = self.get_embedding_local(self.str(triplet))
            if not self.contain(triplet, embedding):
                new_triplets.append(self.str(triplet))
                
        return new_triplets
    
    # Must be with emb!
    def compute_spatial_graph(self, locations):
        locations = deepcopy(locations)
        locations.remove("player")
        graph = {}
        for triplet in self.triplets:
            if triplet[0][0][0] in locations and triplet[0][1][0] in locations and triplet[0][2]["label"] != "free":
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
    
    # Must be with emb!
    def find_path(self, A, B, locations):
        if A == B:
            return "You are already there"
        items = [item[0] for item in self.items]
        if A not in items or B not in items:
            return "Destionation is unknown. Please, choose another destination or explore new paths and locations."
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
                