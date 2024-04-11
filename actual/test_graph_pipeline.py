from time import time

from observedgpaph import ObservedGraph
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
from graphs.dummy_graph import DummyGraph
from prompts import *
from utils import *
from textworld_adapter import *

# There is configs of exp, changeable part of pipeline
# If you add some parameters, please, edit config
log_file = "exp_nav3_description_beamsearch"
env_name = "benchmark/navigation3/navigation3.z8"
main_goal = "Find the treasure"
model = "gpt-4-0125-preview"
agent_instance = PlanInJsonAgent
graph_instance = DescriptionGraphBeamSearchStrategy
history_instance = HistoryWithPlan
goal_freq = 10
threshold = 0.02
n_prev, majority_part = 1, 0.51

max_steps, n_attempts = 15, 1
n_neighbours = 4

system_prompt = actual_system_prompt.format(main_goal = main_goal)
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
obs_graph = ObservedGraph()
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

observations, hist = [], []
locations = set()
tried_action = {}
total_amount, total_time = 0, 0

for i in range(n_attempts):
    log("Attempt: " + str(i + 1))
    log("=" * 70)
    observation, info = env.reset()
    agent.reset()
    action = "start"
    goal = "Start game"
    subgraph = "Nothing there"
    previous_location = env.curr_location.lower()
    attempt_amount, attempt_time = 0, 0
    done = False
    # for step in range(max_steps):
    for step, new_action in enumerate(walkthrough):
        start = time()
        
        old_obs = observation
        G_true = graph_from_facts(info)
        full_graph = G_true.edges(data = True)
        obs_graph.update_graph_based_on_observation(observation, full_graph)
        print(obs_graph.graph.edges(data = True))
        breakpoint()
        
        observation = observation.split("$$$")[-1]
        observation = "Step: " + str(step + 1) + "\n" + observation
        inventory = env.get_inventory()
        observation += f"\nInventory: {inventory}"
        observation += f"\nAction that led to this: {action}"
        if env.curr_location.lower() in tried_action:
            observation += f"\nActions that you tried here before: {tried_action[env.curr_location.lower()]}"
        
        locations.add(env.curr_location.lower())
        
        # subgraph, description = graph.update(observation, observations, agent.plan, subgraph, locations, env.curr_location.lower(), previous_location, action, step + 1, log)
        # valid_actions = env.get_valid_actions()
        # description += f"\nValid actions (just recommendation): {valid_actions}"
        
        if done:
            log("Game itog: " + observation)
            log("\n" * 10)
            break
        
        action, goal, is_nav = new_action, "without goal", False    

        observations.append(observation)
        observations = observations[-n_prev:]
        previous_location = env.curr_location.lower()
        
        if is_nav:
            observation, reward, done, info = proceed_navigation(action, graph, env, locations, log)
        else:
            observation, reward, done, info = env.step(action)
        if previous_location not in tried_action:
            tried_action[previous_location] = {action}
        else:
            tried_action[previous_location].add(action)
            
         # Update the knowledge graph based on observations and actions
        if any(direction in action for direction in ["west", "east", "south", "north"]):
            obs_graph.update_graph_for_movement(old_obs, action, observation, full_graph)
        else:
            obs_graph.update_graph_based_on_action(observation, action, full_graph)            
        
        step_amount = graph.total_amount + agent.total_amount + history.total_amount - total_amount
        attempt_amount += step_amount
        total_amount += step_amount
        log(f"\nTotal amount: {round(total_amount, 2)}$, attempt amount: {round(attempt_amount, 2)}$, step amount: {round(step_amount, 2)}$")
        
        step_time = time() - start
        attempt_time += step_time
        total_time += step_time
        log(f"Total time: {round(total_time, 2)} sec, attempt time: {round(attempt_time, 2)} sec, step time: {round(step_time, 2)} sec")