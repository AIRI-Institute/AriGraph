import os
import json
import numpy as np
from inspect import signature
from copy import deepcopy

from prompts import system_prompt, exploration_system_prompt

def find_args(callable, args):
    needful_arg_signature = signature(callable).parameters
    needful_args = list(needful_arg_signature.keys())
    args_for_return = {}
    for arg in needful_args:
        if arg == "self":
            continue
        if arg not in args and "=" not in str(needful_arg_signature[arg]):
            raise "Haven't needful argument"
        elif arg not in args:
            continue
        args_for_return[arg] = args[arg]
    return args_for_return

def process_triplets(raw_triplets):
    raw_triplets = raw_triplets.split(";")
    triplets = []
    for triplet in raw_triplets:
        if len(triplet.split(",")) != 3:
            continue
        if triplet[0] in "123456789":
            triplet = triplet[2:]
        subj, relation, obj = triplet.split(",")
        subj, relation, obj = subj.strip(' \n"'), relation.strip(' \n"'), obj.strip(' \n"')
        if len(subj) == 0 or len(relation) == 0 or len(obj) == 0:
            continue
        triplets.append([subj, obj, {"label": relation}])
        
    return triplets

def find_direction(action):
    if "north" in action:
        return "north of"
    if "east" in action:
        return "east of"
    if "south" in action:
        return "south of"
    if "west" in action:
        return "west of"
    raise "ACTION ISN'T A DIRECTION"

def parse_triplets_removing(text):
    text = text.split("[[")[-1] if "[[" in text else text.split("[\n[")[-1]
    text = text.replace("[", "")
    text = text.strip("]")
    pairs = text.split("],")
    parsed_triplets = []
    for pair in pairs:
        splitted_pair = pair.split("->")
        if len(splitted_pair) != 2:
            continue
        first_triplet = splitted_pair[0].split(",")
        if len(first_triplet) != 3:
            continue
        subj, rel, obj = first_triplet[0].strip(''' '"\n'''), first_triplet[1].strip(''' '"\n'''), first_triplet[2].strip(''' '"\n''')
        parsed_triplets.append([subj, obj, {"label": rel}])
    return parsed_triplets

def parse_plan(plan):
    plan = plan.split("[")[-1].split("]")[0]
    plan = plan.split(",")
    return [action.strip('''\n'" ''') for action in plan]

def process_crucial_items(response):
    observed_items = []
    if "Crucial things: " in response:
        observed_items = response.split("Crucial things: ")[1].split(";")[0].strip("[]").split(",")
        for i in range(len(observed_items)):
            observed_items[i] = observed_items[i].strip(''' \n.'"''')
    
    return observed_items

class Switch:
    def __init__(self, n_min, n_max):
        self.scores, self.exploitation, self.explor_steps, self.exploit_steps = [], False, 0, 0
        self.n_min, self.n_max = n_min, n_max
        
    def __call__(self, agent, curr_score):
        self.scores.append(curr_score)
        if self.criterium:
            agent.system_prompt = system_prompt
            self.exploitation = True
        elif self.exploitation and self.exploit_steps >= self.explor_steps:
            agent.system_prompt = exploration_system_prompt
            self.scores, self.exploitation, self.explor_steps, self.exploit_steps = [], False, 0, 0
        if self.exploitation:
            self.exploit_steps += 1
        else:
            self.explor_steps += 1
        
    @property    
    def criterium(self):
        if len(self.scores) > self.n_max:
            return True
        i, r = self.scores.index(max(self.scores)), len(self.scores) - 1
        l = max(0, 2*i - r)
        if len(self.scores[i + 1:]) < self.n_min:
            return False
        
        summ, weighted_summ = np.sum(self.scores[l:]), 0
        dist = r - i
        for j in range(l, r + 1):
            weighted_summ += self.scores[j] * (j - i + dist) / dist    
        return summ > weighted_summ

class Logger:
    def __init__(self, path):
        self.path = path
        os.makedirs(path, exist_ok=True)
        
    def __call__(self, text, filename = "log.txt"):
        print(text)
        with open(self.path + "/" + filename, "a") as file:
            file.write(text + "\n")
            
    def to_json(self, obj, filename = "history.json"):
        try:
            with open(self.path + "/" + filename, "w") as file:
                json.dump(obj, file)
        except:
            raise "Object isn't json serializible"
        
def remove_equals(graph):
    graph_copy = deepcopy(graph)
    for triplet in graph_copy:
        if graph.count(triplet) > 1:
            graph.remove(triplet)
    return graph 

def proceed_navigation(action, graph, env, locations, log):
    destination = action.split("go to")[-1].strip('''\n'" ''').lower()
    path = graph.find_path(env.curr_location.lower(), destination, locations)
    if not isinstance(path, list):
        observation, reward, done, info = path, 0, False, env.curr_info
    else:
        log("\n\nNAVIGATION\n\n")
        for hidden_step, hidden_action in enumerate(path):
            observation, reward, done, info = env.step(hidden_action)
            if curr_loc != env.curr_location.lower():
                if env.curr_location.lower() not in locations:
                    new_triplets_raw = [(env.curr_location.lower(), curr_loc, {"label": hidden_action + "_of"})]
                    graph.add_triplets(new_triplets_raw)
                    locations.add(env.curr_location.lower())
                curr_loc = env.curr_location.lower()
            if done:
                break
            log("Navigation step: " + str(hidden_step + 1))
            log("Observation: " + observation + "\n\n")
    return observation, reward, done, info

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
    return (triplet[0].lower(), triplet[1].lower(), {"label": triplet[2]["label"].lower()})

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
            
def check_equals(lists, threshold = 0.5):
    if not lists:
        return lists
    new_lists, total_obs = [lists[0]], set(lists[0])
    for candidate in lists[1:]:
        if len(set(candidate) & total_obs) / (len(candidate) + 1e-9) > threshold:
            new_lists.append([])
        else:
            new_lists.append(candidate)
            total_obs = total_obs | set(candidate)
    return new_lists