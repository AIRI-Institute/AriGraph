import json
from time import time

from agents.parent_agent import GPTagent
from graphs.contriever_graph import ContrieverGraph
from utils.envs_cfg import ENV_NAMES, FIRST_OBS, MAIN_GOALS
from utils.win_cond import win_cond_clean_place, win_cond_clean_take
from utils.textworld_adapter import TextWorldWrapper, graph_from_facts

from prompts.system_prompts import default_system_prompt, system_plan_agent, \
    system_action_agent_sub_expl, if_exp_prompt

from utils.utils import Logger, observation_processing, find_unexplored_exits, \
    simulate_environment_actions, action_processing, action_deprocessing



# Changeable part of pipeline

log_file = "arigraph_nav4_without_episodic"

# env_name can be picked from:
# ["hunt", "hunt_hard", "cook", "cook_hard", "cook_hardest", "cook_rl_baseline", "clean"]
# for test another envs edit utils.envs_cfg
env_name = "hunt_hard"
model = "gpt-4o"
retriever_device = "cpu"
api_key = "insert your key here"
n_prev, topk_episodic = 5, 2
max_steps, n_attempts = 150, 1
need_exp = True

# End of changeable part of pipeline

main_goal = MAIN_GOALS[env_name]
log = Logger(log_file)
env = TextWorldWrapper(ENV_NAMES[env_name])

agent = GPTagent(model = model, system_prompt=default_system_prompt, api_key = api_key)
agent_plan = GPTagent(model = "gpt-4-0125-preview", system_prompt=system_plan_agent, api_key = api_key)
agent_action = GPTagent(model = "gpt-4-0125-preview", system_prompt=system_action_agent_sub_expl, api_key = api_key)
agent_if_expl = GPTagent(model = model, system_prompt=if_exp_prompt, api_key = api_key)

def run():        
    total_amount, total_time = 0, 0

    for attempt in range(n_attempts):
        log("\n\n\n\n\n\n\nAttempt: " + str(attempt + 1))
        log("=" * 70)
        observations, history = [], []
        locations = set()
        observation, info = env.reset()
        action = "start"
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
        previous_location = observation_processing(env.curr_location).lower()
        attempt_amount, attempt_time = 0, 0
        done = False
        graph = ContrieverGraph(model, system_prompt = "You are a helpful assistant", device = retriever_device, api_key = api_key)
        reward, step_reward = 0, 0
        rewards = []
        for step in range(max_steps):
            start = time()
            log("Step: " + str(step + 1))
            observation = observation.split("$$$")[-1]
            observation = observation_processing(observation)
            if step == 0:
                observation += FIRST_OBS[env_name]
            observation = "Game step #" + str(step + 1) + "\n" + observation 
            inventory = env.get_inventory()

            if done:
                log("Game itog: " + observation)
                log("\n" * 10)
                break

            log("Observation: " + observation)        
            log("Inventory: " + str(inventory))
            locations.add(observation_processing(env.curr_location).lower())
            
            observed_items, _ = agent.item_processing_scores(observation, plan0)
            items = {key.lower(): value for key, value in observed_items.items()}
            log("Crucial items: " + str(items))
            
            subgraph, top_episodic = graph.update(observation, observations, plan=plan0, prev_subgraph=subgraph, locations=list(locations), curr_location=observation_processing(env.curr_location).lower(), previous_location=previous_location, action=action, log=log, items1 = items, topk_episodic=topk_episodic)
            observation += f"\nInventory: {inventory}"
            
            log("Length of subgraph: " + str(len(subgraph)))
            log("Associated triplets: " + str(subgraph))
            log("Episodic memory: " + str(top_episodic))
            
            if_explore, _ = agent_if_expl.generate(prompt=f"Plan: \n{plan0}", t=0.2) if need_exp else ("False", 0)
            if_explore = "True" in if_explore
            log('If explore: ' + str(if_explore))
            
            #Exploration
            all_unexpl_exits = get_unexpl_exits(locations, graph) if if_explore else ""
            if if_explore:
                log(all_unexpl_exits)

            valid_actions = [action_processing(action) for action in env.get_valid_actions()] + env.expand_action_space() if "cook" in env_name else env.get_valid_actions()
            valid_actions += [f"go to {loc}" for loc in locations]
            log("Valid actions: " + str(valid_actions))
            hist_obs = "\n".join(history)

            plan0 = planning(hist_obs, observation, plan0, subgraph, top_episodic, if_explore, all_unexpl_exits)
            action = choose_action(hist_obs, observation, subgraph, top_episodic, plan0, all_unexpl_exits, valid_actions, if_explore)
            
            observations.append(observation)
            observations = observations[-n_prev:]
            history.append(f"Observation: {observation}\nAction taken: {action}")
            history = history[-n_prev:]
            previous_location = observation_processing(env.curr_location).lower()

            observation, step_reward, done, info = process_action_get_reward(action, env, info, graph, locations, env_name)
            reward += step_reward
            rewards.append(reward)
            
            step_amount = agent.total_amount + graph.total_amount + agent_plan.total_amount + agent_action.total_amount + agent_if_expl.total_amount - total_amount
            attempt_amount += step_amount
            total_amount += step_amount
            log(f"\nTotal amount: {round(total_amount, 2)}$, attempt amount: {round(attempt_amount, 2)}$, step amount: {round(step_amount, 2)}$")
            
            step_time = time() - start
            attempt_time += step_time
            total_time += step_time
            log(f"Total time: {round(total_time, 2)} sec, attempt time: {round(attempt_time, 2)} sec, step time: {round(step_time, 2)} sec")
            log("=" * 70)
            
            log(f"\n\nTOTAL REWARDS: {rewards}\n\n")


def process_action_get_reward(action, env, info, graph, locations, env_name):
    G_true = graph_from_facts(info)    
    full_graph = G_true.edges(data = True)
    
    step_reward = 0
    is_nav = "go to" in action
    done = False
    if is_nav:
        destination = action.split('go to ')[1]
        path = graph.find_path(observation_processing(env.curr_location).lower(), destination, locations)
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
        
    
    G_true_new = graph_from_facts(info)    
    full_graph_new = G_true_new.edges(data = True)

    step_reward = simulate_environment_actions(full_graph, full_graph_new, win_cond_clean_take, win_cond_clean_place) \
        if env_name == "clean" else step_reward
    return observation, step_reward, done, info


def choose_action(observations, observation, subgraph, top_episodic, plan0, all_unexpl_exits, valid_actions, if_explore):
    # \n5. Your {topk_episodic} most relevant episodic memories from the past for the current situation: {top_episodic}.
    prompt = f'''\n1. Main goal: {main_goal}
\n2. History of {n_prev} last observations and actions: {observations} 
\n3. Your current observation: {observation}
\n4. Information from the memory module that can be relevant to current situation:  {subgraph}
\n5. Your {topk_episodic} most relevant episodic memories from the past for the current situation: {top_episodic}.
\n6. Your current plan: {plan0}'''

    if if_explore:
        prompt += f'''\n7. Yet unexplored exits in the environment: {all_unexpl_exits}'''
        

    prompt += f'''\n\nPossible actions in current situation: {valid_actions}'''  
    t = 0.2 if need_exp else 1
    action0, cost_action = agent_action.generate(prompt, jsn=True, t = t)
    log("Action: " + action0)
    
    try:
        action_json = json.loads(action0)
        action = action_json["action_to_take"]
    except:
        log("!!!INCORRECT ACTION CHOICE!!!")
        action = "look"

    action = action_deprocessing(action) if "cook" in env_name else action
    return action


def planning(observations, observation, plan0, subgraph, top_episodic, if_explore, all_unexpl_exits):
# \n5. Your {topk_episodic} most relevant episodic memories from the past for the current situation: {top_episodic}.
    prompt = f'''\n1. Main goal: {main_goal}
\n2. History of {n_prev} last observations and actions: {observations} 
\n3. Your current observation: {observation}
\n4. Information from the memory module that can be relevant to current situation: {subgraph}
\n5. Your {topk_episodic} most relevant episodic memories from the past for the current situation: {top_episodic}.
\n6. Your previous plan: {plan0}'''

    if if_explore:
        prompt += f'''\n7. Yet unexplored exits in the environment: {all_unexpl_exits}'''

    plan0, cost_plan = agent_plan.generate(prompt, jsn=True, t=0.2)
    log("Plan0: " + plan0)
    return plan0


def get_unexpl_exits(locations, graph):
    all_unexpl_exits = ""
    for loc in locations:
        loc_gr = graph.get_associated_triplets([loc], steps = 1)
        unexplored_exits = find_unexplored_exits(loc, loc_gr)
        all_unexpl_exits += f'\nUnexplored exits for {loc}: {unexplored_exits}'
    return all_unexpl_exits



if __name__ == "__main__":
    run()
