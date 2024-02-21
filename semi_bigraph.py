import os
import json
import numpy as np
from copy import deepcopy
from scipy.spatial.distance import cosine

class KnowledgeSemiBiGraph:
    def __init__(self, path, load = False, embedding_treshold = 0.05, state_embeddin_treshold = 0.05):
        os.makedirs(path, exist_ok=True)
        self.path, self.embedding_treshold, self.state_embeddin_treshold = path, embedding_treshold, state_embeddin_treshold
        self.items = {}
        self.states = {
            "Start graph": {
                "observation": "Start graph",
                "location": "Cosmic space",
                "trying": -1,
                "step": -1,
                "n": -1,
                "explored_states": [],
                "inventory": [],
                "appearances": {},
                "memorizings": {},
                "embedding": [0] * 768
            }
        }
        self.metainf = {
            "last_state": "Start graph"
        }
        if load:
            with open(path + "/states.json", "r") as file:
                self.states = json.load(file)
            with open(path + "/items.json", "r") as file:
                self.items = json.load(file)
            with open(path + "/metainf.json", "r") as file:
                self.metainf = json.load(file)
    
    def add_item(self, name, embedding):
        item = self.get_item(name, embedding)
        if item is None:
            item = {
                "name": name,
                "embedding": embedding,
                "factological_associations": [],
                "memorizing_associations": []
            }
            self.items[name] = item  
        return item      

    def add_state(self, observation, action,
                location, trying, step, inventory, embedding):
        state_key = f'''
Observation: {observation}
Location: {location}
'''     
        state_key = self.get_state_key(state_key, embedding)
        if state_key is not None:
            self.states[state_key]["visits"].append((trying, step, inventory))
            self.states[state_key]["n"] += 1
            self.states[state_key]["trying"] = trying
            self.states[state_key]["step"] = step
            self.states[state_key]["inventory"] = inventory
        else:
            state_key = f'''
Observation: {observation}
Location: {location}
'''
            self.states[state_key] = {
                "observation": observation,
                "location": location,
                "trying": trying,
                "inventory": inventory, 
                "step": step,
                "n": 1,
                "embedding": embedding,
                "visits": [(trying, step, inventory)],
                "explored_states": [],
                "appearances": {},
                "memorizings": {}
            }
        self.states[self.metainf["last_state"]]["explored_states"].append((action, state_key, trying, step))
        self.metainf["last_state"] = state_key

    def add_insight(self, insight, observation, location, embedding):
        state_key = f'''
Observation: {observation}
Location: {location}
'''    
        state_key = self.get_state_key(state_key, embedding)
        assert state_key in self.states
        if "insights" not in self.states[state_key]:
            self.states[state_key]["insights"] = [insight]
        else:
            self.states[state_key]["insights"].append(insight)

    def get_item(self, name, embedding):
        if name in self.items:
            return self.items[name]
        item, best_score = None, 10
        for candidate in self.items:
            score = cosine(self.items[candidate]["embedding"], embedding)
            if score < self.embedding_treshold and score < best_score:
                best_score = score
                item = self.items[candidate]
        return item
    
    def get_state_key(self, state_key, embedding):
        if state_key in self.states:
            return state_key
        true_key, best_score = None, 10
        for candidate in self.states:
            score = cosine(self.states[candidate]["embedding"], embedding)
            if score < self.state_embeddin_treshold and score < best_score:
                best_score = score
                true_key = candidate
        return true_key

    def observe_items(self, items,
                observation, location, embedding):
        state_key = f'''
Observation: {observation}
Location: {location}
'''     
        state_key = self.get_state_key(state_key, embedding)
        for item in items:
            name = list(item.keys())[0]
            embedding = item[name]
            new_item = self.add_item(name, embedding)
            name = new_item["name"]
            self.items[name]["factological_associations"].append(state_key)
            if name in self.states[state_key]["appearances"]:
                self.states[state_key]["appearances"][name] += 1
            else:
                self.states[state_key]["appearances"][name] = 1

    def remember_items(self, items,
                observation, location, embedding):
        state_key = f'''
Observation: {observation}
Location: {location}
'''     
        state_key = self.get_state_key(state_key, embedding)
        for item in items:
            name = list(item.keys())[0]
            embedding = item[name]
            if self.get_item(name, embedding) is not None:
                name = self.get_item(name, embedding)["name"]
                self.items[name]["memorizing_associations"].append(state_key)
                if name in self.states[state_key]["memorizings"]:
                    self.states[state_key]["memorizings"][name] += 1
                else:
                    self.states[state_key]["memorizings"][name] = 1

    def save(self):
        with open(self.path + "/items.json", "w") as file:
            json.dump(self.items, file)
        with open(self.path + "/states.json", "w") as file:
            json.dump(self.states, file)
        with open(self.path + "/metainf.json", "w") as file:
            json.dump(self.metainf, file)

    def get_associations(self, remembered_items):
        state_key = self.metainf["last_state"]
        n = self.states[state_key]["n"]
        experienced_actions = self.get_experienced_actions(state_key)
        associations = {}
        for item in remembered_items:
            name = item
            for associated_key in self.items[name]["factological_associations"]:
                if associated_key not in associations:
                    associations[associated_key] = self.states[state_key]["memorizings"][name] * self.states[associated_key]["appearances"][name] \
                    / (self.states[associated_key]["n"] * self.states[state_key]["n"])
                else:
                    associations[associated_key] += self.states[state_key]["memorizings"][name] * self.states[associated_key]["appearances"][name] \
                    / (self.states[associated_key]["n"] * self.states[state_key]["n"])
        associations = [(value, key) for key, value in associations.items()]
        associations.sort()
        associations = associations[:1]
        associations = [self.get_string_state(key) for (value, key) in associations]
        return associations, experienced_actions, n  
    
    def get_experienced_actions(self, state_key):
        actions = {}
        for action in self.states[state_key]["explored_states"]:
            if action[0] in actions:
                actions[action[0]] += 1
            else:
                actions[action[0]] = 1
        actions = [(value, key) for key, value in actions.items()]
        actions.sort()
        actions = actions[:3]
        experienced_actions = ""
        for action in actions:
            for candidate in reversed(self.states[state_key]["explored_states"]):
                if candidate[0] == action[1]:
                    experienced_actions += f'''
    action: {action[1]}
    consequence: {candidate[1]}
    trying: {candidate[2]}
    step: {candidate[3]}

'''
                    break
        return experienced_actions
    
    def get_string_state(self, state_key):
        if state_key == "last":
            state_key = self.metainf["last_state"]
        state = self.states[state_key]
        desc = f"Observation: {state['observation']}, Location: {state['location']}, Inventory: {state['inventory']},\
Trying: {state['trying']}, Step: {state['step']}, Number of visiting: {state['n']}"
        return desc

    def find_best_state(self, items):
        scores = {}
        for item in items:
            for state in self.states.values():
                state_key = f'''
Observation: {state["observation"]}
Location: {state["location"]}
'''             
                if "appearances" not in state:
                    print(state)
                if item in state["appearances"]:
                    if state_key in scores:
                        scores[state_key] += state["appearances"][item] / state["n"]
                    else:
                        scores[state_key] = state["appearances"][item] / state["n"]
        
        best_key, best_score = None, -10
        for key, score in scores.items():
            if score > best_score:
                best_score = score
                best_key = key
        return best_key