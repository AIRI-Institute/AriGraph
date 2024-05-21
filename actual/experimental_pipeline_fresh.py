from time import time

from parent_agent import GPTagent
from textworld_adapter import TextWorldWrapper
from parent_graph import TripletGraph
from graphs.subgraph_strategy import SubgraphStrategy
from agents.direct_action_agent import DirectActionAgent
from agents.plan_in_json_agent import PlanInJsonAgent
from graphs.history import History, HistoryWithPlan
from graphs.extended_graphs import ExtendedGraphSubgraphStrategy, ExtendedGraphPagerankStrategy, \
    ExtendedGraphMixtralPagerankStrategy, ExtendedGraphDescriptionPagerankStrategy
from graphs.description_graphs import DescriptionGraphBeamSearchStrategy
from graphs.parent_without_emb import GraphWithoutEmbeddings
from graphs.contriever_graph_retrieve import ContrieverGraphNew 
from graphs.contriever_graph import ContrieverGraph
from graphs.dummy_graph import DummyGraph
from graphs.steps_in_triplets import StepsInTripletsGraph
from prompts import *
from utils import *
from prompts_diff_agents import *

# There is configs of exp, changeable part of pipeline
# If you add some parameters, please, edit config
log_file = "exp_nav3_big"
env_name = "benchmark/navigation3/navigation3_1.z8"
main_goal = ""
model = "gpt-4-0125-preview"
agent_instance = GPTagent
graph_instance = ContrieverGraphNew
history_instance = HistoryWithPlan
goal_freq = 10
threshold = 0.02
n_prev, majority_part = 3, 0.51

max_steps, n_attempts = 150, 2
n_neighbours = 4

system_prompt = system_prompt
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
graph = graph_instance(**find_args(graph_instance, config))
agent = agent_instance(**find_args(agent_instance, config))
history = history_instance(**find_args(history_instance, config))
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

agent_if_exp = GPTagent(model = model, system_prompt= if_exp_prompt) 
agent_plan = GPTagent(model = model, system_prompt=system_plan_agent)
agent_action = GPTagent(model = model, system_prompt=system_action_agent_sub_expl)

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
    agent.reset()
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
    previous_location = env.curr_location.lower()
    attempt_amount, attempt_time = 0, 0
    done = False
    key1, key2, key3 = False, False, False
    graph = graph_instance(**find_args(graph_instance, config))
    action_history = []
    for step in range(max_steps):
    # for step, new_action in enumerate(walkthrough[:25]):
        start = time()
        log("Step: " + str(step + 1))
        observation = observation.split("$$$")[-1]
        if step == 0:
            observation += f""" \n Your task is to get a treasure. Treasure is hidden in the golden locker. You need a golden key to unlock it. The key is hidden in one of the other lockers located in the environment. All lockers are locked and require a specific key to unlock. The key 1 you found in room A unlocks white locker. Read the notes that you find, they will guide you further."""
        observation = "Step: " + str(step + 1) + "\n" + observation
        inventory = env.get_inventory()
        if "Key 1" in inventory:
            key1 = True
        if "Key 2" in inventory:
            key2 = True
        if "Key 3" in inventory:
            key3 = True
        if (not key1 and step > 40) or (not key2 and step > 70) or (not key3 and step > 100):
            done = True 

        if done:
            log("Game itog: " + observation)
            log("\n" * 10)
            break

        observation += f"\nInventory: {inventory}"
        observation += f"\nAction that led to this observation: {action}\n\n"
        # if env.curr_location.lower() in tried_action:
        #     observation += f"\nActions that you tried here before: {tried_action[env.curr_location.lower()]}"
        # observation += f"\nActions that you made since game started: {action_history}"
        # observation += f"\nGoal that led to this: {goal}"
        log("Observation: " + observation)
        
        locations.add(env.curr_location.lower())
        
        observed_items, cost_items = agent.bigraph_processing_scores(observation, plan0)
        items = {key.lower(): value for key, value in observed_items.items()}
        log("Crucial items: " + str(items))
        # associated_subgraph = graph.update(observation=observation, observations=observations, locations=list(locations), curr_location=env.curr_location.lower(), previous_location=previous_location, action=action, log=log, items=items, goal="")
        subgraph, _, _ = graph.update(observation, observations, plan=plan0, prev_subgraph=subgraph, locations=list(locations), curr_location=env.curr_location.lower(), previous_location=previous_location, action=action, log=log, step = step + 1, items1 = items)
        
        log("Length of subgraph: " + str(len(subgraph)))
        log("Associated triplets: " + str(subgraph))
        # while True:
        #     triplet = input("Enter triplet: ")
        #     if triplet == "end":
        #         break
        #     subgraph.append(f"Step {step + 1}: {triplet}")
        
        # if if_explore == True:
        valid_actions = env.get_valid_actions() + [f"go to {loc}" for loc in locations]
        tried_now = {act[0] for act in tried_action[env.curr_location.lower()]}\
            if env.curr_location.lower() in tried_action else {}
        not_yet_tried = list({act for act in valid_actions if act not in tried_now})
        log("Actions that isn't tried: " + str(not_yet_tried))
        prompt = f'''\n1. Main goal: {main_goal}
    \n2. History of {n_prev} last observations and actions: {observations} 
    \n3. Your current observation: {observation}
    \n4. Information from the memory module that can be relevant to current situation: {subgraph}
    \n5. Your current plan: {plan0}    
    
    Remember that you should not visit locations and states that you visited before when you are exploring.
    '''
        plan0, cost_plan = agent_plan.generate(prompt, jsn=True, t=0.2)
        log("Plan0: " + plan0)
        plan_json = json.loads(plan0)
       
        sub_goal_1 = plan_json["plan_steps"][0]["sub_goal_1"]
        reason1 = plan_json["plan_steps"][0]["reason"]
        
        # if_explore, cost = agent_if_exp.generate(prompt=f"Plan: \n{plan0}", t=0.2)
        # if_explore = if_explore == "True"
        # log('if_exp: ' + str(if_explore))
    #     else:
    #         prompt = f'''\n1.Main goal: {main_goal}
    # \n2. History of {n_prev} last observations and actions: {observations} 
    # \n3. Your current observation: {observation}
    # \n4. {inventory}
    # \n5. Information from the memory module that can be relevant to current situation: {subgraph}
    # \n6. Your current plan: {plan0}
    # '''


        #Generate action
        # acts_with_cons = graph.get_conseq(tried_action[env.curr_location.lower()])\
        #     if env.curr_location.lower() in tried_action else []
        # log("Actions with consequences: " + str(acts_with_cons))
        
        prompt = f'''\n1. Main goal: {main_goal}
\n2. History of {n_prev} last observations and actions: {observations} 
\n3. Your current observation: {observation}
\n4. Information from the memory module that can be relevant to current situation:  {subgraph}
\n5. Your current plan: {plan0}

Possible actions in current situation (you should choose several actions from this list and estimate their probabilities): {valid_actions}'''          
        action0, cost_action = agent_action.generate(prompt, jsn=True, t=1.2)
        
        log("Action: " + action0)
        
        try:
            action_json = json.loads(action0)
            action = action_json["action_to_take"]
        except:
            action = "look"
        
        observations.append(observation)
        observations = observations[-n_prev:]
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
                    observation, reward, done, info = env.step(hidden_action)
                    if done:
                        break
                    log("Navigation step: " + str(hidden_step + 1))
                    log("Observation: " + observation + "\n\n")
        else:
            observation, reward, done, info = env.step(action)
            
        act_for_hist = action.lower()
        if is_nav or "north" in act_for_hist or "south" in act_for_hist or "east" in act_for_hist or "west" in act_for_hist:
            act_for_hist += f" (found yourself at {env.curr_location})"
        action_history.append(act_for_hist)
        
        if previous_location not in tried_action:
            tried_action[previous_location] = [(action, step + 1)]
        else:
            tried_action[previous_location].append((action, step + 1))
        
        step_amount = agent.total_amount + graph.total_amount + agent_plan.total_amount + agent_action.total_amount + agent_if_exp.total_amount - total_amount
        attempt_amount += step_amount
        total_amount += step_amount
        log(f"\nTotal amount: {round(total_amount, 2)}$, attempt amount: {round(attempt_amount, 2)}$, step amount: {round(step_amount, 2)}$")
        
        step_time = time() - start
        attempt_time += step_time
        total_time += step_time
        log(f"Total time: {round(total_time, 2)} sec, attempt time: {round(attempt_time, 2)} sec, step time: {round(step_time, 2)} sec")
        log("=" * 70)
        
        graph.save(log_file)
        history.save(log_file)