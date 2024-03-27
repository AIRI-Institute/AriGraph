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

log_file = "log_example_full_pipeline_nav2.txt"
env_name = "benchmark/navigation2/navigation2.z8"
n_min, n_max = 3, 15

log = Logger(log_file)
graph = TripletGraph()
agent = GPTagent(model = "gpt-4-0125-preview", system_prompt=exploration_system_prompt)
env = TextWorldWrapper(env_name)
switch = Switch(n_min, n_max)

observations = []
locations = set()
n_steps = 60

for i in range(1):
    log("Attempt: " + str(i + 1))
    log("\n\n")
    observation, info = env.reset()
    curr_loc = env.curr_location
    prev_action = "start"
    goal = "Nothing"
    plan = "Nothing"
    n_truth, n, recall = 0, 0, 0
    done = False
    for step in range(n_steps):
        log("Step: " + str(step + 1))
        observation = observation.split("$$$")[-1]
        inventory = env.get_inventory()
        observation += f"\nInventory: {inventory}"
        valid_actions = env.get_valid_actions()
        observation += f"\nValid actions (just recommendation): {valid_actions}"
        observation += f"\nAction that led to this: {prev_action}"
        log("Observation: " + observation)
        
        locations.add(env.curr_location)
        
        # Extracting crucial items
        observed_items, remembered_items = agent.bigraph_processing(observations, observation)
        items = [list(item.keys())[0] for item in observed_items + remembered_items]
        log("Crucial items: " + str(items))
        
         # Extracting triplets
        prompt = prompt_extraction.format(observation = observation, observations = observations[-1:])
        response = agent.generate(prompt)
        new_triplets_raw = process_triplets(response)
        new_triplets = graph.exclude(new_triplets_raw)
        log("New triplets excluded: " + str(new_triplets))
        
        # Using subgraph
        associated_subgraph = graph.get_associated_triplets(items, steps = 2)
        
        #Using full graph
        # associated_subgraph = graph.get_all_triplets()
        
        # Replacing triplets
        prompt = prompt_refining.format(ex_triplets = associated_subgraph, new_triplets = new_triplets)
        response = agent.generate(prompt)
        predicted_outdated = parse_triplets_removing(response)
        log("Outdated triplets: " + response)
        
        # Updating graph
        graph.delete_triplets(predicted_outdated, locations)
        if curr_loc != env.curr_location:
            new_triplets_raw.append((env.curr_location, curr_loc, {"label": find_direction(prev_action)}))
            curr_loc = env.curr_location
        graph.add_triplets(new_triplets_raw)
        
        # Setting system prompt
        switch(agent, 2 * len(new_triplets) - len(predicted_outdated))
        log("Is exploitation: " + str(switch.exploitation))
        
        # Using subgraph
        associated_subgraph = graph.get_associated_triplets(items, steps = 2)
        
        #Using full graph
        # associated_subgraph = graph.get_all_triplets()
        
        log("Associated subgraph: " + str(associated_subgraph))

        # Setting goal
        prompt = prompt_goal.format(observation = observation, observations = observations[-1:], graph = associated_subgraph, goal = goal, plan = plan)
        goal = agent.generate(prompt)
        log("Goal: " + goal)
        log("Current plan: " + str(plan))
        
        # Constructing plan
        prompt = prompt_planning_new.format(observation = observation, observations = observations[-1:], graph = associated_subgraph, goal = goal, plan = plan)
        # prompt = prompt_planning_without_obs.format(graph = associated_subgraph, goal = goal, plan = plan)
        response = agent.generate(prompt)
        plan = parse_plan(response)
        log("Model response: " + response)
        
        # Parse action
        is_nav = False
        if len(plan) == 0:
            action = np.random.choice(valid_actions)
        elif plan[0].startswith("go to"):
            is_nav = True
        else:
            action = plan[0]
        
        observations.append(observation)
        
        # Proceed navigation
        if is_nav:
            destination = plan[0].split("go to")[-1].strip('''\n'" ''')
            path = graph.find_path(env.curr_location, destination, locations)
            if not isinstance(path, list):
                observation = path
            else:
                log("\n\nNAVIGATION\n\n")
                for hidden_step, hidden_action in enumerate(path):
                    observation, reward, done, info = env.step(hidden_action)
                    if curr_loc != env.curr_location:
                        if env.curr_location not in locations:
                            new_triplets_raw = [(env.curr_location, curr_loc, {"label": hidden_action})]
                            graph.add_triplets(new_triplets_raw)
                            locations.add(env.curr_location)
                        curr_loc = env.curr_location
                    if done:
                        break
                    log("Navigation step: " + str(hidden_step + 1))
                    log("Observation: " + observation + "\n\n")
                
            prev_action = plan[0]
        
        # Proceed action 
        else:
            if done: 
                break
            observation, reward, done, info = env.step(action)
            prev_action = action
            
        if len(plan) > 0:
            plan.pop(0)

        log("============================")
