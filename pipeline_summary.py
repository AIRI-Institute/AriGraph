import json
from time import time

from agents.parent_agent import GPTagent
from utils.envs_cfg import ENV_NAMES, FIRST_OBS, MAIN_GOALS
from utils.win_cond import win_cond_clean_place, win_cond_clean_take
from utils.textworld_adapter import TextWorldWrapper, graph_from_facts

from prompts.system_prompts import system_plan_agent, summary_prompt, \
    system_action_agent_sub_expl

from utils.utils import Logger, observation_processing, simulate_environment_actions, \
    action_processing, action_deprocessing


# Changeable part of pipeline

log_file = "test_new_pipe_summary"

# env_name can be picked from:
# ["hunt", "hunt_hard", "cook", "cook_hard", "cook_rl_baseline", "clean"]
# for test another envs edit utils.envs_cfg
env_name = "clean"
model = "gpt-4-0125-preview"
api_key = "insert your key here"
n_prev = 5
max_steps, n_attempts = 5, 1

# End of changeable part of pipeline

main_goal = MAIN_GOALS[env_name]
log = Logger(log_file)
env = TextWorldWrapper(ENV_NAMES[env_name])

agent_plan = GPTagent(model = model, system_prompt=system_plan_agent, api_key = api_key)
agent_summary = GPTagent(model = model, system_prompt = summary_prompt, api_key = api_key) 
agent_action = GPTagent(model = model, system_prompt=system_action_agent_sub_expl, api_key = api_key)

def run():        
    total_amount, total_time = 0, 0

    for attempt in range(n_attempts):
        log("\n\n\n\n\n\n\nAttempt: " + str(attempt + 1))
        log("=" * 70)
        history = []
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
        summary = "Yet nothing"
        attempt_amount, attempt_time = 0, 0
        done = False
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
            
            observation += f"\nInventory: {inventory}"
            hist_obs = "\n".join(history)

            summary = get_summary(hist_obs, observation, summary)

            valid_actions = [action_processing(action) for action in env.get_valid_actions()] + env.expand_action_space() if "cook" in env_name else env.get_valid_actions()
            
            plan0 = planning(hist_obs, observation, summary, plan0)
            action = choose_action(hist_obs, observation, plan0, valid_actions, summary)
            
            history.append(f"Observation: {observation}\nAction taken: {action}")
            history = history[-n_prev:]

            observation, step_reward, done, info = process_action_get_reward(action, env, info, env_name)
            reward += step_reward
            rewards.append(reward)
            
            step_amount = agent_plan.total_amount + agent_action.total_amount + agent_summary.total_amount - total_amount
            attempt_amount += step_amount
            total_amount += step_amount
            log(f"\nTotal amount: {round(total_amount, 2)}$, attempt amount: {round(attempt_amount, 2)}$, step amount: {round(step_amount, 2)}$")
            
            step_time = time() - start
            attempt_time += step_time
            total_time += step_time
            log(f"Total time: {round(total_time, 2)} sec, attempt time: {round(attempt_time, 2)} sec, step time: {round(step_time, 2)} sec")
            log("=" * 70)
            
            log(f"\n\nTOTAL REWARDS: {rewards}\n\n")


def process_action_get_reward(action, env, info, env_name):
    G_true = graph_from_facts(info)    
    full_graph = G_true.edges(data = True)
    
    step_reward = 0
    observation, reward_, done, info = env.step(action)
    step_reward += reward_
        
    
    G_true_new = graph_from_facts(info)    
    full_graph_new = G_true_new.edges(data = True)

    step_reward = simulate_environment_actions(full_graph, full_graph_new, win_cond_clean_take, win_cond_clean_place) \
        if env_name == "clean" else step_reward
    return observation, step_reward, done, info


def choose_action(observations, observation, plan0, valid_actions, summary):
    prompt = f'''\n1. Main goal: {main_goal}
\n2. History of {n_prev} last observations and actions: {observations} 
\n3. Your current observation: {observation}
\n4. Your summary about current situation: {summary}
\n5. Your current plan: {plan0}

Possible actions in current situation: {valid_actions}'''       
    action0, cost_action = agent_action.generate(prompt, jsn=True, t=1)
    log("Action: " + action0)
    
    try:
        action_json = json.loads(action0)
        action = action_json["action_to_take"]
    except:
        log("!!!INCORRECT ACTION CHOICE!!!")
        action = "look"

    action = action_deprocessing(action) if "cook" in env_name else action
    return action


def planning(observations, observation, summary, plan0):
    prompt = f'''\n1. Main goal: {main_goal}
\n2. History of {n_prev} last observations and actions: {observations} 
\n3. Your current observation: {observation}
\n4. Your summary about current situation: {summary}
\n5. Your previous plan: {plan0}'''

    plan0, cost_plan = agent_plan.generate(prompt, jsn=True, t=0.2)
    log("Plan0: " + plan0)
    return plan0


def get_summary(observations, observation, summary):
    prompt = f'''\n1. Main goal: {main_goal}
\n2. History of {n_prev} last observations and actions: {observations} 
\n3. Your current observation: {observation}
\n4. Your previous summary: {summary}
Your summary: '''
    summary, cost = agent_summary.generate(prompt, t = 0.6)
    log("Summary: " + summary)
    return summary



if __name__ == "__main__":
    run()