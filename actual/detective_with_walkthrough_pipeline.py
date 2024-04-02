from time import time
from jericho import FrotzEnv

from parent_agent import GPTagent
from textworld_adapter import TextWorldWrapper
from parent_graph import TripletGraph
from graphs.subgraph_strategy import SubgraphStrategy
from agents.direct_action_agent import DirectActionAgent
from graphs.history import History
from graphs.extended_graphs import ExtendedGraphSubgraphStrategy, ExtendedGraphPagerankStrategy, ExtendedGraphMixtralPagerankStrategy
from graphs.dummy_graph import DummyGraph
from prompts import *
from utils import *

# There is configs of exp, changeable part of pipeline
# If you add some parameters, please, edit config
log_file = "exp_detective_extended_graph_based_on_walkthrough"
env_name = "benchmark/navigation2/navigation2.z8"
main_goal = "Find the treasure"
model = "gpt-4-0125-preview"
agent_instance = DirectActionAgent
graph_instance = ExtendedGraphPagerankStrategy
history_instance = History
goal_freq = 10
threshold = 0.02
n_prev, majority_part = 1, 0.51

max_steps, n_attempts = 75, 3
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
graph = graph_instance(**find_args(graph_instance, config))
agent = agent_instance(**find_args(agent_instance, config))
history = history_instance(**find_args(history_instance, config))
env = FrotzEnv("z-machine-games-master/jericho-game-suite/detective.z5")
walkthrough = env.get_walkthrough()

observations, hist = [], []
locations = set()
total_amount, total_time = 0, 0

graph.load("exp_detective_extended_graph_with_walkthrough")
tried_action = {}

for i in range(n_attempts):
    log("Attempt: " + str(i + 1))
    log("=" * 70)
    observation, info = env.reset()
    agent.reset()
    action = "start"
    goal = "Start game"
    is_nav = False
    previous_location = env.get_player_location().name.lower()
    attempt_amount, attempt_time = 0, 0
    done = False
    # for step, new_action in enumerate(walkthrough):
    for step in range(max_steps):
        try:
            start = time()
            
            # new_action = new_action.lower()
            # replacing = {"n": "north", "e": "east", "w": "west", "s": "south"}
            # if new_action in replacing:
            #     new_action = replacing[new_action]
            
            log("Step: " + str(step + 1))
            observation = observation.split("$$$")[-1]
            inventory = [item.name for item in env.get_inventory()]
            observation += f"\nInventory: {inventory}"
            valid_actions = env.get_valid_actions()
            observation += f"\nValid actions (just recommendation): {valid_actions}"
            observation += f"\nAction that led to this: {action}"
            location = env.get_player_location().name
            if env.get_player_location().name.lower() in tried_action:
                observation += f"\nActions that you tried here before: {tried_action[env.get_player_location().name.lower()]}"
            log("Observation: " + observation)
            
            locations.add(env.get_player_location().name.lower())
            
            # n_last, last_acts, last_locs = history.n_last(n_neighbours)
            # n_by_action, action_acts, action_locs = history.n_by_action(action, n_neighbours)
            # n_by_location, location_acts, location_locs = history.n_by_location(env.get_player_location().name, n_neighbours)
            
            # summaries = [history.summary(obss + [observation]) for obss in [n_last, n_by_action, n_by_location]]
            # log("Summary last: " + str(summaries[0]))
            # log("Summary action: " + str(summaries[1]))
            # log("Summary location: " + str(summaries[2]))
            
            # history.add_state(observation, i + 1, step + 1, action, env.get_player_location().name)
            # history.add_metastate(summaries[0], i + 1, step + 1, last_acts, last_locs)
            # history.add_metastate(summaries[1], i + 1, step + 1, action_acts, action_locs)
            # history.add_metastate(summaries[2], i + 1, step + 1, location_acts, location_locs)
            
            summaries = [None, None, None]
            
            subgraph = graph.update(observation, summaries, locations, env.get_player_location().name.lower(), previous_location, action, log)
            
            needful_args = {
                "observation": observation,
                "observations": observations,
                "goal": goal,
                "locations": list(locations),
                "curr_location": env.get_player_location().name.lower(),
                "previous_location": previous_location,
                "action": action,
                "env": env,
                "graph": graph,
                "agent": agent,
                "log": log,
                "main_goal": main_goal,
                "attempt": i + 1,
                "step": step + 1,
            }
            
            if done:
                log("Game itog: " + observation)
                log(f"Scored {info['score']} out of {env.get_max_score()}, total steps: {step + 1}\n")
                log("\n" * 10)
                break
            
            # Everything happens there
            needful_args["subgraph"] = subgraph
            # action = new_action
            action, goal, is_nav = agent.make_decision(**find_args(agent.make_decision, needful_args))
        
            needful_args.pop("env")
            needful_args.pop("graph")
            needful_args.pop("agent")
            needful_args.pop("log")
            needful_args["action"] = action
            needful_args["goal"] = goal
            
            observations.append(observation)
            observations = observations[-n_prev:]
            previous_location = env.get_player_location().name.lower()
            
            if is_nav:
                observation, reward, done, info = proceed_navigation(action, graph, env, locations, log)
            else:
                observation, reward, done, info = env.step(action)
            if previous_location not in tried_action:
                tried_action[previous_location] = {action}
            else:
                tried_action[previous_location].add(action)
                
            
            step_amount = graph.total_amount + agent.total_amount + history.total_amount - total_amount
            attempt_amount += step_amount
            total_amount += step_amount
            log(f"\nTotal amount: {round(total_amount, 2)}$, attempt amount: {round(attempt_amount, 2)}$, step amount: {round(step_amount, 2)}$")
            
            step_time = time() - start
            attempt_time += step_time
            total_time += step_time
            log(f"Total time: {round(total_time, 2)} sec, attempt time: {round(attempt_time, 2)} sec, step time: {round(step_time, 2)} sec")
                
            needful_args['step_time'] = step_time
            needful_args['step_amount'] = step_amount
            hist.append(deepcopy(needful_args))
            log.to_json(hist)
            log("=" * 70)
            
            graph.save(log_file)
            history.save(log_file)
            
        except:
            break