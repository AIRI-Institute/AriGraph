import pickle
from graphs.contriever_graph import ContrieverGraph

graph = ContrieverGraph(model='gpt-4-turbo', system_prompt='', depth='1')

with open('/trinity/home/n.semenov/KG/actual/graph7.pkl', 'rb') as input_file:
    loaded_objects = pickle.load(input_file)

graph_load = loaded_objects[0]
 
graph.triplets = graph_load.triplets
graph.items_emb = graph_load.items_emb

print(graph.find_items('green bell pepper'))
#associated_subgraph = graph1.get_associated_triplets(graph1.find_items(['recipe #1']), steps = 2) 
associated_subgraph = graph.get_associated_triplets(['recipe #1'], steps = 2) 

print(associated_subgraph)