import re
from copy import deepcopy

from utils.contriever import Retriever
from graphs.parent_graph import TripletGraph
from utils.retriever_search_drafts import graph_retr_search
from prompts.prompts import prompt_extraction_current, prompt_refining_items

from utils.utils import process_triplets, parse_triplets_removing, \
    find_direction, find_opposite_direction, find_top_episodic_emb, \
    top_k_obs, clear_triplet

class ContrieverGraph(TripletGraph):
    def __init__(self, model, system_prompt, api_key, device = "cpu"):
        super().__init__(model, system_prompt, api_key)
        self.retriever = Retriever(device)
        self.triplets_emb, self.items_emb = {}, {}
        self.obs_episodic, self.obs_episodic_list, self.top_episodic_dict_list = {}, [], []
        
    def clear(self):
        self.triplets = []
        self.total_amount = 0
        self.triplets_emb, self.items_emb = {}, {}
        self.obs_episodic, self.obs_episodic_list, self.top_episodic_dict_list = {}, [], []
        
    def update(self, observation, observations, plan, prev_subgraph, locations, curr_location, previous_location, action, items1, log, topk_episodic):        
        example = [re.sub(r"Step \d+: ", "", triplet) for triplet in prev_subgraph]
        prompt = prompt_extraction_current.format(observation = observation, example = example)
        response, _ = self.generate(prompt, t = 0.001)
        new_triplets_raw = process_triplets(response)
        
        new_triplets = self.exclude(new_triplets_raw)
        new_triplets_str = self.convert(new_triplets_raw)
        
        log("New triplets: " + str(new_triplets))       
        items_ = {triplet[0] for triplet in new_triplets_raw} | {triplet[1] for triplet in new_triplets_raw}        
        associated_subgraph = self.get_associated_triplets(items_, steps = 1)
        words_to_exclude = ['west', 'east', 'south', 'north', 'associated with', 'used for', 'to be']
        associated_subgraph = [item for item in associated_subgraph if not any(word in item for word in words_to_exclude)]

        prompt = prompt_refining_items.format(ex_triplets = associated_subgraph, new_triplets = new_triplets)
        response, _ = self.generate(prompt, t = 0.001)
        predicted_outdated = parse_triplets_removing(response)
        self.delete_triplets(predicted_outdated, locations)
        log("Outdated triplets: " + response)
        log("NUMBER OF REPLACEMENTS: " + str(len(predicted_outdated)))
       
        if "go to" not in action:
            if curr_location != previous_location:
                new_triplets_raw.append([curr_location, previous_location, {"label": find_direction(action)}])
                new_triplets_raw.append([previous_location, curr_location, {"label": find_opposite_direction(action)}])

        self.add_triplets(new_triplets_raw)

        triplets = self.triplets_to_str(self.triplets)
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

        associated_subgraph = [element for element in associated_subgraph if element not in new_triplets_str]

        obs_plan_embeddings = self.retriever.embed((plan))
        top_episodic_dict = find_top_episodic_emb(prev_subgraph, deepcopy(self.obs_episodic), obs_plan_embeddings, self.retriever)
        top_episodic = top_k_obs(top_episodic_dict, k=topk_episodic)

        top_episodic = [item for item in top_episodic if item not in observations]
        
        obs_embedding = self.retriever.embed(observation)
        obs_value = [new_triplets_str, obs_embedding]
        self.obs_episodic[observation] = obs_value

        self.obs_episodic_list.append(deepcopy(self.obs_episodic))
        self.top_episodic_dict_list.append(top_episodic_dict)
        
        return associated_subgraph, top_episodic
    
    def update_without_retrieve(self, observation, prev_subgraph, log):
        example = [re.sub(r"Step \d+: ", "", triplet) for triplet in prev_subgraph]
        prompt = prompt_extraction_current.format(observation = observation, example = example)
        response, _ = self.generate(prompt, t = 0.001)
        new_triplets_raw = process_triplets(response)
        
        new_triplets = self.exclude(new_triplets_raw)
        new_triplets_str = self.convert(new_triplets_raw)
        
        log("New triplets: " + str(new_triplets))        
        # items_ = {triplet[0] for triplet in new_triplets_raw} | {triplet[1] for triplet in new_triplets_raw}        
        # associated_subgraph = self.get_associated_triplets(items_, steps = 1)
        # words_to_exclude = []
        # associated_subgraph = [item for item in associated_subgraph if not any(word in item for word in words_to_exclude)]

        # prompt = prompt_refining_items.format(ex_triplets = associated_subgraph, new_triplets = new_triplets)
        # response, _ = self.generate(prompt, t = 0.001)
        # predicted_outdated = parse_triplets_removing(response)
        # self.delete_triplets(predicted_outdated, set())
        # log("Outdated triplets: " + response)
        self.add_triplets(new_triplets_raw)
        
        obs_embedding = self.retriever.embed(observation)
        obs_value = [new_triplets_str, obs_embedding]
        self.obs_episodic[observation] = obs_value
        return new_triplets_raw, obs_value
    
    def retrieve(self, items1, retrieve_base, retrieve_facts, topk_episodic):
        triplets = self.triplets_to_str(self.triplets)
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

        associated_subgraph = [element for element in associated_subgraph]

        obs_plan_embeddings = self.retriever.embed((retrieve_base))
        top_episodic_dict = find_top_episodic_emb(associated_subgraph, deepcopy(self.obs_episodic), obs_plan_embeddings, self.retriever)
        top_episodic = top_k_obs(top_episodic_dict, k=topk_episodic)

        top_episodic = [item for item in top_episodic]
        return associated_subgraph, top_episodic
    
    def triplets_to_str(self, triplets):
        return [self.str(triplet) for triplet in triplets]  
    
    def convert(self, triplets):
        new_triplets = []
        for triplet in triplets:
            triplet = clear_triplet(triplet)
            new_triplets.append(self.str(triplet))
                
        return new_triplets    
    
    def get_embedding_local(self, text):
        return self.retriever.embed([text])[0].cpu().detach().numpy()
    
    
    def add_triplets(self, triplets):
        for triplet in triplets:
            if triplet[2]["label"] == "free":
                continue
            triplet = clear_triplet(triplet)
            if triplet not in self.triplets:
                self.triplets.append(triplet)
                self.triplets_emb[self.str(triplet)] = self.get_embedding_local(self.str(triplet))
                if triplet[0] not in self.items_emb:
                    self.items_emb[triplet[0]] = self.get_embedding_local(triplet[0])
                if triplet[1] not in self.items_emb:
                    self.items_emb[triplet[1]] = self.get_embedding_local(triplet[1])
                    
    def delete_triplets(self, triplets, locations):
        for triplet in triplets:
            if triplet[0] in locations and triplet[1] in locations:
                continue
            if triplet in self.triplets:
                self.triplets.remove(triplet)
                self.triplets_emb.pop(self.str(triplet))
    
    def get_triplets_by_ids(self, best_ids):
        return [self.triplets[i] for i in best_ids]
    
    def find_current_items(self, triplets):
        items = {triplet[0] for triplet in triplets} | {triplet[1] for triplet in triplets}
        return {item: self.items_emb[item] for item in items}
    
    def filter_associated(self, triplets):
        return [triplet for triplet in triplets if "associated with" not in triplet]
        
            

            
                    
class LLaMAContrieverGraph(ContrieverGraph):
    def __init__(self, model, system_prompt, api_key, pipeline, device = "cpu"):
        super().__init__(model, system_prompt, api_key, device)
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
            