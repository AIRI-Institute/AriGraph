import re
from copy import deepcopy

from graphs.contriever_graph import ContrieverGraph
from utils.retriever_search_drafts import graph_retr_search
from prompts.prompts import prompt_extraction_current, prompt_refining_items, \
    reflex_prompt

from utils.utils import process_triplets, parse_triplets_removing, \
    find_direction, find_opposite_direction, find_top_episodic_emb, \
    top_k_obs, clear_triplet, check_conn

class ReflexiveGraph(ContrieverGraph):
    def __init__(self, model, system_prompt, api_key, device = "cpu"):
        super().__init__(model, system_prompt, api_key, device)
        self.meta_triplets = []
        self.obs_meta, self.obs_meta_list, self.top_meta_dict_list = {}, [], []
        
    def reset(self):
        self.triplets_emb, self.triplets = {}, []
        self.obs_episodic, self.obs_episodic_list, self.top_episodic_dict_list = {}, [], []
        
    def add_triplets_meta(self, triplets):
        for triplet in triplets:
            if triplet[2]["label"] == "free":
                continue
            triplet = clear_triplet(triplet)
            if triplet not in self.meta_triplets:
                self.meta_triplets.append(triplet)
                self.triplets_emb[self.str(triplet)] = self.get_embedding_local(self.str(triplet))
                if triplet[0] not in self.items_emb:
                    self.items_emb[triplet[0]] = self.get_embedding_local(triplet[0])
                if triplet[1] not in self.items_emb:
                    self.items_emb[triplet[1]] = self.get_embedding_local(triplet[1])
                    
    def delete_triplets(self, triplets, locations):
        for triplet in triplets:
            if triplet[0] in locations and triplet[1] in locations:
                continue
            if triplet in self.meta_triplets:
                self.meta_triplets.remove(triplet)
                self.triplets_emb.pop(self.str(triplet))
            if triplet in self.triplets:
                self.triplets.remove(triplet)
                self.triplets_emb.pop(self.str(triplet))
        
    def update(self, observation, observations, plan, prev_subgraph, locations, curr_location, \
            previous_location, action, items1, log, topk_episodic, \
            for_reflex, topk_reflections, prev_meta_subgraph):  
        is_reflex = len(for_reflex) > 2
              
        example = [re.sub(r"Step \d+: ", "", triplet) for triplet in prev_subgraph]
        prompt = prompt_extraction_current.format(observation = observation, example = example)
        response, _ = self.generate(prompt, t = 0.)
        new_triplets_raw = process_triplets(response)
        
        new_triplets = self.exclude(new_triplets_raw)
        new_triplets_str = self.convert(new_triplets_raw)
        log("New triplets: " + str(new_triplets))   
        
        new_triplets_raw_meta, new_triplets_meta = [], []
        if is_reflex:
            reflection = self.reflex(for_reflex)
            meta_example = [re.sub(r"Step \d+: ", "", triplet) for triplet in prev_meta_subgraph]
            prompt = prompt_extraction_current.format(observation = reflection, example = meta_example)
            response, _ = self.generate(prompt, t = 0.)
            new_triplets_raw_meta = process_triplets(response)
            new_triplets_meta = self.exclude(new_triplets_raw_meta)
            new_triplets_str_meta = self.convert(new_triplets_raw_meta)
            log("New meta triplets: " + str(new_triplets_meta))   
                 
        for_search = new_triplets_raw + new_triplets_raw_meta
        items_ = {triplet[0] for triplet in for_search} | {triplet[1] for triplet in for_search}        
        associated_subgraph = self.get_associated_triplets(items_, steps = 1) + self.get_associated_triplets_meta(items_, steps = 1)
        words_to_exclude = ['west', 'east', 'south', 'north', 'associated with', 'used for', 'to be']
        associated_subgraph = [item for item in associated_subgraph if not any(word in item for word in words_to_exclude)]

        prompt = prompt_refining_items.format(ex_triplets = associated_subgraph, new_triplets = new_triplets + new_triplets_meta)
        response, _ = self.generate(prompt, t = 0.)
        predicted_outdated = parse_triplets_removing(response)
        self.delete_triplets(predicted_outdated, locations)
        log("Outdated triplets: " + response)
       
        if "go to" not in action:
            if curr_location != previous_location:
                new_triplets_raw_meta.append([curr_location, previous_location, {"label": find_direction(action)}])
                new_triplets_raw_meta.append([previous_location, curr_location, {"label": find_opposite_direction(action)}])

        self.add_triplets(new_triplets_raw)
        self.add_triplets_meta(new_triplets_raw_meta)

        triplets = self.triplets_to_str(self.triplets + self.meta_triplets)
        associated_subgraph = set()
        
        #retrieve for dict of items

        for query, depth in items1.items():  # items1 is now a dictionary
            results = graph_retr_search(
                query, triplets, self.retriever, max_depth=depth,  
                topk=6,
                post_retrieve_threshold=0.75, 
                verbose=2
            )
            associated_subgraph.update(results)

        associated_subgraph_meta = [element for element in associated_subgraph if element not in (new_triplets_str + self.triplets_to_str(self.triplets))]
        associated_subgraph = [element for element in associated_subgraph if element not in (new_triplets_str + associated_subgraph_meta)]

        obs_plan_embeddings = self.retriever.embed((plan))
        top_episodic_dict = find_top_episodic_emb(prev_subgraph, deepcopy(self.obs_episodic), obs_plan_embeddings, self.retriever)
        top_episodic = top_k_obs(top_episodic_dict, k=topk_episodic)

        top_episodic = [item for item in top_episodic if item not in observations]
        
        obs_embedding = self.retriever.embed(observation)
        obs_value = [new_triplets_str, obs_embedding]
        self.obs_episodic[observation] = obs_value

        self.obs_episodic_list.append(deepcopy(self.obs_episodic))
        self.top_episodic_dict_list.append(top_episodic_dict)
        
        top_episodic_meta = []
        if is_reflex:
            top_episodic_dict_meta = find_top_episodic_emb(prev_meta_subgraph, deepcopy(self.obs_meta), obs_plan_embeddings, self.retriever)
            top_episodic_meta = list(top_k_obs(top_episodic_dict_meta, k=topk_reflections))
            
            obs_embedding_meta = self.retriever.embed(reflection)
            obs_value_meta = [new_triplets_str_meta, obs_embedding_meta]
            self.obs_meta[reflection] = obs_value_meta

            self.obs_meta_list.append(deepcopy(self.obs_meta))
            self.top_meta_dict_list.append(top_episodic_dict_meta)
        
        return associated_subgraph, associated_subgraph_meta, top_episodic, top_episodic_meta, reflection if is_reflex else "Nothing there"
    
    def get_associated_triplets_meta(self, items, steps = 2):
        items = deepcopy([string.lower() for string in items])
        associated_triplets = []

        for i in range(steps):
            now = set()
            for triplet in self.meta_triplets:
                for item in items:
                    
                    if (item == triplet[0] or item == triplet[1]) and self.str(triplet) not in associated_triplets:
                        associated_triplets.append(self.str(triplet))
                        if item == triplet[0]:
                            now.add(triplet[1])
                        if item == triplet[1]:
                            now.add(triplet[0])    
                        
                        break
                    
            if "itself" in now:
                now.remove("itself")  
            items = now
        return associated_triplets
    
    def reflex(self, for_reflex):
        prompt = reflex_prompt.format(for_reflex = for_reflex)
        response, _ = self.generate(prompt, t = 0.)
        return response
    
    def compute_spatial_graph(self, locations):
        locations = deepcopy(locations)
        if "player" in locations:
            locations.remove("player")
        graph = {}
        for triplet in self.meta_triplets:
            if triplet[0] in locations and triplet[1] in locations and check_conn(triplet[2]["label"]):
                if triplet[0] in graph:
                    graph[triplet[0]]["connections"].append((triplet[2]["label"], triplet[1]))
                else:
                    graph[triplet[0]] = {"connections": [(triplet[2]["label"], triplet[1])]}
                
                if triplet[1] in graph:
                    graph[triplet[1]]["connections"].append(("reversed", triplet[0]))
                else:
                    graph[triplet[1]] = {"connections": [("reversed", triplet[0])]}
                    
        for loc in graph:
            connections = deepcopy(graph[loc]["connections"])
            connected_loc = [connection[1] for connection in connections if check_conn(connection[0])]
            for connection in connections:
                if connection[1] in connected_loc and connection[0] == "reversed":
                    graph[loc]["connections"].remove(connection)
        return graph