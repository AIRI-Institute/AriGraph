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

# env = FrotzEnv("z-machine-games-master/jericho-game-suite/detective.z5")
# obs, info = env.reset()
# done = False
# while not done:
#     print(obs)
#     print("Valid actions (just recommendation):", env.get_valid_actions())
#     print("Can you choose an action to perform in the game now?")
#     obs, reward, done, info = env.step(input(">>> "))

# raise "False"
def remove_equals(graph):
    graph_copy = deepcopy(graph)
    for triplet in graph_copy:
        if graph.count(triplet) > 1:
            graph.remove(triplet)
    return graph      

def process_triplets(raw_triplets):
    raw_triplets = raw_triplets.split(";")
    triplets = []
    for triplet in raw_triplets:
        if len(triplet.split(",")) > 3:
            continue
        elif len(triplet.split(",")) < 3:
            continue
        else:
            subj, relation, obj = triplet.split(",")
            subj, relation, obj = subj.strip(' \n"'), relation.strip(' \n"'), obj.strip(' \n"')
            if len(subj) == 0 or len(relation) == 0 or len(obj) == 0:
                continue
            triplets.append([subj, obj, {"label": relation}])
        
    return triplets

def parse_triplets(text):
    text = text.split("[[")[-1]
    text = text.replace("[", "")
    text = text.strip("]")
    triplets = text.split("],")
    parsed_triplets = []
    for triplet in triplets:
        parsed_triplet = triplet.split(",")
        if len(parsed_triplet) != 3:
            continue
        subj, rel, obj = parsed_triplet[0].strip(''' '"\n'''), parsed_triplet[1].strip(''' '"\n'''), parsed_triplet[2].strip(''' '"\n''')
        parsed_triplets.append([subj, obj, {"label": rel}])
    return parsed_triplets

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
    with open("interactive_logs_expanding_replacing_clean_3x3.txt", "a") as file:
        file.write(text + "\n")

paths = {
    "benchmark/recipe3_cook_cut/tw-cooking-recipe3+take3+cook+cut+drop+go1-7yGrcV9pTE8DF75n.z8": "Recipe_3_cook_cut",
    "benchmark/take2_go9/tw-cooking-recipe2+take2+go9-Q9nDu630U5j3tqBG.z8": "Take2_go9",
    "benchmark/navigation4/navigation4.z8": "Navigation4",
    "benchmark/navigation2/navigation2.z8": "Navigation2",
}

Paths = [
    "benchmark/recipe3_cook_cut/tw-cooking-recipe3+take3+cook+cut+drop+go1-7yGrcV9pTE8DF75n.z8",
    "benchmark/take2_go9/tw-cooking-recipe2+take2+go9-Q9nDu630U5j3tqBG.z8",
    # "benchmark/navigation4/navigation4.z8",
    # "benchmark/navigation2/navigation2.z8",
    "benchmark/take2_go12/tw-cooking-recipe2+take2+go12-Q9nDu630U5j3tqBG.z8",
    "benchmark/recipe5_cook_cut/tw-cooking-recipe5+take5+cook+cut+drop+go1-7yGrcV9pTE8DF75n.z8",
]


# for path in Paths:
#     print(path)
#     env = TextWorldWrapper(path)
#     env.reset()
#     print(env.walkthrough())
#     print("=====================")
agent = GPTagent(model = "gpt-4-0125-preview")
# env = FrotzEnv("z-machine-games-master/jericho-game-suite/detective.z5")
env = TextWorldWrapper("benchmark/clean_3x3/clean_3x3_mess.z8")
agent.system_prompt = '''You play at the text game, goal and some needful information are given in Task note. Please, try to achieve the goal fast and effective. If you think you haven’t some crucial knowledges about the game, explore new areas and items. Otherwise, go to the goal and pay no attention to noisy things.'''
prompt_extraction = '''## 1. Overview
Your task is to extract information from game observations in structured formats to build a knowledge graph.
- **Nodes** represent entities and concepts. They are akin to Wikipedia nodes.
- The aim is to achieve simplicity and clarity in the knowledge graph, making it useful for you in the future.
- Use the following triplet format for extracted data: "triplet1; triplet2; ...", more detailed - "subject1, relation1, object1; subject2, relation2, object2; ...", where a triplet is "subject1, relation1, object1" or "subject2, relation2, object2".
- For example, from the text "Albert Einstein, born in Germany, is known for developing the theory of relativity" you should extract the following data: "Albert Einstein, country, Germany; Albert Einstein, developed, Theory of relativity".
- Both subject and object in triplets should be akin to Wikipedia nodes. Object can be a date or number, objects should not contain citations or sentences.
- Instead of generating complex objects, divide triplet with complex object into two triplets with more precise objects. For example, the text "John Doe is a developer at Google" corresponds to two triplets: "John Doe, position, developer; John Doe, employed by, Google".
- Exclude from the extracted data triplets where subject or object are collective entities such as "People".
- Exclude from the extracted data triplets where object is a long phrase with more than 5 words.
- Similar relations, such as "has friend" and "friend of", replace with uniform relation, for example, "has friend"
- Similar entities, such as "House" and "house" or "small river" and "little river", replace with uniform relation, for example, "house" or "small river"
- If some subject just has some state or property, object in triplet must be "itself" (for example, from text "John open the door and fry chiken" you should extract the following data: "Door, opened, itself; Chiken, fried, itself").  
## 2. Coreference Resolution
- **Maintain Entity Consistency**: When extracting entities, it is vital to ensure consistency.
If an entity, such as "John Doe", is mentioned multiple times in the text but is referred to by different names or pronouns (e.g., "Joe", "he"),
always use the most complete identifier for that entity throughout the knowledge graph. In this example, use "John Doe" as the entity ID.
Remember, the knowledge graph should be coherent and easily understandable, so maintaining consistency in entity references is crucial.

####
Observation: {observation} 
####
Previous observations and actions: {observations}
####

Please, extract information from this data following instructions from begin of this prompt.

Extracted data: '''

prompt_filter_wrong = '''#### Graph: {graph}
####
Observation: {observation}
####
Previous observations and actions: {observations}
####

Please review the provided graph and select the triplets that are inaccurate based on the current game state.

For example, in the following data: "Graph: [['John', 'at', 'hall'], ['hall', 'west of', 'kitchen'], ['kitchen', 'west of', 'hall']] Observation: John found himself at hall. He moved to the west before. Previous observations and actions: John found himself at the kitchen." You should exclude the following triplets: [['kitchen', 'west of', 'hall']]. This triplet is wrong because John moved from the kitchen to the west and found himself at the hall, so the relationships are reversed.

In the answer list, provide the inaccurte triplets from the graph in the format: "[unactual triplet1, unactual triplet2, ...]". Please adhere to the specified format for the answer.

Answer:'''

prompt_filter_outdated = '''#### Graph: {graph}
####
Observation: {observation}
####
Previous observations and actions: {observations}
####

Please review the provided graph and select the triplets that are outdated based on the current game state. Consider triplets that are false now.

For example: "Graph: [['player', 'at', 'kitchen'], ['key', 'located at', 'table'], ['table', 'located in', 'kitchen'], ['player', 'inventory contains', 'key']] Observation: Taken. Inventory: ['key']. John took the key before. Previous observations and actions: John found himself at the kitchen, he sees the table with the key on it." You should exclude the following triplet: [['key', 'located at', 'table']]. This triplet should be excluded because the player took the key from the table in the previous step and it is now in the player's inventory, so the key is no longer located on the table.

In the answer list, provide the outdated triplets from the graph in the format: "[unactual triplet1, unactual triplet2, ...]". Please adhere to the specified format for the answer.

Answer:'''

prompt_goal = '''#### Graph: {graph}
####
Observation: {observation}
####
Previous observations and actions: {observations}
####
Previous goal: {goal}
####
Current plan: {plan}
####

Based on the information provided above, your task is to set a clear and actionable goal for the next few steps in the game. This goal should be beneficial, directly contribute to winning the game, and be achievable given the current game context. Examples of appropriate goals include "Explore the east exit from the Kitchen", "Open the golden chest", "Find a path to the library", "Descend to the cellar", and "Deliver the red book to the home". Each of these goals could be relevant in different scenarios.

Please define a goal considering the current situation in the game.
Goal: '''

prompt_refining = """The triplets denote facts about the environment where the player moves. The player takes actions and the environment changes, so some triplets from the list of existing triplets should be replaced with one of the new triplets. For example, the door was previously opened and now it is closed, so the triplet "Door, state, opened" should be replaced with the triplet "Door, state, closed". Another example, the player took the item from the locker and the triplet "Item, is in, Locker" should be replaced with the triplet "Player, has, Item".
First example of existing triplets: "Golden locker, state, open"; "Room K, is west of, Room I".
First example of new triplets: "Golden locker, state, closed"; "Room K, is west of, Room I".
First example of replacing: [["Golden locker, state, open" -> "Golden locker, state, closed"],].
In some cases there are no triplets to replace.
Second example of existing triplets: Golden locker, state, open; "Room K, is west of, Room I".
Second example of new triplets: "Room T, is north of, Room N".
Second example of replacing: [].
Generate replacing from existing triplets and new_triplets by analogy with first and second examples.
Existing triplets: {ex_triplets}.
New triplets: {new_triplets}.
Replacing: """


prompt_filter = """The triplets denote facts about the environment where the player moves. The player takes actions and the environment changes, so some triplets from the list of existing triplets should be deleted. For example, the door was previously opened and now it is closed, so the triplet "Door, state, opened" should be deleted. Another example, the player took the item from the locker and the triplet "Item, is in, Locker" should be deleted too.
First example of observation: Taken. You keep in hand an apple. Action that led to this: take an apple
First example of previous observations: You see a table. On this table you see an apple. Your hands are empty
First example of existing triplets: [['apple', 'located at', 'table'], ['hands', 'are', 'empty'], ['apple', 'in', 'hands']]
First example of deleted triplets: [['apple', 'located at', 'table'], ['hands', 'are', 'empty']]

In some cases there are no triplets to replace.
Second example of observation: You are at the street with many buses here. Action that led to this: north
Second example of previous observations: You see a table. On this table you see an apple. Your hands are empty
Second example of existing triplets: [['apple', 'located at', 'table'], ['hands', 'are', 'empty'], ['buses', 'located at', 'street']]
Second example of deleted triplets: []

Generate replacing from existing triplets and new_triplets by analogy with first and second examples.
####
Observation: {observation}
Previous observations: {observations}
Existing triplets: {ex_triplets}
####
Deleted triplets: """

prompt_planning = '''I will provide you with graph of the environment. It consists of connected rooms with different items. 
####
Graph: {graph}

I will also provide you with current game state. It consist of current observation and previous observations.
####
Observation: {observation}
Previous observations: {observations}
Current plan: {plan}
####

Your task is to achieve the goal. 
####
Goal: {goal}
####

Write me new plan on how you will solve this task. 
Plan must consist of actions in environment. Examples of action: "take *something*", "examine *something*", "open *something*", "go to *some location*".
Avoid to use actions like "north", "west", "south" and "east", use "go to" action instead to move at chosen location.
Example of correct plan for making sandwich and give it to son: ["go to kitchen", "take bread", "take butter", "make sandwich", "go to living room", "give sandwich to son"]
####
Generated plan: '''

prompt_planning_without_obs = '''I will provide you with graph of the environment. It consists of connected rooms with different items. 
####
Graph: {graph}

I will also provide you curent plan.
####
Current plan: {plan}
####

Your task is to achieve the goal. 
####
Goal: {goal}
####

Write me new plan on how you will solve this task. 
Plan must consist of actions in environment. Examples of action: "take *something*", "examine *something*", "open *something*", "go to *some location*".
Avoid to use actions like "north", "west", "south" and "east", use "go to" action instead to move at chosen location.
Example of correct plan for making sandwich and give it to son: ["go to kitchen", "take bread", "take butter", "make sandwich", "go to living room", "give sandwich to son"]
####
Warning! Plan must be generated in format of list of actions (like in example above). Correct format of answer: [action_1, action_2, ...]
Generated plan: '''














# Replacing test

graph = TripletGraph()
observations = []
# # One for navigation
# # walkthrough = ["examine Task note", "take Key 1", "go west", "go south", "go south", "unlock Grey locker with Key 1",
# #                    "open Grey locker", "take Note 2 from Grey locker", "examine Note 2", "take Key 2 from Grey locker",
# #                    "go north", "go east", "go east", "go north", "unlock Orange locker with Key 2", "open Orange locker",
# #                    "take Golden key from Orange locker", "go south", "go west", "go west", "go north", "go east",
# #                    "unlock Golden locker with Golden key", "open Golden locker", "take treasure from Golden locker", "END"]

# # One for 2x2
# # walkthrough = ['take book', 'go east', 'put book on the shelf', 'go west', 'take apple', 'go south', 'examine refrigerator', 'open refrigerator', 'put apple in refrigerator', 'take icecream', 'eat icecream', 'END']

# # One for clean 3x3 default
walkthrough = ['take toothbrush', 'go north', 'take dumbbell', 'take dirty plate', 'go east', 'take raw meat', 'go south', 'take school notebooks', 'go south', 'take tv remote', 'take flippers', 'go west', 'take teddy bear', 'put flippers on equipment rack', 'go west', 'take fantasy book', 'put dumbbell on dumbbell stand', 'go north', 'take buisness suit', 'open refrigerator', 'put raw meat in refrigerator', 'close refrigerator', 'open dishwasher', 'put dirty plate in dishwasher', 'close dishwasher', 'go north', 'take sleeping mask', 'take dining chair', 'put toothbrush on bathroom sink', 'go east', 'open toy storage cabinet', 'put teddy bear in toy storage cabinet', 'close toy storage cabinet', 'put school notebooks on study table', 'go east', 'put tv remote on tv table', 'go south', 'open wardrobe', 'put buisness suit in wardrobe', 'close wardrobe', 'put sleeping mask on bedside table', 'go south', 'put fantasy book on bookcase', 'go west', 'go north', 'drop dining chair', 'END']

locations = {"player", "Kids' Room"}
env.reset()
for action in walkthrough:
    locations.add(env.curr_location)
    env.step(action)
print("LOCATIONS: ", locations)

for i in range(1):
    log("Attempt: " + str(i + 1))
    log("\n\n")
    observation, info = env.reset()
    # G_new = graph_from_facts(info)
    # walkthrough = env.walkthrough()
    # walkthrough = env.get_walkthrough()
    prev_action = "start"
    done = False
    for step, action in enumerate(walkthrough):
        log("Step: " + str(step + 1))
        observation = observation.split("$$$")[-1]
        inventory = env.get_inventory()
        # inventory = [item.name for item in env.get_inventory()]
        observation += f"\nInventory: {inventory}"
        valid_actions = env.get_valid_actions()
        observation += f"\nValid actions (just recommendation): {valid_actions}"
        observation += f"\nAction that led to this: {prev_action}"
        log("Observation: " + observation)
        
        observed_items, remembered_items = agent.bigraph_processing(observations, observation)
        items = [list(item.keys())[0] for item in observed_items + remembered_items]
        log("Crucial items: " + str(items))
        associated_subgraph = graph.get_associated_triplets(items)


        prompt = prompt_extraction.format(observation = observation, observations = observations[-1:])
        response = agent.generate(prompt)
        new_triplets_raw = process_triplets(response)
        new_triplets = graph.exclude(new_triplets_raw)
        # log("Model response: " + response)
        # log("New triplets: " + str(new_triplets_raw))
        log("New triplets excluded: " + str(new_triplets))
        
        
        prompt = prompt_refining.format(ex_triplets = associated_subgraph, new_triplets = new_triplets)
        # prompt = prompt_filter.format(ex_triplets = associated_subgraph, observation = observation, observations = observations[-1:])
        response = agent.generate(prompt)
        # predicted_outdated = parse_triplets(response)
        predicted_outdated = parse_triplets_removing(response)
        log("Outdated triplets: " + response)
        # outdated_edges = []
        # if step > 0:
        #     old_edges, new_edges = G_old.edges(data = True), G_new.edges(data = True)
        #     for edge in old_edges:
        #         if edge not in new_edges:
        #             outdated_edges.append(edge)
        #     log("Outdated triplets truth: " + str(outdated_edges))
        # n_truth += int(input("n_truth: "))
        # n += int(input("n: "))
        # recall += int(input("recall: "))
        # n_local, n_truth_local, recall_local = graph.compute_stats(predicted_outdated, outdated_edges, exclude_nav = True, locations=locations)
        # n_truth += n_truth_local
        # n += n_local
        # recall += recall_local
        
        graph.delete_triplets(predicted_outdated)
        graph.add_triplets(new_triplets_raw)
        
        n, n_truth, recall = graph.compare(graph_from_facts(info).edges(data = True), exclude_nav = True, locations=locations)
        # breakpoint()
        # prompt = prompt_extraction.format(observation = observation, observations = observations[-1:])
        # response = agent.generate(prompt)
        # triplets = process_triplets(response)
        # graph += triplets
        # graph = remove_equals(graph)
        # log("Observation: " + observation)
        # log("=====================")
        # log("Included triplets: " + response)
        # log("=====================")
        
        # prompt = prompt_filter_wrong.format(observation = observation, observations = observations[-1:], graph = graph)
        # response = agent.generate(prompt)
        # triplets = process_triplets(response)
        # for triplet in triplets:
        #     if triplet in graph:
        #         graph.remove(triplet)
        # log("Excluded wrong triplets: " + response)
        # log("=====================")
        
        # prompt = prompt_filter_outdated.format(observation = observation, observations = observations[-1:], graph = graph)
        # response = agent.generate(prompt)
        # triplets = process_triplets(response)
        # for triplet in triplets:
        #     if triplet in graph:
        #         graph.remove(triplet)
        # log("Excluded outdated triplets: " + response)
        # log("=====================")
        
        # prompt = prompt_goal.format(observation = observation, observations = observations[-1:], graph = graph)
        # response = agent.generate(prompt)
        # log("Goal at this step: " + response)
        # log("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        
        observations.append(observation)
        # G_old = graph_from_facts(info)
        if done: 
            break
        observation, reward, done, info = env.step(action)
        # G_new = graph_from_facts(info)
        # breakpoint()
        # old_edges, new_edges = G.edges(data = True), G_new.edges(data = True)
        # print(observation)
        # for edge in new_edges:
        #     if edge not in old_edges:
        #         print("New edge: ", edge)
        # for edge in old_edges:
        #     if edge not in new_edges:
        #         print("Outdated edge: ", edge)
        # print("=========================================")
        prev_action = action
        if n > 0:
            log("Precision: " + str(recall / n))
        if n_truth > 0:
            log("Recall:" + str(recall / n_truth))
        log("============================")


raise "error"


# Test goal + plan

graph = TripletGraph()
observations = []
# One for navigation
# walkthrough = ["examine Task note", "take Key 1", "go west", "go south", "go south", "unlock Grey locker with Key 1",
#                    "open Grey locker", "take Note 2 from Grey locker", "examine Note 2", "take Key 2 from Grey locker",
#                    "go north", "go east", "go east", "go north", "unlock Orange locker with Key 2", "open Orange locker",
#                    "take Golden key from Orange locker", "go south", "go west", "go west", "go north", "go east",
#                    "unlock Golden locker with Golden key", "open Golden locker", "take treasure from Golden locker", "END"]

# One for 2x2
# walkthrough = ['take book', 'go east', 'put book on the shelf', 'go west', 'take apple', 'go south', 'examine refrigerator', 'open refrigerator', 'put apple in refrigerator', 'take icecream', 'eat icecream', 'END']

# One for clean 3x3 default
walkthrough = ['take toothbrush', 'go north', 'take dumbbell', 'take dirty plate', 'go east', 'take raw meat', 'go south', 'take school notebooks', 'go south', 'take tv remote', 'take flippers', 'go west', 'take teddy bear', 'put flippers on equipment rack', 'go west', 'take fantasy book', 'put dumbbell on dumbbell stand', 'go north', 'take buisness suit', 'open refrigerator', 'put raw meat in refrigerator', 'close refrigerator', 'open dishwasher', 'put dirty plate in dishwasher', 'close dishwasher', 'go north', 'take sleeping mask', 'take dining chair', 'put toothbrush on bathroom sink', 'go east', 'open toy storage cabinet', 'put teddy bear in toy storage cabinet', 'close toy storage cabinet', 'put school notebooks on study table', 'go east', 'put tv remote on tv table', 'go south', 'open wardrobe', 'put buisness suit in wardrobe', 'close wardrobe', 'put sleeping mask on bedside table', 'go south', 'put fantasy book on bookcase', 'go west', 'go north', 'drop dining chair', 'END']

locations = {"player", "Kids' Room"}
env.reset()
for action in walkthrough:
    locations.add(env.curr_location)
    env.step(action)
print("LOCATIONS: ", locations)
n_steps = 20

for i in range(1):
    log("Attempt: " + str(i + 1))
    log("\n\n")
    observation, info = env.reset()
    G_new = graph_from_facts(info)
    # walkthrough = env.walkthrough()
    # walkthrough = env.get_walkthrough()
    prev_action = "start"
    goal = "Nothing"
    plan = "Nothing"
    n_truth, n, recall = 0, 0, 0
    done = False
    for step in range(n_steps):
        log("Step: " + str(step + 1))
        observation = observation.split("$$$")[-1]
        inventory = env.get_inventory()
        # inventory = [item.name for item in env.get_inventory()]
        observation += f"\nInventory: {inventory}"
        valid_actions = env.get_valid_actions()
        observation += f"\nValid actions (just recommendation): {valid_actions}"
        observation += f"\nAction that led to this: {prev_action}"
        log("Observation: " + observation)
        
        # observed_items, remembered_items = agent.bigraph_processing(observations, observation)
        # items = [list(item.keys())[0] for item in observed_items + remembered_items]
        # log("Crucial items: " + str(items))
        # associated_subgraph = graph.get_associated_triplets(items)
        associated_subgraph = graph.get_all_triplets()
        log("Associated subgraph: " + str(associated_subgraph))
        # breakpoint()
        new_triplets = graph.exclude(G_new.edges(data = True))
        prompt = prompt_goal.format(observation = observation, observations = observations[-1:], graph = graph, goal = goal, plan = plan)
        # prompt = prompt_refining.format(ex_triplets = associated_subgraph, new_triplets = new_triplets)
        # prompt = prompt_filter.format(ex_triplets = associated_subgraph, observation = observation, observations = observations[-1:])
        goal = agent.generate(prompt)
        log("Goal: " + goal)
        # prompt = prompt_planning.format(observation = observation, observations = observations[-1:], graph = graph, goal = goal, plan = plan)
        prompt = prompt_planning_without_obs.format(graph = graph, goal = goal, plan = plan)
        # predicted_outdated = parse_triplets(response)
        response = agent.generate(prompt)
        # predicted_outdated = parse_triplets_removing(response)
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
        # n_truth += int(input("n_truth: "))
        # n += int(input("n: "))
        # recall += int(input("recall: "))
        # n_local, n_truth_local, recall_local = graph.compute_stats(predicted_outdated, outdated_edges, exclude_nav = True, locations=locations)
        # n_truth += n_truth_local
        # n += n_local
        # recall += recall_local
        
        graph.delete_triplets(outdated_edges)
        graph.add_triplets(G_new.edges(data = True))
        # breakpoint()
        # prompt = prompt_extraction.format(observation = observation, observations = observations[-1:])
        # response = agent.generate(prompt)
        # triplets = process_triplets(response)
        # graph += triplets
        # graph = remove_equals(graph)
        # log("Observation: " + observation)
        # log("=====================")
        # log("Included triplets: " + response)
        # log("=====================")
        
        # prompt = prompt_filter_wrong.format(observation = observation, observations = observations[-1:], graph = graph)
        # response = agent.generate(prompt)
        # triplets = process_triplets(response)
        # for triplet in triplets:
        #     if triplet in graph:
        #         graph.remove(triplet)
        # log("Excluded wrong triplets: " + response)
        # log("=====================")
        
        # prompt = prompt_filter_outdated.format(observation = observation, observations = observations[-1:], graph = graph)
        # response = agent.generate(prompt)
        # triplets = process_triplets(response)
        # for triplet in triplets:
        #     if triplet in graph:
        #         graph.remove(triplet)
        # log("Excluded outdated triplets: " + response)
        # log("=====================")
        
        # prompt = prompt_goal.format(observation = observation, observations = observations[-1:], graph = graph)
        # response = agent.generate(prompt)
        # log("Goal at this step: " + response)
        # log("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        
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
        # if n > 0:
        #     log("Precision: " + str(recall / n))
        # if n_truth > 0:
        #     log("Recall:" + str(recall / n_truth))
        log("============================")

# print(agent.generate('''
# Ниже дан фрагмент необходимого эссе. Пожалуйста, напиши этот фрагмент более развернуто - добавь детали и подробности, разбей шаги на более мелкие.
# Дописывать эссе не нужно, сконцентрируйся на фрагменте и постарайся написать его как можно более интересно и подробно.
# ####
# Текст:
# ### План действий и разработка стратегии
# 1. Предварительное уведомление нарушителя. Первым шагом я решила написать официальное письмо в компанию-нарушителя с требованием удалить мой материал с их сайта и предложением добровольно урегулировать вопрос, чтобы избежать судебного разбирательства.
# 2. Составление и подача иска в суд. Если компания игнорировала бы мое требование, следующим шагом стала бы подача иска в суд о защите авторских прав, согласно статье 1252 Гражданского кодекса РФ.
# 3. Подготовка сопутствующих документов и доказательств. Значительную часть подготовки заняла бы сбор доказательств нарушения моих прав, включая скриншоты с сайта нарушителя, архив версий моего сайта (доказательство первичности моего авторства), а также экспертизы, подтверждающие идентичность текстов.
# 4. Защита в суде. В суде я бы аргументировала свои требования ссылками на статьи Гражданского кодекса, подтверждающие мои исключительные права на произведение, а также привела бы аналогичные прецеденты из судебной практики.'''))
# query = f'''
# Monday: You at a large hall. There is doors to north, east and west. You see iron chest, wooden chest, cat and a closet. You examine the iron chest. There is a
# combination lock. After several attemptions, you enter '4321', and a chest become opened. Here you see three shelfs. You open third shelf and find a prize. Congratulations!
# ####
# Tuesday: You at a large hall. There is doors to north, east and west. You see iron chest, wooden chest, cat and a closet. You examine the closet. There is a
# combination lock. After several attemptions, you enter '4321', and a closet become opened. Here you see three shelfs. You open third shelf and find a prize. Congratulations!
# ####
# Wednesday: You at a large hall. There is doors to north, east and west. You see iron chest, wooden chest, cat and a closet. You examine the closet. There is a
# combination lock. After several attemptions, you enter '4321', and a closet become opened. Here you see three shelfs. You open third shelf and find nothing. 
# ####
# Thursday: You at a large hall. There is doors to north, east and west. You see iron chest, wooden chest, cat and a closet. You say meow to cat. Cat say moew too.
# ####
# Valid actions (just recommendtion): ['examine iron chest', 'examine wooden chest', 'examine closet', 'north', 'east', 'west', 'say meow to cat', 'follow cat']
# ####
# Please, based on this information choose action to perform in the game. 
# Action:'''
# for i in range(10):
#     print(agent.generate(query, t = 1))

# for game_path, graph_path in paths.items(): 
#     env = TextWorldWrapper(game_path)
#     observation, info = env.reset()
#     # print(env.walkthrough())
#     # breakpoint()
#     graph = KnowledgeSemiBiGraph(graph_path, True)
#     G = graph_from_facts(info)
    # with open(graph_path + "/items.json", "r") as file:
    #     items = json.load(file)
    # print(graph_path, len(items))
    # draw_graph(G, game_path.split("/")[1] + ".pdf")


#     recall = 0
#     # for node in tqdm(G.nodes):
#     #     if agent.contain(node, list(items.keys()), False):
#     #         recall += 1
#     # print(graph_path, recall / len(G.nodes))
#     for edge in tqdm(G.edges):
#         embedding_1, embedding_2 = agent.get_embedding_local(edge[0]), agent.get_embedding_local(edge[1])
#         item_1, item_2 = graph.get_item(edge[0], embedding_1), graph.get_item(edge[1], embedding_2)
#         if item_1 is None or item_2 is None:
#             continue
#         for cand in item_1["factological_associations_items"]:
#             if cand == item_2["name"]:
#                 recall += 1
#                 break
#     print(graph_path, recall / len(G.edges))


# def planning(graph, agent, n_branches = 3, depth = 10):
#     branches = []
#     for it in range(n_branches):
#         print(f"Branch number {it + 1}")
#         current_state = graph.get_last_state()
#         branch = {
#             "actions": [],
#             "final": graph.get_string_state(current_state),
#             "experienced_states": [current_state],
#             "consequences": [graph.get_string_state(current_state)],
#             # "forbidden_actions": {}
#         }
#         for step in range(depth):
#             is_loop = False
#             associations, experienced_actions, n = graph.get_associations(state_key = current_state)
#             action = agent.get_action_planning(branches, branch, associations, experienced_actions, n, step)
#             print(current_state)
#             print(action)
#             contnue = int(input("Would yo like to continue: "))
#             if contnue == 0:
#                 raise "End"
#             current_state, is_unknown, graph_action = graph.get_next_step(action, current_state, agent.get_embedding_local(action), branch["consequences"])
#             current_state = graph.get_state_key(current_state, agent.get_embedding_local(current_state)) if current_state != "Unknown" else current_state
#             if current_state in branch["experienced_states"] and current_state != "Unknown":
#                 true_number = branch["experienced_states"].index(current_state) + 1
#                 is_loop = True
            
#             state_for_pred = graph.get_string_state(current_state) if current_state != "Unknown" else current_state
#             consequence = agent.get_predictions(branch, graph_action, state_for_pred, associations, experienced_actions, n)
#             consequence += f"\nAction that led to this: {graph_action}"
#             print("==========================")
#             print(consequence)
#             contnue = int(input("Would yo like to continue: "))
#             if contnue == 0:
#                 raise "End"
#             if is_unknown:
#                 branch["actions"].append(graph_action)
#                 branch["experienced_states"].append(current_state)
#                 branch["final"] = consequence
#                 branch["consequences"].append(consequence)
#                 break
#             branch["actions"].append(graph_action)
#             branch["final"] = consequence
#             branch["consequences"].append(consequence)
#             if is_loop:
#                 branch["actions"] = branch["actions"][:true_number]
#                 branch["experienced_states"] = branch["experienced_states"][:true_number]
#                 branch["consequences"] = branch["consequences"][:true_number]
#                 branch["final"] = branch["consequences"][true_number - 1]
#                 # branch["forbidden_actions"][true_number - 1] = forbidden_action
#         branches.append(branch)
#     return branches

# instructor = INSTRUCTOR('hkunlp/instructor-large')

# text = '''Room A'''

# # instruction = '''There is a description of game state. Pay attention to location and inventory. Location and inventory are the most crucial parameters.'''
# instruction = '''Represent the entiny in the knowledge graph'''
# embeddings = instructor.encode([[instruction, text]])
# embedding_1 =  list(map(float, list(embeddings[0])))

# text = '''Room B'''
# embeddings = instructor.encode([[instruction, text]])
# embedding_2 =  list(map(float, list(embeddings[0])))

# print(cosine(embedding_1, embedding_2))

# # env = FrotzEnv("z-machine-games-master/jericho-game-suite/detective.z5")
# # print(env.get_dictionary())

# graph_name = "Detective_bigraph_interactive"
# load = True
# graph = KnowledgeSemiBiGraph(graph_name, load)
# agent = GPTagent()

# # import json
# # with open("Detective_bigraph_walkthrough_test/states.json", "r") as file:
# #     states = json.load(file)
    
# # for state in states:
# #     for i in range(len(states[state]["explored_states"])):
# #         cons = states[state]["explored_states"][i]
# #         states[state]["explored_states"][i] = (cons[0], cons[1], cons[2], cons[3], 
# #                 graph.get_state_key(cons[1], agent.get_embedding_local(cons[1], True)))
# # with open("Detective_bigraph_walkthrough_gpt/states_new.json", "w") as file:
#     # json.dump(states, file)
        


# env = FrotzEnv("z-machine-games-master/jericho-game-suite/detective.z5")
# prev_action = None
# observation, info = env.reset()
# observations = []
# observations.append({"observation": observation, "trying": 9, "step": 0})
# done = False
# rewards, scores = [], []
# action = "start"
# steps_from_reflection = 0
# selected_branch, branches = 0, [{"actions": [], "consequences": []}]
# reflection = {"insight": "Still nothing", "trying": 9}
# n_steps = 200
# for step in range(n_steps):
#     old_obs = observation
#     inventory = [item.name for item in env.get_inventory()]
#     location = env.get_player_location().name
#     valid_actions = env.get_valid_actions()

#     observed_items, remembered_items = agent.bigraph_processing(observations, observation, location, 
#                     valid_actions, 9, step + 1)
#     state_key = f'''
# Observation: {observation}
# Location: {location}
# '''         
#     state_embedding = agent.get_embedding_local(state_key)
#     action_embedding = agent.get_embedding_local(action)
#     graph.add_state(observation, action, action_embedding, location, 9, step + 1, state_embedding)
#     graph.observe_items(observed_items, observation, location, state_embedding)
#     remembered_items.append({action: action_embedding})
#     graph.remember_items(remembered_items, observation, location, state_embedding)
#     # graph.save()

#     filtered_items = [graph.get_item(list(item.keys())[0], list(item.values())[0])["name"] for item in remembered_items if graph.get_item(list(item.keys())[0], list(item.values())[0]) is not None]
#     associations, experienced_actions, n = graph.get_associations(filtered_items)
#     # action, use_graph, is_random, insight = agent.choose_action(observations, observation, location, 
#     #                 valid_actions, trying, step, reflection,
#     #                 associations, experienced_actions, steps_from_reflection > -1, n, inventory)
#     # use_graph = use_graph or steps_from_reflection > 10
#     # if use_graph:
#     #     steps_from_reflection = 0
#     #     reflection = reflect(graph, agent, filtered_items)
#     #     reflection = {"insight": reflection, "trying": trying + 1, "step": step + 1}
#     #     action, is_random, insight = agent.choose_action_with_reflection(observations, observation, location, 
#     #                 valid_actions, trying, step,
#     #                 associations, experienced_actions, reflection, n, inventory)
#     # else:
#     #     steps_from_reflection += 1

#     state_key = graph.get_state_key(state_key, state_embedding)
#     need_plan = False
#     if len(branches[selected_branch]["actions"]) == 0:
#         need_plan = True
#     elif not (agent.is_equal(state_key, branches[selected_branch]["consequences"][0], graph.state_embeddin_treshold)):
#         need_plan = True

#     if need_plan:
#         branches = planning(graph, agent)
#         selected_branch = agent.select_branch(branches, observations, observation, location, 9, step + 1, inventory, associations, n)

#     insight = "Now insight is absent"
#     action = branches[selected_branch]["actions"][0]
#     branches[selected_branch]["actions"].pop(0)
#     branches[selected_branch]["consequences"].pop(0)

#     graph.add_insight(insight, observation, location, state_embedding)

#     state_key = f'''
# Observation: {observation}
# Location: {location}
# '''    
#     state_embedding = agent.get_embedding_local(state_key)
#     state_key = graph.get_state_key(state_key, state_embedding)
#     new_obs = graph.get_string_state(state_key) + f"\nAction that led to this: {prev_action}" if prev_action is not None else graph.get_string_state(state_key)
#     observations.append(new_obs)
    
#     # action = agent.choose_action_vanilla(observations, observation, inventory, location, valid_actions)

#     observation, reward, done, info = env.step(action)
#     inventory = [item.name for item in env.get_inventory()]
#     observation += f"\nInventory: {inventory}"
#     print("$$$$$$$$$$$$$$$$$$")
#     print("Really action: ", action)
#     print("Consequences:", observation)
#     print("$$$$$$$$$$$$$$$$$$$$$$$$")
#     prev_action = action
    
# import textworld.gym

# # Register a text-based game as a new environment.
# env_id = textworld.gym.register_game("z-machine-games-master/jericho-game-suite/anchor.z8",
#                                      max_episode_steps=50)

# env = textworld.gym.make(env_id)  # Start the environment.

# obs, infos = env.reset()  # Start new episode.
# env.render()

# score, moves, done = 0, 0, False
# while not done:
#     command = input("> ")
#     obs, score, done, infos = env.step(command)
#     env.render()
#     moves += 1

# env.close()
# print("moves: {}; score: {}".format(moves, score))

