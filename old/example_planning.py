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

log_file = "log_example_planning_nav3_subgraph.txt"
env_name = "benchmark/navigation3/navigation3.z8"

log = Logger(log_file)
graph = TripletGraph()

# Only for clean
# system_prompt = "You are a housewife. Currently you are at large home where you should clean up, namely find things that are out of place and take them to their place."

agent = GPTagent(model = "gpt-4-0125-preview", system_prompt=system_prompt)
env = TextWorldWrapper(env_name)
observations = []

locations = {"player", "Kids' Room", "Kitchen"}
# locations = {"player", "kitchen", "bedroom", "livingroom", "corridor", "bathroom", "pantry", "backyard", "garden", "shed"}
env.reset()

# ATTENTION!!!
# walkthrough = env.walkthrough()

# For navigation2
# walkthrough = ["examine Task note", "take Key 1", "go west", "go south", "go south", "unlock Grey locker with Key 1",
#                    "open Grey locker", "take Note 2 from Grey locker", "examine Note 2", "take Key 2 from Grey locker",
#                    "go north", "go east", "go east", "go north", "unlock Orange locker with Key 2", "open Orange locker",
#                    "take Golden key from Orange locker", "go south", "go west", "go west", "go north", "go east",
#                    "unlock Golden locker with Golden key", "open Golden locker", "take treasure from Golden locker", "END"]

# For navigation4
# walkthrough = ["examine Task note",
# "take key 1", "go west", "go south", "go east", "go east", "go east", "go south", "go east", "unlock Bronze locker with Key 1", 
# "open Bronze locker", "examine Note 2", "take Key 2", "go west", "go north", "go west", "go west", "go west", 
# "unlock Red locker with Key 2", "open Red locker", "examine Note 3", "take Key 3 from Red locker", "go east", "go east", 
# "go north", "go north", "go east", "unlock Cyan locker with Key 3", "open Cyan locker", "examine Note 4", "drop Key 1", 
# "take Key 4 from Cyan locker", "go west", "go south", "go south", "go east", "go north", "unlock Black locker with Key 4", 
# "open Black locker", "drop Key 2", "take Golden Key from Black locker", "go south", "go west", "go west", 
# "go west", "go north", "go east", "unlock Golden locker with Golden Key", "open Golden locker", "take treasure from Golden locker", 
# "examine treasure"]

# For navigation3
walkthrough = ["examine Task note", "take Key 1", "go west", "go south", "go east", "go east", "unlock White locker with Key 1", 
"open White locker", "take Key 2 from White locker", "examine Note 2", "go west", "go west", "unlock Red locker with Key 2", 
"open Red locker", "take Key 3 from Red locker", "take Note 3 from Red locker", "examine Note 3", "go east", "go east", 
"go north", "go north", "go west", "go east", "go east", "unlock Cyan locker with Key 3", "open Cyan locker", 
"take Golden key from Cyan locker", "go west", "go south", "go south", "go west", "go west", "go north", 
"go east", "unclock Golden locker with Golden key", "unlock Golden locker with Golden key", "open Golden locker", 
"take treasure from Golden locker"]

# One for clean 3x3 default
# walkthrough = ['take toothbrush', 'go north', 'take dumbbell', 'take dirty plate', 'go east', 'take raw meat', 'go south', 'take school notebooks', 'go south', 'take tv remote', 'take flippers', 'go west', 'take teddy bear', 'put flippers on equipment rack', 'go west', 'take fantasy book', 'put dumbbell on dumbbell stand', 'go north', 'take buisness suit', 'open refrigerator', 'put raw meat in refrigerator', 'close refrigerator', 'open dishwasher', 'put dirty plate in dishwasher', 'close dishwasher', 'go north', 'take sleeping mask', 'take dining chair', 'put toothbrush on bathroom sink', 'go east', 'open toy storage cabinet', 'put teddy bear in toy storage cabinet', 'close toy storage cabinet', 'put school notebooks on study table', 'go east', 'put tv remote on tv table', 'go south', 'open wardrobe', 'put buisness suit in wardrobe', 'close wardrobe', 'put sleeping mask on bedside table', 'go south', 'put fantasy book on bookcase', 'go west', 'go north', 'drop dining chair', 'END']

for action in walkthrough:
    locations.add(env.curr_location)
    env.step(action)
log("LOCATIONS: " + str(locations))
n_steps = 50
n_attempts = 1

for i in range(n_attempts):
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
        
        # Extracting true graph
        G_true = graph_from_facts(info)
        graph.delete_all()
        graph.add_triplets(G_true.edges(data = True))
        
        # Using subgraph
        observed_items, remembered_items = agent.bigraph_processing(observations, observation)
        items = [list(item.keys())[0] for item in observed_items + remembered_items]
        log("Crucial items: " + str(items))
        associated_subgraph = graph.get_associated_triplets(items, steps = 2)
        
        #Using full graph
        # associated_subgraph = get_text_graph(G_true)
        
        log("Associated subgraph: " + str(associated_subgraph))

        # Setting goal
        prompt = prompt_goal.format(observation = observation, observations = observations[-1:], graph = associated_subgraph, goal = goal, plan = plan)
        goal = agent.generate(prompt)
        log("Goal: " + goal)
        log("Current plan: " + str(plan))
        
        # Constructing plan
        prompt = prompt_planning.format(observation = observation, observations = observations[-1:], graph = associated_subgraph, goal = goal, plan = plan)
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
                G_old = graph_from_facts(info)
                log("\n\nNAVIGATION\n\n")
                for hidden_step, hidden_action in enumerate(path):
                    observation, reward, done, info = env.step(hidden_action)
                    if done:
                        break
                    log("Navigation step: " + str(hidden_step + 1))
                    log("Observation: " + observation + "\n\n")
                
            prev_action = plan[0]
        
        # Proceed action 
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
    log("Game itog: " + observation)
    log("\n"*10)
