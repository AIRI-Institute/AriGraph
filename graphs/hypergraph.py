import ast
import torch
import numpy as np
from copy import deepcopy

from graphs.contriever_graph import ContrieverGraph
from utils.retriever_search_drafts import graph_retr_search_thesises
from prompts.prompts import prompt_extraction_thesises, \
    prompt_refining_thesises
from utils.utils import process_thesises, find_direction, find_opposite_direction, \
    sort_scores

class Hyperedge:
    def __init__(self, name, embedding, parent, children = []):
        self.name, self.parents, self.embedding, self.children = \
             name, [parent], embedding, list(set(children))
    
    def add_children(self, children):
        self.children = list(set(self.children + children))
        
    def add_parent(self, parent):
        if parent not in self.parents:
            self.parents.append(parent)
        
class Entity:
    def __init__(self, name, embedding, parent):
        self.name, self.parents, self.embedding = \
             name, [parent], embedding
             
    def add_parent(self, parent):
        if parent not in self.parents:
            self.parents.append(parent)
            
    def delete_parent(self, parent):
        if parent in self.parents:
            self.parents.remove(parent)
            
class Event:
    def __init__(self, name, embedding, children = []):
        self.name, self.embedding, self.children = \
             name, embedding, list(set(children))
    
    def add_children(self, children):
        self.children = list(set(self.children + children))
        
    def delete_child(self, child):
        if child in self.children:
            self.children.remove(child)
        

class Hypergraph(ContrieverGraph):
    def __init__(self, model, system_prompt, api_key, device = "cpu"):
        super().__init__(model, system_prompt, api_key, device)
        self.thesises, self.entities, self.events = \
            {}, {}, {}
        

    def add(self, thesises, event):
        thesises, event = self.clear(thesises, event)
        event_id = hash(event)
        thesises_ids = []
        for thesis in thesises:
            entities_ids = []
            thesis_id = hash(thesis["name"])
            for entity in thesis["entities"]:
                entity_emb = self.get_embedding_local(entity)
                entity_id = hash(entity)
                if entity_id not in self.entities:
                    self.entities[entity_id] = Entity(entity, entity_emb, thesis_id)
                else:
                    self.entities[entity_id].add_parent(thesis_id)
                entities_ids.append(entity_id)
                
            thesis_emb = self.get_embedding_local(thesis["name"])
            if thesis_id not in self.thesises:
                self.thesises[thesis_id] = Hyperedge(thesis["name"], thesis_emb, event_id, entities_ids)
            else:
                self.thesises[thesis_id].add_parent(event_id)
                self.thesises[thesis_id].add_children(entities_ids)
            thesises_ids.append(thesis_id)
            
        event_emb = self.get_embedding_local(event)
        if event_id not in self.events:
            self.events[event_id] = Event(event, event_emb, thesises_ids)
        else:
            self.events[event_id].add_children(thesises_ids)
            
    def delete_thesises(self, thesises_names):
        for name in thesises_names:
            thesis_id = hash(name)
            if thesis_id not in self.thesises:
                continue
            
            for parent in self.thesises[thesis_id].parents:
                self.events[parent].delete_child(thesis_id)
            for child in self.thesises[thesis_id].children:
                self.entities[child].delete_parent(thesis_id)
            self.thesises.pop(thesis_id)
                
    def clear(self, thesises, event):
        new_event = event.lower().strip(''' '"/|`''')
        new_thesises = []
        for thesis in thesises:
            new_thesis = {
                "name": thesis["name"].lower().strip(''' '"/|`'''),
                "entities": [entity.lower().strip(''' '"/|`''') for entity in thesis["entities"]]
            }
            new_thesises.append(new_thesis)
        return new_thesises, new_event
    
    def bfs(self, starts, steps = 1):
        now = set(starts)
        future = set()
        total = set(starts)
        visited_thesises, step = [], 0
        while now and step < steps:
            for entity in now:
                entity_id = hash(entity)
                if entity_id not in self.entities:
                    continue
                for thesis_id in self.entities[entity_id].parents:
                    visited_thesises.append(self.thesises[thesis_id].name)
                    for child_id in self.thesises[thesis_id].children:
                        candidate_name = self.entities[child_id].name
                        if candidate_name not in total:
                            total.add(candidate_name)
                            future.add(candidate_name)
            now = deepcopy(future)
            future = set()
            step += 1
        return visited_thesises
    
    
    def update(self, observation, history, plan, curr_location, previous_location, action, items1, log, topk_episodic):  
        # Extraction new thesises      
        prompt = prompt_extraction_thesises + f'''
####
INPUT TEXT: {observation}
####
Your answer: '''
        response, _ = self.generate(prompt, t = 0.)
        new_thesises_raw = process_thesises(response)
        
        only_names = [thesis["name"] for thesis in new_thesises_raw]
        log("New thesises: " + response)  
        
        # Remove outdated and inaccurate thesises      
        items_ = []
        for thesis in  new_thesises_raw:
            items_ += thesis["entities"]       
        associated_subgraph = self.bfs(items_, steps = 1)

        prompt = prompt_refining_thesises.format(ex_thesises = associated_subgraph, new_thesises = only_names)
        response, _ = self.generate(prompt, t = 0.)
        predicted_outdated = response.split("[")[-1].split("]")[0].split(";")
        predicted_outdated = [pair.strip().split("<-")[1].strip(''' '".,''') for pair in predicted_outdated if "<-" in pair]
        self.delete_thesises(predicted_outdated)
        self.add(new_thesises_raw, observation)
        log("Outdated thesises: " + str(predicted_outdated))
        log("Original replacement: " + str(response))

        # Legacy navigation part
        if "go to" not in action:
            if curr_location != previous_location:
                new_triplets_raw = [[curr_location, previous_location, {"label": find_direction(action)}], 
                                    [previous_location, curr_location, {"label": find_opposite_direction(action)}]]
                self.add_triplets(new_triplets_raw)

        # Semantic extraction
        associated_subgraph = set()
        for query, depth in items1.items():
            results = graph_retr_search_thesises(
                query.lower(), self.thesises, self.entities,
                self.retriever,
                max_depth=depth,  
                topk=5,
                post_retrieve_threshold=0.75, 
                verbose=2
            )
            associated_subgraph.update(results)

        associated_subgraph = [element for element in associated_subgraph if element not in only_names]

        # Episodic extraction
        obs_plan_embeddings = self.retriever.embed((plan))
        top_episodic = self.sort_episodic(only_names, obs_plan_embeddings)
        top_episodic = [episodic for episodic in top_episodic if episodic not in history + [observation]][:topk_episodic]
        
        return associated_subgraph, top_episodic
    
    def sort_episodic(self, thesises_names, work_emb):
        results = {}
        if not self.events:
            return results
        # List of all embeddings from the dictionary B
        key_embeddings = torch.cat([torch.tensor(event.embedding).view(1, -1) for event in self.events.values()])


        # Get the similarity scores using the provided retriever
        similarity_results = self.retriever.search_in_embeds(
            key_embeds=key_embeddings,
            query_embeds=work_emb,
            topk=len(self.events),  # Get scores for all entries
            return_scores=True
        )

        similarity_results = sort_scores(similarity_results)
        
        # Extract the first (and only) list of scores from the nested list structure
        if similarity_results['scores']:
            similarity_scores = similarity_results['scores'][0]
        else:
            similarity_scores = [0] * len(self.events)  # Default to zero scores if nothing is returned

        # Normalize similarity scores
        max_similarity_score = max(similarity_scores, default=0).item() if similarity_scores else 0
        similarity_scores = [score.item() / max_similarity_score if max_similarity_score else 0 for score in similarity_scores]

        # Calculate and normalize match counts
        match_counts = [sum(1 for element in thesises_names if hash(element) in event.children) for event in self.events.values()]
        
        match_counts_relative = []
        for i, event in enumerate(self.events.values()):
            match_counts_relative.append((match_counts[i]/(len(event.children) + 1e-9))*np.log((len(event.children) + 1e-9)))
        
        max_match_count = max(match_counts_relative, default=0)
        normalized_match_scores = [count / max_match_count if max_match_count else 0 for count in match_counts_relative]
        scores = [normalized_match_scores[i] + similarity_scores[i] for i in range(len(similarity_scores))]
        ids = np.argsort(scores)
        return np.array([event.name for event in self.events.values()])[ids]
        

                
    