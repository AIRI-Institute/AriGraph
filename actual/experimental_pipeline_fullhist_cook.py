from time import time

from parent_agent import GPTagent
from textworld_adapter import TextWorldWrapper, graph_from_facts
from parent_graph import TripletGraph
from graphs.subgraph_strategy import SubgraphStrategy
from agents.direct_action_agent import DirectActionAgent
from agents.plan_in_json_agent import PlanInJsonAgent
from graphs.history import History, HistoryWithPlan
from graphs.extended_graphs import ExtendedGraphSubgraphStrategy, ExtendedGraphPagerankStrategy, \
    ExtendedGraphMixtralPagerankStrategy, ExtendedGraphDescriptionPagerankStrategy
from graphs.description_graphs import DescriptionGraphBeamSearchStrategy
from graphs.parent_without_emb import GraphWithoutEmbeddings
from graphs.dummy_graph import DummyGraph
from graphs.steps_in_triplets import StepsInTripletsGraph
from prompts import *
from utils import *
from prompts_diff_agents import *
from win_cond import *

# There is configs of exp, changeable part of pipeline
# If you add some parameters, please, edit config
log_file = "exp_cooking_fullhistory"
env_name = "benchmark/cook/game.z8"
main_goal = ""
# main_goal = "Find the treasure"
model = "gpt-4-0125-preview"
agent_instance = GPTagent
graph_instance = StepsInTripletsGraph
history_instance = HistoryWithPlan
goal_freq = 10
threshold = 0.02
n_prev, majority_part = 1, 0.51

max_steps, n_attempts = 150, 2
n_neighbours = 4

system_prompt = """You are an agent who plays a text-based game. 
You will be provided with the history of your observations and actions in the environment, your current observation, content of your inventory and a list of valid actions. 
Your task will be provided in the first observation.
You need to select an action from the list of valid actions. Answer only with this action."""
config = {
    "log_file": log_file,
    "env_name": env_name,
    "main_goal": main_goal,
    "model": model,
    "goal_freq": goal_freq,
    "threshold": threshold,
    "system_prompt": system_prompt,
    "n_prev": n_prev,
    "majority_part": majority_part
}
# End of changeable part

log = Logger(log_file)

# Flexible init with only arguments class need
env = TextWorldWrapper(env_name)
walkthrough = ["examine Task note", "take Key 1", "go west", "go south", "go east", "go east", "unlock White locker with Key 1", 
"open White locker", "take Key 2 from White locker", "examine Note 2", "go west", "go west", "unlock Red locker with Key 2", 
"open Red locker", "take Key 3 from Red locker", "take Note 3 from Red locker", "examine Note 3", "go east", "go east", 
"go north", "go north", "go west", "go east", "go east", "unlock Cyan locker with Key 3", "open Cyan locker", 
"take Golden key from Cyan locker", "go west", "go south", "go south", "go west", "go west", "go north", 
"go east", "unclock Golden locker with Golden key", "unlock Golden locker with Golden key", "open Golden locker", 
"take treasure from Golden locker"]

explore_all_rooms = ["west", "north", "south", "south", "south", "north", "east", "east", "south", "north", "north", "north", 
                     "west", "east", "east"]

agent_summary = GPTagent(model = model, system_prompt= system_prompt) 

locations = set()
# observation, info = env.reset()
action = "start"
plan0 = "Explore all locations"
subgraph = "Nothing there"
description = "Nothing there"
# previous_location = env.curr_location.lower()
# for exp_act in explore_all_rooms:
#     start = time()
#     observation = observation.split("$$$")[-1]
#     inventory = env.get_inventory()
#     observation += f"\nInventory: {inventory}"
#     observation += f"\nAction that led to this: {action}"
#     log("Observation: " + observation)
    
#     locations.add(env.curr_location.lower())    
#     subgraph, description = graph.update(observation, plan0, subgraph, description, locations, env.curr_location.lower(), previous_location, action, 0, log)
#     previous_location = env.curr_location.lower()

#     observation, reward, done, info = env.step(exp_act)
#     action = exp_act
# os.makedirs("Visit_graph", exist_ok=True)
# graph.save("Visit_graph")
    
total_amount, total_time = 0, 0

for i in range(n_attempts):
    log("\n\n\n\n\n\n\nAttempt: " + str(i + 1))
    log("=" * 70)
    observations, hist = [], []
    locations = set()
    tried_action = {}
    env = TextWorldWrapper(env_name)
    observation, info = env.reset()
    action = "start"
    goal = "Start game"
    plan0 = f'''{{
  "main_goal": {main_goal},
  "plan_steps": [
    {{
      "sub_goal_1": "Start the game",
      "reason": "You should start the game"
    }},
  ],
}}'''
    subgraph = []
    description = "Nothing there"
    summary = "Still nothing"
    previous_location = env.curr_location.lower()
    attempt_amount, attempt_time = 0, 0
    done = False
    key1, key2, key3 = False, False, False
    graph = graph_instance(**find_args(graph_instance, config))
    action_history = []
    reward = 0
    step_reward = 0
    rewards = []
    for step in range(max_steps):
    # for step, new_action in enumerate(walkthrough[:25]):
        start = time()
        step_reward = 0
        log("Step: " + str(step + 1))
        G_true = graph_from_facts(info)    
        full_graph = G_true.edges(data = True)
        observation = observation.split("$$$")[-1]

        observation = remove_trailing_part(observation)
        if 'livingroom' in observation:
            observation = observation.replace("livingroom", "living room")
        if 'Livingroom' in observation:
            observation = observation.replace("Livingroom", "Living room")   

        if 'Recipe #1' in observation:
            observation = observation.replace("Recipe #1", "Recipe") 
        if step == 0:
            observation += 'Your task is to prepare the meal by following the recipe from a cookbook and eating it aftewards. Do not forget the content of recipe when you find it. When you will prepare food, remember that frying is done only with stove, roasting is done only with oven and grilling is done only with BBQ. Meal shoud be prepared in the kitchen. Do not forget to prepate meal after you gathered and processed all individual ingredients.'
        observation = "Step: " + str(step + 1) + "\n" + observation
        inventory = env.get_inventory()
        # if "Key 1" in inventory:
        #     key1 = True
        # if "Key 2" in inventory:
        #     key2 = True
        # if "Key 3" in inventory:
        #     key3 = True
        # if (not key1 and step > 40) or (not key2 and step > 70) or (not key3 and step > 100):
        #     done = True 

        if done:
            log("Game itog: " + observation)
            log("\n" * 10)
            break

        observation += f"\nInventory: {inventory}"
        observation += f"\nAction that led to this observation: {action}"
        log("Observation: " + observation)
        
        location = env.curr_location.lower()
        if location == 'livingroom':
            location = 'living room'
        locations.add(location)
        
        valid_actions = env.get_valid_actions()
        prompt = f'''\n1. Main goal: {main_goal}
    \n2. Your current observation: {observation}
    \n3. History of your previous observations and actions: {observations}
    \n4. Valid actions: {valid_actions}
    '''
        action, cost_plan = agent_summary.generate(prompt, jsn=False, t=0.2)
        observations.append(observation)
        log("Chosen action: " + action)
       
        
        previous_location = env.curr_location.lower()
        
        is_nav = "go to" in action
        if is_nav:
            destination = action.split('go to ')[1]
            path = graph.find_path(env.curr_location, destination, locations)
            print("path", path)
            if not isinstance(path, list):
                observation = path
            else:
                log("\n\nNAVIGATION\n\n")
                for hidden_step, hidden_action in enumerate(path):
                    observation, reward_, done, info = env.step(hidden_action)
                    step_reward += reward_
                    if done:
                        break
                    log("Navigation step: " + str(hidden_step + 1))
                    log("Observation: " + observation + "\n\n")
        else:
            observation, reward_, done, info = env.step(action)
            step_reward += reward_
            
        act_for_hist = action.lower()
        if is_nav or "north" in act_for_hist or "south" in act_for_hist or "east" in act_for_hist or "west" in act_for_hist:
            act_for_hist += f" (found yourself at {env.curr_location})"
        action_history.append(act_for_hist)
        
        if previous_location not in tried_action:
            tried_action[previous_location] = [(action, step + 1)]
        else:
            tried_action[previous_location].append((action, step + 1))

        G_true_new = graph_from_facts(info)    
        full_graph_new = G_true_new.edges(data = True)

        reward += step_reward
        rewards.append(reward)
        
        step_amount = agent_summary.total_amount  - total_amount
        attempt_amount += step_amount
        total_amount += step_amount
        log(f"\nTotal amount: {round(total_amount, 2)}$, attempt amount: {round(attempt_amount, 2)}$, step amount: {round(step_amount, 2)}$")
        
        step_time = time() - start
        attempt_time += step_time
        total_time += step_time
        log(f"Total time: {round(total_time, 2)} sec, attempt time: {round(attempt_time, 2)} sec, step time: {round(step_time, 2)} sec")
        log("=" * 70)
        log(f"\n\nREWARDS: {rewards}\n\n")