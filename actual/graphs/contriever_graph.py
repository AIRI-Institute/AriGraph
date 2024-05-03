import numpy as np

from utils import *
from prompts import *
from prompts_v2 import *
from graphs.parent_without_emb import GraphWithoutEmbeddings
from contriever import Retriever

class ContrieverGraph(GraphWithoutEmbeddings):
    def __init__(self, model, system_prompt, depth, threshold = None, topk = None, device = "cpu"):
        super().__init__(model, system_prompt, 0.1)
        self.retriever = Retriever(device)
        self.threshold, self.topk, self.depth = threshold, topk, depth
        self.triplets_emb, self.items_emb = {}, {}
        
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
        
        # associated_subgraph = self.reasoning(items)  
        self.expand_graph(threshold = 0.9)
        associated_subgraph = self.beam_search_on_triplets(items, observation, plan, deepcopy(new_triplets_raw), depth = 4, width = 7, log = log)
 
        return associated_subgraph
    
    def add_triplets(self, triplets):
        for triplet in triplets:
            if triplet[2]["label"] == "free":
                continue
            triplet = clear_triplet(triplet)
            if triplet not in self.triplets:
                self.triplets.append(triplet)
                self.triplets_emb[self.str(triplet)] = self.retriever.embed([self.str(triplet)])[0].cpu().detach().numpy()
                if triplet[0] not in self.items_emb:
                    self.items_emb[triplet[0]] = self.retriever.embed([triplet[0]])[0].cpu().detach().numpy()
                if triplet[1] not in self.items_emb:
                    self.items_emb[triplet[1]] = self.retriever.embed([triplet[1]])[0].cpu().detach().numpy()
                    
    def reasoning(self, items):
        scores_hist = []
        scores = np.zeros(len(self.triplets))
        current_items = {item: self.retriever.embed([item])[0].cpu().detach().numpy() if item not in self.items_emb\
                            else self.items_emb[item]\
                            for item in items}
        for it in range(self.depth):
            iter_matrix = self.compute_iter_matrix(current_items)
            iter_scores = self.aggregate_scores_matrix(iter_matrix)
            scores += iter_scores
            best_ids = np.argsort(scores)[-self.topk:]
            current_triplets = self.get_triplets_by_ids(best_ids)
            current_items = self.find_current_items(current_triplets)
            scores_hist.append(np.copy(scores))
        
        return [self.str(triplet) for triplet in current_triplets], scores_hist
    
    def get_triplets_by_ids(self, best_ids):
        return [self.triplets[i] for i in best_ids]
    
    def find_current_items(self, triplets):
        items = {triplet[0] for triplet in triplets} | {triplet[1] for triplet in triplets}
        return {item: self.items_emb[item] for item in items}
    
    def aggregate_scores_matrix(self, matrix):
        return np.max(matrix, axis = -1)
    
    def compute_iter_matrix(self, items):
        matrix = [
            [np.dot(embedding_item, embedding_triplet) for embedding_item in items.values()] 
                for embedding_triplet in self.triplets_emb.values()
        ]
        return np.array(matrix)
    
    def expand_graph(self, threshold, force_connect = False):
        matrix = np.array([
            [np.dot(embedding_item1, embedding_item2) for embedding_item1 in self.items_emb.values()] 
                for embedding_item2 in self.items_emb.values()
        ])
        items = list(self.items_emb.keys())
        conn_matrix = [[0] * len(items) for _ in items]
        for triplet in self.triplets:
            idx1, idx2 = items.index(triplet[0]), items.index(triplet[1])
            conn_matrix[idx1][idx2] = 1
            conn_matrix[idx2][idx1] = 1
        
        for_add = []
        for i in range(matrix.shape[0]):
            for j in range(i + 1, matrix.shape[1]):
                if matrix[i][j] > threshold and conn_matrix[i][j] == 0:
                    for_add.append([items[i], items[j], {"label": "associated with"}])
        self.add_triplets(for_add)
        if force_connect:
            connections = self.find_connections(matrix)
            self.add_triplets(connections)
        
    def find_connections(self, matrix):
        connections = []
        items = list(self.items_emb.keys())
        components = self.find_components()
        for i in range(len(components) - 1):
            for j in range(i + 1, len(components)):
                idx1, idx2, maximum = 0, 0, -1
                for k in components[i]:
                    for l in components[j]:
                        if matrix[k][l] > maximum:
                            idx1, idx2, maximum = k, l, matrix[k][l]
                connections.append([items[idx1], items[idx2], {"label": "associated with"}])
        return connections
    
    def find_components(self):
        visited = set()
        components = []
        items = list(self.items_emb.keys())
        while len(visited) < len(items):
            start_item, start_idx = items[0], 0
            while start_item in visited:
                start_idx += 1
                start_item = items[start_idx]
            visited.add(start_item)
            component = [start_idx]
            current, future = {start_item}, set()
            while len(current) > 0:
                for item in current:
                    for triplet in self.triplets:
                        if triplet[0] == item and triplet[1] not in visited:
                            idx = items.index(triplet[1])
                            component.append(idx)
                            visited.add(triplet[1])
                            future.add(triplet[1])
                        if triplet[1] == item and triplet[0] not in visited:
                            idx = items.index(triplet[0])
                            component.append(idx)
                            visited.add(triplet[0])
                            future.add(triplet[0])
                current = deepcopy(future)
                future = set()
            components.append(component)
        return components
            
        
    def beam_search_on_triplets(self, items, observation, plan, visited, depth, width, log):
        items = set(items)
        visited = {self.str(clear_triplet(triplet)) for triplet in visited}
        chosen = set()
        for step in range(depth):
            candidates = [self.str(triplet) for triplet in self.triplets 
                          if (triplet[0] in items or triplet[1] in items) and self.str(triplet) not in visited]
            log("Length of candidates: " + str(len(candidates)))
            for triplet in candidates:
                visited.add(triplet)
            if not candidates:
                break
            
            prompt = prompt_choose_triplets.format(descr = observation + f"\nYour plan: {plan}", triplets = chosen, candidates = candidates, number = width)
            response, cost = self.generate(prompt, t = 0.2)
            filtered_candidates = process_candidates(response)
            items = {self.add_item(triplet[0]) for triplet in filtered_candidates} | {self.add_item(triplet[1]) for triplet in filtered_candidates}
            for triplet in filtered_candidates:
                chosen.add(self.str(triplet))
        chosen = list(chosen)
        return chosen
        
        
            