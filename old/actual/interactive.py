import numpy as np
import seaborn
import json
import matplotlib.pyplot as plt

from graphs.contriever_graph import ContrieverGraph
from prompts import *
from prompts_v2 import *
from prompts_diff_agents import *
from utils import *

graph = ContrieverGraph("", "", None, None, 10)
items = np.array(["fried", "frying", "fry", "grilled", "grilling", "grill", "recipe", "dice", "diced", "dicing", "recipe #1"])
# items = np.array(["orange bell pepper", "green bell pepper", "red bell pepper"])
instruction = "Represent node in knowledge graph"
# items_emb = {item: graph.get_embedding(item) for item in items}
items_emb = {item: graph.get_emb(item) for item in items}
for item in items_emb:
    print("Item:", item)
    scores = [np.dot(items_emb[item], value) / (np.linalg.norm(items_emb[item]) * np.linalg.norm(value))  for value in items_emb.values()]
    best_idx = np.argsort(scores)
    for i in reversed(best_idx):
        print(items[i] + ":", scores[i])
    print("===" * 4)


# graph = ContrieverGraph("", "", None, None, 10)
# graph_test = {
#         'items': ['toothbrush', 'dirty plate', 'fantasy book'],
#         'graph': ['dining room, contains, dining table', 'dining table, has on, toothbrush',
#                   'dining table, has on, centerpiece', 'dining table, has on, candles',
#                   'dining table, has on, salt and pepper shakers', 'dining room, has exit, east',
#                   'dining room, has exit, north', 'dining room, has exit, south', 'dining room, has exit, west',
#                   'kitchen, contains, dishwasher', 'kitchen, contains, refrigerator', 'kitchen, contains, cook table',
#                   'dishwasher, is, closed', 'refrigerator, is, closed', 'cook table, has on, business suit',
#                   'kitchen, has exit, east', 'kitchen, has exit, north', 'kitchen, has exit, south',
#                   'kitchen, is west of, dining room', 'dining room, is east of, kitchen', 'bathroom, contains, toilet',
#                   'toilet, has on, toilet paper', 'toilet paper, is on, toilet', 'toilet, has on, sleeping lamp',
#                   'sleeping lamp, is on, toilet', 'bathroom, contains, sink', 'sink, has on, deodorant',
#                   'deodorant, is on, sink', 'bathroom, contains, towel rack', 'towel rack, is, empty',
#                   'bathroom, has exit, east', 'bathroom, has exit, south', 'bathroom, contains, table runner',
#                   'table runner, is on, floor', 'bathroom, is north of, kitchen', 'kitchen, is south of, bathroom',
#                   'kids room, contains, toy storage cabinet', 'kids room, contains, study table',
#                   'kids room, contains, kids bed', 'study table, has on, school notebooks',
#                   'study table, has on, felt tip pens', 'study table, has on, dumbbell',
#                   'kids bed, has on, dirty plate', 'kids room, has exit, east', 'kids room, has exit, south',
#                   'kids room, has exit, west', 'kids room, is east of, bathroom', 'bathroom, is west of, kids room',
#                   'living room, contains, tv table', 'tv table, has on, tv', 'living room, contains, sofa',
#                   'sofa, has on, raw meat', 'sofa, has on, decorative pillow',
#                   'living room, contains, game console cabinet', 'game console cabinet, has in, gaming console',
#                   'living room, has exit, south', 'living room, has exit, west', 'living room, is east of, kids room',
#                   'kids room, is west of, living room', 'master bedroom, contains, wardrobe',
#                   'master bedroom, contains, king size bed', 'king size bed, has on, wet towel',
#                   'master bedroom, contains, bedside table', 'bedside table, has on, alarm clock',
#                   'bedside table, has on, bed lamp', 'master bedroom, has exit, north',
#                   'master bedroom, has exit, south', 'master bedroom, has exit, west',
#                   'master bedroom, is south of, living room', 'living room, is north of, master bedroom',
#                   'library, has odor, bad odor', 'library, contains, bookcase', 'bookcase, has on, detective book',
#                   'library, contains, reading table', 'reading table, has on, swimming fins',
#                   'reading table, has on, reading glasses', 'library, has exit, north', 'library, has exit, west',
#                   'library, is south of, master bedroom', 'master bedroom, is north of, library',
#                   'swimming pool area, contains, pool equipment rack',
#                   'swimming pool area, contains, table for pool chemicals', 'swimming pool area, contains, toy car',
#                   'swimming pool area, has exit, east', 'swimming pool area, has exit, north',
#                   'swimming pool area, has exit, west', 'pool equipment rack, has on, swimming goggles',
#                   'pool equipment rack, has on, life ring', 'table for pool chemicals, has on, chlorine',
#                   'toy car, is on, floor', 'swimming pool area, is west of, library',
#                   'library, is east of, swimming pool area', 'gym, contains, sport equipment locker',
#                   'gym, contains, empty dumbbell stand', 'gym, contains, empty treadmill', 'fantasy book, is on, floor',
#                   'gym, has exit, east', 'gym, has exit, north', 'gym, is west of, swimming pool area',
#                   'swimming pool area, is east of, gym']
#     }

# # This part form graph from list of triplets in str form
# # triplets = [triplet ([subject (str), object (str), {"label": relation (str)}])]
# triplets = []
# for triplet in graph_test["graph"]:
#     temp = triplet.split(", ")
#     triplets.append([temp[0], temp[2], {"label": temp[1]}])
# graph.add_triplets(triplets)
# print("Number of triplets:", len(graph.triplets))
# print("Number of items:", len(graph.items_emb))

# # Compute matrix of items similarity (same for triplet)
# # items_emb = {item_name (str): item_emb (np.array)}
# # triplets_emb = {triplet_str (str): triplet_emb (np.array)}
# matrix = np.array([ 
#             [np.dot(embedding_item1, embedding_item2) for embedding_item1 in graph.items_emb.values()]  
#                 for embedding_item2 in graph.items_emb.values() 
#         ])
# print("\n\n\nMATRIX OF SIMILARITY BETWEEN ITEMS")
# print(matrix)
# print(graph.items_emb.keys())

# # Compute new embedding
# text = "Have a nice day"
# print("\n\n\nNEW EMBEDDING")
# print(text + ":", graph.retriever.embed([text])[0].cpu().detach().numpy())

# graph.expand_graph(0.9, True)
# descr = """-= Kitchen =-
# You've just sauntered into a Kitchen.

# You can make out an opened dishwasher here. What a letdown! The dishwasher is empty! You make out an opened refrigerator in the corner. The refrigerator contains a milk and a cheese. Wow, isn't TextWorld just the best? You can see a cook table! The cook table appears to be empty. Hm. Oh well

# There is an unblocked exit to the east. There is an exit to the north. Don't worry, it is unguarded. You need an unguarded exit? You should try going south.
# Your plan: {
#   "main_goal": "You are at large house and your goal is to clean up it. Namely, you should find items that are out of place and return them to their place",
#   "plan_steps": [
#     {
#       "sub_goal_1": "Find the correct place for the fantasy book",
#       "reason": "The fantasy book is still out of place, and a suitable location for it needs to be found, likely a library, study, or a bedroom with a reading nook."
#     },
#     {
#       "sub_goal_2": "Explore the house to identify other misplaced items",
#       "reason": "To ensure the house is thoroughly cleaned, continue exploring to find and reposition any additional items that are not in their proper place."
#     },
#     {
#       "sub_goal_3": "Avoid revisiting previously explored locations",
#       "reason": "Maintaining efficiency in the cleaning process requires exploring new areas while avoiding areas that have already been inspected."
#     },
#     {
#       "sub_goal_4": "Choose a new direction to explore from the kitchen",
#       "reason": "Given the current location in the kitchen and its exits leading east and the option to go south, selecting a direction that potentially leads to unexplored areas is crucial for discovering new locations to find a place for the fantasy book and other items."
#     }
#   ]
# }"""
# print(graph.find_items(["toothbrush", "fantasy book"]))
# print(graph.A_star("toothbrush", "fantasy book", descr))
# breakpoint()
# associated_graph, history = graph.reasoning(graph_test["items"])
# best_idx = np.argsort(history[-1])[-10:]
# history = np.transpose(np.array(history))
# assert history.shape[0] == len(graph.triplets)
# f = plt.figure(figsize = (20, 20))
# for i in best_idx:
#     plt.plot(history[i], label = graph.str(graph.triplets[i]), figure = f)
# plt.legend()
# plt.savefig("importances.pdf")
# print(associated_graph)
# exp_name = "exp_retrieve_1_1"
# with open("KG/files/items.json") as f:
#     itemss = json.load(f)
# with open("KG/files/obs.json") as f:
#     obss = json.load(f)
# with open("KG/files/graph.json") as f:
#     graphs = json.load(f)
# with open("KG/files/plans.json") as f:
#     plans = json.load(f)
    
# for name in ["heuristic"]:
#     graph = ContrieverGraph(model = "gpt-4-0125-preview", system_prompt = system_prompt, depth = 150, threshold = None, topk = 5)
#     log = Logger(exp_name + "_" + name)

#     assert len(itemss) == len(obss) and len(itemss) == len(plans) and len(itemss) == len(graphs)
#     step = 0
#     for items, obs, plan, graph_ in zip(itemss, obss, plans, graphs):
#         step += 1
#         log("Step: " + str(step))
#         graph.triplets = []
#         graph.triplets_emb = {}
#         graph.items_emb = {}
#         triplets = []
#         for triplet in graph_:
#             temp = triplet.split(", ")
#             triplets.append([temp[0], temp[2], {"label": temp[1]}])
#         graph.add_triplets(triplets)
#         graph.expand_graph(1.1, True)
#         log("Observation: " + obs)
#         log("Items: " + str(items))
#         log("Plan: " + str(plan))
        
#         if name == "bfs":
#             subgraph = graph.get_associated_triplets(items, steps = 2)
        
#         if name == "beamsearch":
#             subgraph = graph.beam_search_on_triplets(items, obs, plan, set(), depth = 5, width = 5, log = log)
        
#         if name == "heuristic":
#             subgraph = graph.heuristic_connections(obs, plan, items)
#         log("\n<<EXTRACTED SUBGRAPH>>\n" + str(subgraph))
#         log("===" * 25)
    
