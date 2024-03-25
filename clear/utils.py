import numpy as np
from copy import deepcopy

from prompts import system_prompt, exploration_system_prompt

def process_triplets(raw_triplets):
    raw_triplets = raw_triplets.split(";")
    triplets = []
    for triplet in raw_triplets:
        if len(triplet.split(",")) > 3:
            continue
        elif len(triplet.split(",")) < 3:
            continue
        else:
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
    text = text.split("[[")[-1]
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
    plan = plan.split("Plan:")[-1].strip(" \n[]")
    plan = plan.split(",")
    return [action.strip('''\n'" ''') for action in plan]

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
        
    def __call__(self, text):
        print(text)
        with open(self.path, "a") as file:
            file.write(text + "\n")
        
def remove_equals(graph):
    graph_copy = deepcopy(graph)
    for triplet in graph_copy:
        if graph.count(triplet) > 1:
            graph.remove(triplet)
    return graph 