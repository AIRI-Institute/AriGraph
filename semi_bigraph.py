import os
import json
import numpy as np
from copy import deepcopy
from scipy.spatial.distance import cosine, euclidean

class KnowledgeSemiBiGraph:
    def __init__(self, path, load = False, embedding_treshold = 0.02, state_embeddin_treshold = 0.02, steps_between_tryings = 250):
        os.makedirs(path, exist_ok=True)
        self.path, self.embedding_treshold, self.state_embeddin_treshold = path, embedding_treshold, state_embeddin_treshold
        self.items, self.steps_between_tryings = {}, steps_between_tryings
        self.states = {
            "Start graph": {
                "observation": "Start graph",
                "location": "Cosmic space",
                "trying": -1,
                "step": -1,
                "n": 10000000000000,
                "explored_states": [],
                "inventory": [],
                "appearances": {},
                "memorizings": {},
                "embedding": [0] * 767 + [0.001],
                "visits": [],
                "n_extracting": 0
            }
        }
        self.metainf = {
            "last_state": "Start graph",
            "max_extractions": 1
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
                "memorizing_associations": [],
                "factological_associations_items": {},
                "memorizing_associations_items": {},
                "n_obs": 1,
                "n_mem": 1,
                "n_extr": 0
            }
            self.items[name] = item  
        return item      

    def add_state(self, observation, action, action_embedding,
                location, trying, step, embedding):
        state_key = f'''
Observation: {observation}
Location: {location}
'''     
        state_key = self.get_state_key(state_key, embedding)
        if state_key is not None:
            self.states[state_key]["visits"].append((trying, step))
            self.states[state_key]["n"] += 1
            self.states[state_key]["trying"] = trying
            self.states[state_key]["step"] = step
            self.states[state_key]["inventory"] = "Nothing there"
        else:
            state_key = f'''
Observation: {observation}
Location: {location}
'''
            self.states[state_key] = {
                "observation": observation,
                "location": location,
                "trying": trying,
                # "inventory": inventory, 
                "step": step,
                "n": 1,
                "embedding": embedding,
                "visits": [(trying, step)],
                "explored_states": [],
                "appearances": {},
                "memorizings": {},
                "n_extracting": 0
            }
        consequence = f'''
Observation: {observation}
Location: {location}
'''
        added_action = self.add_item(action, action_embedding)["name"]
        self.items[added_action]["factological_associations"].append(state_key)
        if added_action in self.states[state_key]["appearances"]:
            self.states[state_key]["appearances"][added_action] += 1
        else:
            self.states[state_key]["appearances"][added_action] = 1
        self.states[self.metainf["last_state"]]["explored_states"].append((added_action, consequence, trying, step, state_key))
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
            score = euclidean(self.items[candidate]["embedding"], embedding)
            if score < self.embedding_treshold and score < best_score:
                best_score = score
                item = self.items[candidate]
        return item
    
    def get_state_key(self, state_key, embedding):
        if state_key in self.states:
            return state_key
        true_key, best_score = None, 10
        for candidate in self.states:
            score = euclidean(self.states[candidate]["embedding"], embedding)
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
        names = []
        state_key = self.get_state_key(state_key, embedding)
        
        for item in items:
            name = list(item.keys())[0]
            embedding = item[name]
            new_item = self.add_item(name, embedding)
            name = new_item["name"]
            names.append(name)
            self.items[name]["n_obs"] += 1
            self.items[name]["factological_associations"].append(state_key)
            if name in self.states[state_key]["appearances"]:
                self.states[state_key]["appearances"][name] += 1
            else:
                self.states[state_key]["appearances"][name] = 1
        for name_1 in names:
            for name_2 in names:
                if name_1 == name_2:
                    continue
                if name_2 in self.items[name_1]["factological_associations_items"]:
                    self.items[name_1]["factological_associations_items"][name_2] += 1
                else:
                    self.items[name_1]["factological_associations_items"][name_2] = 1
        return names

    def remember_items(self, items,
                observation, location, embedding):
        state_key = f'''
Observation: {observation}
Location: {location}
'''     
        state_key = self.get_state_key(state_key, embedding)
        names = []
        for item in items:
            name = list(item.keys())[0]
            embedding = item[name]
            if self.get_item(name, embedding) is not None:
                name = self.get_item(name, embedding)["name"]
                names.append(name)
                self.items[name]["n_mem"] += 1
                self.items[name]["memorizing_associations"].append(state_key)
                if name in self.states[state_key]["memorizings"]:
                    self.states[state_key]["memorizings"][name] += 1
                else:
                    self.states[state_key]["memorizings"][name] = 1
        for name_1 in names:
            for name_2 in names:
                if name_1 == name_2:
                    continue
                if name_2 in self.items[name_1]["memorizing_associations_items"]:
                    self.items[name_1]["memorizing_associations_items"][name_2] += 1
                else:
                    self.items[name_1]["memorizing_associations_items"][name_2] = 1

    def save(self):
        with open(self.path + "/items.json", "w") as file:
            json.dump(self.items, file)
        with open(self.path + "/states.json", "w") as file:
            json.dump(self.states, file)
        with open(self.path + "/metainf.json", "w") as file:
            json.dump(self.metainf, file)

    def get_associations(self, remembered_items = [], state_key = None):
        if state_key is None:
            state_key = self.metainf["last_state"]
        if len(remembered_items) == 0:
            remembered_items = list(self.states[state_key]["memorizings"].keys())
        n = self.states[state_key]["n"]
        experienced_actions = self.get_experienced_actions(state_key)
        associations = {}
        for item in remembered_items:
            name = item
            for associated_key in self.items[name]["factological_associations"]:
                relatedness_score = self.states[state_key]["memorizings"][name] * self.states[associated_key]["appearances"][name] \
                        / (self.states[associated_key]["n"] * self.states[state_key]["n"])
                time_diff = (self.states[associated_key]["trying"] * self.steps_between_tryings + self.states[associated_key]["step"]\
                    - self.states[state_key]["trying"] * self.steps_between_tryings - self.states[state_key]["step"]) / 5
                time_score = np.exp(time_diff)
                priming_score = self.states[associated_key]["n_extracting"] / self.metainf["max_extractions"]
                if associated_key not in associations:
                    associations[associated_key] = [
                        relatedness_score + time_score + priming_score,
                        [name]
                    ]
                else:
                    associations[associated_key][0] += relatedness_score + time_score + priming_score
                    associations[associated_key][1].append(name)
        associations = [(value[0], value[1], key) for key, value in associations.items()]
        associations.sort()
        associations = associations[:2]
        associations_obs = [self.get_string_state(key) for (value, items, key) in associations]
        for i in range(len(associations_obs)):
            associations_obs[i] += f'''
This situation was associated with following things: {associations[i][1]}
'''
            self.states[associations[i][2]]["n_extracting"] += 1
            self.metainf["max_extractions"] = max(self.metainf["max_extractions"], self.states[associations[i][2]]["n_extracting"])
        return associations_obs, experienced_actions, n  
    
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
        experienced_actions = []
        for action in actions:
            for candidate in reversed(self.states[state_key]["explored_states"]):
                if candidate[0] == action[1]:
                    experienced_actions.append(f'''
action: {action[1]}
    consequence: {candidate[1]}
    trying: {candidate[2]}
    step: {candidate[3]}

''')
                    break
        return experienced_actions
    
    def get_string_state(self, state_key):
        if state_key == "last":
            state_key = self.metainf["last_state"]
        state = self.states[state_key]
        desc = f"Observation: {state['observation']}, Location: {state['location']},\
Trying: {state['trying']}, Step: {state['step']}, Number of visiting: {state['n']}"
        return desc
    
    def get_next_step(self, action_, current_state, action_embedding, visited_states):
        action = self.get_item(action_, action_embedding)
        if action is None:
            return "Unknown", True, action_
        action = action["name"]
        state = self.states[current_state]
        explored_actions = {act[0] for act in state["explored_states"]}
        if action not in explored_actions:
            return "Unknown", True, action_
        for act in reversed(state["explored_states"]):
            if act[0] == action:
                next_state = act[4]
                break
        return next_state, False, action

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
    
    def get_last_state(self):
        return self.metainf["last_state"]