import json
import numpy as np
from sklearn.utils import shuffle

from parent_graph import TripletGraph
from prompts import *
from prompts_v2 import *

class History(TripletGraph):
    def __init__(self, model, system_prompt, majority_part = 0.51):
        super().__init__(model, system_prompt)
        self.states, self.metastates = [], []
        self.majority_part = majority_part
        
    def save(self, path):
        with open(path + "/STATES_HISTORY.json", "w") as file:
            json.dump(self.states, file)
        with open(path + "/METASTATES_HISTORY.json", "w") as file:
            json.dump(self.metastates, file)
        metainf = {"model": self.model, "threshold": self.threshold, "system_prompt": self.system_prompt}
        with open(path + "/METAINF_HISTORY.json", "w") as file:
            json.dump(metainf, file)
            
    def load(self, path):
        with open(path + "/STATES_HISTORY.json", "r") as file:
            self.states = json.load(file)
        with open(path + "/METASTATES_HISTORY.json", "r") as file:
            self.metastates = json.load(file)
        with open(path + "/METAINF_HISTORY.json", "r") as file:
            metainf = json.load(file)
            self.model, self.threshold, self.system_prompt = metainf["model"], metainf["threshold"], metainf["system_prompt"]
        
        
    def add_state(self, state, attempt, step, action, location):
        self.states.append({
            "obs": state,
            "attempt": attempt,
            "step": step,
            "action": action.lower(),
            "location": location.lower(),
        })
        
    def add_metastate(self, metastate, attempt, step, actions, locations):
        if metastate is not None:              
            action = "NOT_DETERMINED"
            if actions:
                unique_acts, counts = np.unique(actions, return_counts = True)
                if max(counts) / len(actions) >= self.majority_part:
                    action = unique_acts[np.argmax(counts)]
                
            location = "NOT_DETERMINED"
            if locations:
                unique_locs, counts = np.unique(locations, return_counts = True)
                if max(counts) / len(locations) >= self.majority_part:
                    location = unique_locs[np.argmax(counts)]
                
            self.metastates.append({
                "obs": metastate,
                "attempt": attempt,
                "step": step,
                "action": action.lower(),
                "location": location.lower()
            })
    
    def n_last(self, n):
        chosen = self.states[-n:]
        actions = [state["action"] for state in chosen]
        locations = [state["location"] for state in chosen]
        chosen = [state["obs"] for state in chosen]
        return chosen, actions, locations
    
    def n_by_action(self, action, n):
        action = action.lower().split()[0]
        candidates = [state for state in self.states + self.metastates if state["action"].split()[0] == action]
        chosen = shuffle(candidates)[-n:]
        actions = [state["action"] for state in chosen]
        locations = [state["location"] for state in chosen]
        chosen = [state["obs"] for state in chosen]
        return chosen, actions, locations
    
    def n_by_location(self, location, n):
        location = location.lower()
        candidates = [state for state in self.states + self.metastates if state["location"] == location]
        chosen = shuffle(candidates)[-n:]
        actions = [state["action"] for state in chosen]
        locations = [state["location"] for state in chosen]
        chosen = [state["obs"] for state in chosen]
        return chosen, actions, locations
    
    def summary(self, obss, instruction = None):
        summary = None
        if len(obss) > 2:
            prompt = prompt_summary
            if instruction is not None:
                prompt += f"\nSPECIAL INSTRUCTIONS: {instruction}\n"
            prompt += prompt_summary_obs.format(observations = obss)
            summary, cost = self.generate(prompt)
        return summary
    
        