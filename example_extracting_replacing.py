from InstructorEmbedding import INSTRUCTOR
from scipy.spatial.distance import cosine, euclidean
from jericho import FrotzEnv
import json
import numpy as np
from copy import deepcopy
from tqdm.auto import tqdm

from agent import GPTagent
from textworld_adapter import TextWorldWrapper, graph_from_facts, get_text_graph, draw_graph
from triplet_graph import TripletGraph
from prompts import *   
from utils import *

log_file = "log_example_extracting_replacing.txt"
env_name = "benchmark/clean_3x3/clean_3x3_mess.z8"

log = Logger(log_file)
graph = TripletGraph()
agent = GPTagent(model = "gpt-4-0125-preview", system_prompt=system_prompt)
env = TextWorldWrapper(env_name)
observations = []

# # One for clean 3x3 default
walkthrough = ['take toothbrush', 'go north', 'take dumbbell', 'take dirty plate', 'go east', 'take raw meat', 'go south', 'take school notebooks', 'go south', 'take tv remote', 'take flippers', 'go west', 'take teddy bear', 'put flippers on equipment rack', 'go west', 'take fantasy book', 'put dumbbell on dumbbell stand', 'go north', 'take buisness suit', 'open refrigerator', 'put raw meat in refrigerator', 'close refrigerator', 'open dishwasher', 'put dirty plate in dishwasher', 'close dishwasher', 'go north', 'take sleeping mask', 'take dining chair', 'put toothbrush on bathroom sink', 'go east', 'open toy storage cabinet', 'put teddy bear in toy storage cabinet', 'close toy storage cabinet', 'put school notebooks on study table', 'go east', 'put tv remote on tv table', 'go south', 'open wardrobe', 'put buisness suit in wardrobe', 'close wardrobe', 'put sleeping mask on bedside table', 'go south', 'put fantasy book on bookcase', 'go west', 'go north', 'drop dining chair', 'END']

locations = {"player", "Kids' Room"}
env.reset()
for action in walkthrough:
    locations.add(env.curr_location)
    env.step(action)
print("LOCATIONS: ", locations)

for i in range(1):
    log("Attempt: " + str(i + 1))
    log("\n\n")
    observation, info = env.reset()
    prev_action = "start"
    done = False
    for step, action in enumerate(walkthrough):
        log("Step: " + str(step + 1))
        observation = observation.split("$$$")[-1]
        inventory = env.get_inventory()
        observation += f"\nInventory: {inventory}"
        valid_actions = env.get_valid_actions()
        observation += f"\nValid actions (just recommendation): {valid_actions}"
        observation += f"\nAction that led to this: {prev_action}"
        log("Observation: " + observation)
        
        observed_items, remembered_items = agent.bigraph_processing(observations, observation)
        items = [list(item.keys())[0] for item in observed_items + remembered_items]
        log("Crucial items: " + str(items))
        associated_subgraph = graph.get_associated_triplets(items)

        prompt = prompt_extraction.format(observation = observation, observations = observations[-1:])
        response = agent.generate(prompt)
        new_triplets_raw = process_triplets(response)
        new_triplets = graph.exclude(new_triplets_raw)
        log("New triplets excluded: " + str(new_triplets))
        
        
        prompt = prompt_refining.format(ex_triplets = associated_subgraph, new_triplets = new_triplets)
        response = agent.generate(prompt)
        predicted_outdated = parse_triplets_removing(response)
        log("Outdated triplets: " + response)
        
        graph.delete_triplets(predicted_outdated)
        graph.add_triplets(new_triplets_raw)
        
        n, n_truth, recall = graph.compare(graph_from_facts(info).edges(data = True), exclude_nav = True, locations=locations)
        
        observations.append(observation)
        if done: 
            break
        observation, reward, done, info = env.step(action)
       
        prev_action = action
        if n > 0:
            log("Precision: " + str(recall / n))
        if n_truth > 0:
            log("Recall:" + str(recall / n_truth))
        log("============================")
