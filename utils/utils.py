import os
import re
import ast
import json
import torch
import numpy as np
from copy import deepcopy
from inspect import signature
import matplotlib.pyplot as plt


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
        subj, relation, obj = subj.split(":")[-1].strip(''' '\n"'''), relation.strip(''' '\n"'''), obj.strip(''' '\n"''')
        if len(subj) == 0 or len(relation) == 0 or len(obj) == 0:
            continue
        triplets.append([subj, obj, {"label": relation}])
        
    return triplets

def process_candidates(raw_triplets):
    raw_triplets = raw_triplets.strip("[] \n.")
    raw_triplets = raw_triplets.split(";")
    triplets = []
    for triplet in raw_triplets:
        if len(triplet.split(",")) != 3:
            continue
        subj, relation, obj = triplet.split(",")
        # step = subj.strip(''' '1234567890.\n"''').replace("Step", "")
        # step = int(step.split(":")[0].strip(' .\n"'))
        # subj = subj.split(":")[-1]
        subj, relation, obj = subj.strip(''' '.\n"'''), relation.strip(' .\n"'), obj.strip(''' '\n."''')
        if len(subj) == 0 or len(relation) == 0 or len(obj) == 0:
            continue
        # triplets.append([subj, obj, {"label": relation, "step": step}])
        triplets.append([subj, obj, {"label": relation}])
        
    return triplets

def find_direction(action):
    if "north" in action:
        return "is north of"
    if "east" in action:
        return "is east of"
    if "south" in action:
        return "is south of"
    if "west" in action:
        return "is west of"
    return "can be achieved from"

def find_opposite_direction(action):
    if "north" in action:
        return "is south of"
    if "east" in action:
        return "is west of"
    if "south" in action:
        return "is north of"
    if "west" in action:
        return "is east of"
    return "can be achieved from"

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


def process_crucial_items(response):
    observed_items = []
    if "Crucial things: " in response:
        observed_items = response.split("Crucial things: ")[1].split(";")[0].strip("[]").split(",")
        for i in range(len(observed_items)):
            observed_items[i] = observed_items[i].strip(''' \n.'"''')
    
    return observed_items


class Logger:
    def __init__(self, path):
        self.path = path
        os.makedirs(path, exist_ok=True)
        
    def __call__(self, text, filename = "log.txt", verbose = True):
        if verbose:
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
    return [triplet[0].lower().strip('''"'. `;:'''), triplet[1].lower().strip('''"'. `;:'''), {"label": triplet[2]["label"].lower().strip('''"'. `;:''')}]

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



def tupleize_state(state):
    """
    Convert state list with dictionaries to a tuple form that can be used in sets.
    """
    return set((item, location, tuple(sorted(properties.items()))) for item, location, properties in state)

def find_changes(prev_state, current_state):
    """
    Identifies items that have been taken or placed by comparing the previous and current states.
    """
    prev_set = tupleize_state(prev_state)
    current_set = tupleize_state(current_state)
    
    env_change = current_set - prev_set
    env_backward = prev_set - current_set
    
    # Convert tuples back to original form (item, location, properties dict)
    env_change = [(item, loc, dict(props)) for item, loc, props in env_change]
    env_backward = [(item, loc, dict(props)) for item, loc, props in env_backward]
    
    return env_change, env_backward

def get_reward_for_changes(env_change, env_backward, win_cond_take, win_cond_place):
    step_reward = 0
    # Check if taken items were correct
    skip_actions = ['examine', 'open', 'close', 'look', 'inventory']
    if env_change !=[]:
        if (env_change[0][1] == "I" and env_backward[0] not in win_cond_place) or (env_change[0] in win_cond_place):
            step_reward += 1
        elif env_change[0][0] == "P" or [s for s in skip_actions if s in env_change[0][2]['label']]:
            step_reward = step_reward 
        else:
            step_reward -= 1

    return step_reward

def simulate_environment_actions(prev_state, current_state, win_cond_take, win_cond_place):
    env_change, env_backward = find_changes(prev_state, current_state)
    step_reward = get_reward_for_changes(env_change, env_backward, win_cond_take, win_cond_place)
    return step_reward


def observation_processing(text):
    pattern = r">.*$"
    cleaned_text = re.sub(pattern, "", text, flags=re.DOTALL)
    if 'livingroom' in cleaned_text:
        cleaned_text = cleaned_text.replace("livingroom", "living room")
    if 'Livingroom' in cleaned_text:
        cleaned_text = cleaned_text.replace("Livingroom", "Living room")   
    if 'Recipe #1' in cleaned_text:
        cleaned_text = cleaned_text.replace("Recipe #1", "Recipe") 

    return cleaned_text

def find_top_episodic_emb(A, B, obs_plan_embedding, retriever):
    results = {}
    if not B:
        return results
    # List of all embeddings from the dictionary B
    key_embeddings = torch.cat([value[1] for value in B.values()])


    # Get the similarity scores using the provided retriever
    similarity_results = retriever.search_in_embeds(
        key_embeds=key_embeddings,
        query_embeds=obs_plan_embedding,
        topk=len(B),  # Get scores for all entries
        return_scores=True
    )

    similarity_results = sort_scores(similarity_results)
    
    # Total elements in A to normalize match scores
    total_elements = len(A)
    
    # Extract the first (and only) list of scores from the nested list structure
    if similarity_results['scores']:
        similarity_scores = similarity_results['scores'][0]
    else:
        similarity_scores = [0] * len(B)  # Default to zero scores if nothing is returned

    # Normalize similarity scores
    max_similarity_score = max(similarity_scores, default=0).item() if similarity_scores else 0
    similarity_scores = [score.item() / max_similarity_score if max_similarity_score else 0 for score in similarity_scores]

    # Calculate and normalize match counts
    match_counts = [sum(1 for element in A if element in value_list) for _, (value_list, _) in B.items()]
    
    match_counts_relative = []
    for i, values in enumerate(B.values()):
        match_counts_relative.append((match_counts[i]/(len(values[0]) + 1e-9))*np.log((len(values[0]) + 1e-9)))
    
    max_match_count = max(match_counts_relative, default=0)
    normalized_match_scores = [count / max_match_count if max_match_count else 0 for count in match_counts_relative]

    # Store in results dictionary, combining normalized scores
    for idx, (key, _) in enumerate(B.items()):
        results[key] = [normalized_match_scores[idx], similarity_scores[idx]]

    return results

def top_k_obs(input_dict, k):
    # Sum values in each key's list
    sum_dict = {key: sum(values) for key, values in input_dict.items()}
    
    # Sort the dictionary by the sum of the values in descending order
    sorted_keys = sorted(sum_dict, key=sum_dict.get, reverse=True)
    
    # Return the top k keys
    return sorted_keys[:k]

def sort_scores(data):
    sorted_data = {}
    for idx_list, score_list in zip(data['idx'], data['scores']):
        # Pair indices with scores and sort by index
        paired_sorted = sorted(zip(idx_list, score_list), key=lambda x: x[0])
        # Unzip the pairs
        _, sorted_scores = zip(*paired_sorted)
        # Assign sorted values back to the dictionary
        sorted_data['idx'] = [idx_list]
        sorted_data['scores'] = [list(sorted_scores)]
    return sorted_data

def find_unexplored_exits(location, triplets):
    exits = set()  # To store exits from the given location
    explored_directions = set()  # To store directions that are explored

    # First pass: Identify all exits from the location
    for triplet in triplets:
        elements = triplet.split(', ')
        if elements[0] == location and 'has exit' in elements[1]:
            exits.add(elements[2])  # Add the direction of the exit 
        elif elements[0] == location and any(x in elements[1] for x in ['exit', 'lead', 'entr', 'path']) and any(x in elements[1] for x in ['north', 'south', 'east', 'west']):
            if 'north' in elements[1]:
                exits.add('north')
            if 'south' in elements[1]:
                exits.add('south')
            if 'east' in elements[1]:
                exits.add('east')
            if 'west' in elements[1]:
                exits.add('west')        
        elif elements[0] == location and any(x in elements[1] for x in ['exit', 'lead', 'entr', 'path']) and any(x in elements[2] for x in ['north', 'south', 'east', 'west']):
            if 'north' in elements[2]:
                exits.add('north')
            if 'south' in elements[2]:
                exits.add('south')
            if 'east' in elements[2]:
                exits.add('east')
            if 'west' in elements[2]:
                exits.add('west')      

    # Second pass: Identify which exits are explored
    for triplet in triplets:
        elements = triplet.split(', ')
        if elements[2] == location:
            if len(elements[1].split(' ')) < 2:
                continue
            direction = elements[1].split(' ')[1]  # Get the direction part
            if direction in exits:
                explored_directions.add(direction)  # Mark this exit as explored

    # Find unexplored exits by checking which exits are not in the explored directions
    unexplored_exits = exits - explored_directions
    output = list(unexplored_exits)
    if unexplored_exits == set():
        output = 'none'  
    return output

def action_processing(action):
    if "cook" in action and "stove" in action:
        action = action.replace("cook", "fry")
    if "cook" in action and "oven" in action:
        action = action.replace("cook", "roast")
    if "cook" in action and "BBQ" in action:
        action = action.replace("cook", "grill")
    return action

def action_deprocessing(action):
    if "fry" in action:
        action = action.replace("fry", "cook")
    if "roast" in action:
        action = action.replace("roast", "cook")
    if "grill" in action:
        action = action.replace("grill", "cook") 
    return action

def process_thesises(response):
    raw_thesises = response.split(".")
    thesises = []
    for raw_thesis in raw_thesises:
        if ";" not in raw_thesis:
            continue
        raw_thesis = raw_thesis.split(";")
        thesises.append({"name": raw_thesis[0], "entities": ast.literal_eval(raw_thesis[1].strip(''' .,/'''))})
    return thesises

def find_unexplored_exits_thesises(location, triplets, thesises):
    exits = set()  # To store exits from the given location
    explored_directions = set()  # To store directions that are explored

    # First pass: Identify all exits from the location
    for thesis in thesises:
        if any(x in thesis for x in ['exit', 'lead', 'entr', 'path']) and location in thesis:
            if 'north' in thesis:
                exits.add('north')
            if 'south' in thesis:
                exits.add('south')
            if 'east' in thesis:
                exits.add('east')
            if 'west' in thesis:
                exits.add('west')  

    # Second pass: Identify which exits are explored
    for triplet in triplets:
        elements = triplet.split(', ')
        if elements[2] == location:
            if len(elements[1].split(' ')) < 2:
                continue
            direction = elements[1].split(' ')[1]  # Get the direction part
            if direction in exits:
                explored_directions.add(direction)  # Mark this exit as explored

    # Find unexplored exits by checking which exits are not in the explored directions
    unexplored_exits = exits - explored_directions
    output = list(unexplored_exits)
    if unexplored_exits == set():
        output = 'none'  
    return output