from InstructorEmbedding import INSTRUCTOR
from scipy.spatial.distance import cosine
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

log_file = "log_example_planning_withObs_nav4.txt"
env_name = "benchmark/navigation4/navigation4.z8"

log = Logger(log_file)
graph = TripletGraph()
agent = GPTagent(model = "gpt-4-0125-preview", system_prompt=system_prompt)
env = TextWorldWrapper(env_name)
observations = []

# For navigation2
# walkthrough = ["examine Task note", "take Key 1", "go west", "go south", "go south", "unlock Grey locker with Key 1",
#                    "open Grey locker", "take Note 2 from Grey locker", "examine Note 2", "take Key 2 from Grey locker",
#                    "go north", "go east", "go east", "go north", "unlock Orange locker with Key 2", "open Orange locker",
#                    "take Golden key from Orange locker", "go south", "go west", "go west", "go north", "go east",
#                    "unlock Golden locker with Golden key", "open Golden locker", "take treasure from Golden locker", "END"]

# For navigation4
walkthrough = ["examine Task note",
"take key 1", "go west", "go south", "go east", "go east", "go east", "go south", "go east", "unlock Bronze locker with Key 1", 
"open Bronze locker", "examine Note 2", "take Key 2", "go west", "go north", "go west", "go west", "go west", 
"unlock Red locker with Key 2", "open Red locker", "examine Note 3", "take Key 3 from Red locker", "go east", "go east", 
"go north", "go north", "go east", "unlock Cyan locker with Key 3", "open Cyan locker", "examine Note 4", "drop Key 1", 
"take Key 4 from Cyan locker", "go west", "go south", "go south", "go east", "go north", "unlock Black locker with Key 4", 
"open Black locker", "drop Key 2", "take Golden Key from Black locker", "go south", "go west", "go west", 
"go west", "go north", "go east", "unlock Golden locker with Golden Key", "open Golden locker", "take treasure from Golden locker", 
"examine treasure"]

locations = {"player", "Kids' Room"}
env.reset()
for action in walkthrough:
    locations.add(env.curr_location)
    env.step(action)
print("LOCATIONS: ", locations)
n_steps = 50

for i in range(1):
    log("Attempt: " + str(i + 1))
    log("\n\n")
    observation, info = env.reset()
    G_new = graph_from_facts(info)
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
        

        associated_subgraph = graph.get_all_triplets()
        G_true = graph_from_facts(info)
        G_true_in_text = get_text_graph(G_true)
        # log("Associated subgraph: " + str(associated_subgraph))
        new_triplets = graph.exclude(G_new.edges(data = True))
        prompt = prompt_goal.format(observation = observation, observations = observations[-1:], graph = G_true_in_text, goal = goal, plan = plan)
        goal = agent.generate(prompt)
        log("Goal: " + goal)
        log("Current plan: " + str(plan))
        prompt = prompt_planning.format(observation = observation, observations = observations[-1:], graph = G_true_in_text, goal = goal, plan = plan)
        # prompt = prompt_planning_without_obs.format(graph = G_true_in_text, goal = goal, plan = plan)
        response = agent.generate(prompt)
        plan = parse_plan(response)
        log("Model response: " + response)
        is_nav = False
        if len(plan) == 0:
            action = np.random.choice(valid_actions)
        elif plan[0].startswith("go to"):
            is_nav = True
        else:
            action = plan[0]
        outdated_edges = []
        if step > 0:
            old_edges, new_edges = G_old.edges(data = True), G_new.edges(data = True)
            for edge in old_edges:
                if edge not in new_edges:
                    outdated_edges.append(edge)
            # log("Outdated triplets truth: " + str(outdated_edges))
        
        graph.delete_triplets(outdated_edges)
        graph.add_triplets(G_new.edges(data = True))
        
        observations.append(observation)
        if is_nav:
            destination = plan[0].split("go to")[-1].strip('''\n'" ''')
            path = graph.find_path(env.curr_location, destination, locations)
            if not isinstance(path, list):
                observation = path
            else:
                G_old = graph_from_facts(info)
                log("\n\nNAVIGATION\n\n")
                for hidden_step, hidden_action in enumerate(path):
                    observation, reward, done, info = env.step(hidden_action)
                    if done:
                        break
                    log("Navigation step: " + str(hidden_step + 1))
                    log("Observation: " + observation + "\n\n")
                
            prev_action = plan[0]
        else:
            G_old = graph_from_facts(info)
            if done: 
                break
            observation, reward, done, info = env.step(action)
            prev_action = action
            
        G_new = graph_from_facts(info)
        if len(plan) > 0:
            plan.pop(0)

        log("============================")
