import os
import json
import numpy as np
from copy import deepcopy
from scipy.spatial.distance import cosine
from InstructorEmbedding import INSTRUCTOR

# Must be with emb!
def check_loc(triplet, locations):
    return triplet[0] in locations and triplet[1] in locations

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
        true_embeddings = [self.get_embedding_local(self.str(true_triplet)) for true_triplet in true]
        for pred_triplet in predicted:
            pred_embedding = self.get_embedding_local(self.str(pred_triplet))
            if not self.contain(pred_triplet, pred_embedding) or (exclude_nav and check_loc(pred_triplet, locations)):
                continue
            n += 1
            for true_embedding, true_triplet in zip(true_embeddings, true):
                if exclude_nav and check_loc(true_triplet, locations): 
                    continue
                n_right += 1
                if cosine(true_embedding, pred_embedding) < self.threshold:
                    recall += 1
                    break
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
            if triplet[0] == "I":
                triplet = ("inventory", triplet[1], triplet[2])
            if triplet[1] == "I":
                triplet = (triplet[0], "inventory", triplet[2])
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
            if triplet[0] == "I":
                triplet = ("inventory", triplet[1], triplet[2])
            if triplet[1] == "I":
                triplet = (triplet[0], "inventory", triplet[2])
            embedding = self.get_embedding_local(self.str(triplet))
            if not self.contain(triplet, embedding):
                new_triplets.append(self.str(triplet))
                
        return new_triplets
        
                