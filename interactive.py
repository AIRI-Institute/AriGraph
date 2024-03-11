from InstructorEmbedding import INSTRUCTOR
from scipy.spatial.distance import cosine
from jericho import FrotzEnv
import json
from tqdm.auto import tqdm

from agent_detective import GPTagent
from graph import KnowledgeGraph
from semi_bigraph import KnowledgeSemiBiGraph
from textworld_adapter import TextWorldWrapper, graph_from_facts, get_text_graph, draw_graph

paths = {
    "benchmark/recipe3_cook_cut/tw-cooking-recipe3+take3+cook+cut+drop+go1-7yGrcV9pTE8DF75n.z8": "Recipe_3_cook_cut",
    "benchmark/take2_go9/tw-cooking-recipe2+take2+go9-Q9nDu630U5j3tqBG.z8": "Take2_go9",
    "benchmark/navigation4/navigation4.z8": "Navigation4",
    "benchmark/navigation2/navigation2.z8": "Navigation2",
}
# agent = GPTagent(model = "gpt-4-0125-preview")
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

instructor = INSTRUCTOR('hkunlp/instructor-large')

text = '''Room A'''

# instruction = '''There is a description of game state. Pay attention to location and inventory. Location and inventory are the most crucial parameters.'''
instruction = '''Represent the entiny in the knowledge graph'''
embeddings = instructor.encode([[instruction, text]])
embedding_1 =  list(map(float, list(embeddings[0])))

text = '''Room B'''
embeddings = instructor.encode([[instruction, text]])
embedding_2 =  list(map(float, list(embeddings[0])))

print(cosine(embedding_1, embedding_2))

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

