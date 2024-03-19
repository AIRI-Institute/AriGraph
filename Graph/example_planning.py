from InstructorEmbedding import INSTRUCTOR
from scipy.spatial.distance import cosine
from jericho import FrotzEnv
import json
import numpy as np
from copy import deepcopy
from tqdm.auto import tqdm

from agent_detective import GPTagent
from graph import KnowledgeGraph
from semi_bigraph import KnowledgeSemiBiGraph
from textworld_adapter import TextWorldWrapper, graph_from_facts, get_text_graph, draw_graph
from triplet_graph import TripletGraph

def remove_equals(graph):
    graph_copy = deepcopy(graph)
    for triplet in graph_copy:
        if graph.count(triplet) > 1:
            graph.remove(triplet)
    return graph      

def parse_triplets_removing(text):
    text = text.split("[[")[-1]
    text = text.replace("[", "")
    text = text.strip("]")
    pairs = text.split("],")
    parsed_triplets = []
    for pair in pairs:
        splitted_pair = pair.split("->")
        if len(splitted_pair) != 2:
            continue
        first_triplet = splitted_pair[0].split(",")
        if len(first_triplet) != 3:
            continue
        subj, rel, obj = first_triplet[0].strip(''' '"\n'''), first_triplet[1].strip(''' '"\n'''), first_triplet[2].strip(''' '"\n''')
        parsed_triplets.append([subj, obj, {"label": rel}])
    return parsed_triplets

def parse_plan(plan):
    plan = plan.strip("[]").split(",")
    return [action.strip('''\n'" ''') for action in plan]

def log(text):
    print(text)
    with open("interactive_logs_goal_plan_navigation2.txt", "a") as file:
        file.write(text + "\n")


graph = TripletGraph()
agent = GPTagent(model = "gpt-4-0125-preview")
env = TextWorldWrapper("benchmark/navigation2/navigation2.z8")
observations = []

# For navigation2
walkthrough = ['take book', 'go east', 'put book on the shelf', 'go west', 'take apple', 'go south', 'examine refrigerator', 'open refrigerator', 'put apple in refrigerator', 'take icecream', 'eat icecream', 'END']

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
        log("Associated subgraph: " + str(associated_subgraph))
        new_triplets = graph.exclude(G_new.edges(data = True))
        prompt = prompt_goal.format(observation = observation, observations = observations[-1:], graph = graph, goal = goal, plan = plan)
        goal = agent.generate(prompt)
        log("Goal: " + goal)
        # prompt = prompt_planning.format(observation = observation, observations = observations[-1:], graph = graph, goal = goal, plan = plan)
        prompt = prompt_planning_without_obs.format(graph = graph, goal = goal, plan = plan)
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
            log("Outdated triplets truth: " + str(outdated_edges))
        
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
