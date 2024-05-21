import json
import networkx as nx
import numpy as np
import torch

from contriever import Retriever
from collections import deque


def edge(text):
    return [e.strip() for e in text.split(",")]


def build_graph(triplets):
    G = nx.Graph()
    for t in triplets:
        src, e, trg =  edge(t)
        G.add_edge(src, trg, relation=e)

    return G


def add_similar(G, src, visited, query, dist, retriever, threshold=1.5):
    result = retriever.search(
        list(G.nodes),
        src,
        similarity_threshold=threshold,
        return_scores=True
    )
    similar = [s for s in result['strings'] if s not in visited]
    visited.update(similar)
    query.extend(similar)
    for s in similar:
        dist[s] = dist[src]

@torch.no_grad()
def claster(nodes, retriever: Retriever):
    curr_nodes = nodes
    print('Initial nodes:\n', " | ".join(curr_nodes), sep="")
    np.set_printoptions(precision=3)
    while True:
        print('=========================')
        embeds = retriever.embed(curr_nodes)
        scores = embeds @ embeds.T
        scores.fill_diagonal_(-1.)
        scores = scores.numpy()
        mmax = scores.max()
        if mmax <= 1.:
            break
        #print(f'Scores ({pair_scores.shape}):\n', pair_scores)
        x,y = np.unravel_index(scores.argmax(), scores.shape)
        combo_node = ", ".join([curr_nodes[x], curr_nodes[y]])
        print(f"Join [{curr_nodes[x]}] and [{curr_nodes[y]}], with similarity score={mmax:.3f}")
        curr_nodes = [n for i, n in enumerate(curr_nodes) if i not in (x, y)]
        curr_nodes.append(combo_node)
        #print("New nodes:\n", " | ".join(curr_nodes), sep="")

    print("Final nodes:\n", "\n".join(curr_nodes), sep="")

def graph_retr_search(
        start_query,
        triplets,
        retriever: Retriever,
        max_depth :int=2,
        topk :int=3,
        post_retrieve_threshold: float=0.7, #not exclusive with topk here
        verbose=2,
):

    queue = deque()
    queue.append(start_query)
    d = {start_query:0}

    result = []

    while queue:
        q = queue.popleft()
        if d[q] >= max_depth: continue

        #if verbose> 1: print(f"Search: {q}, dist={d[q]}")

        res = retriever.search(triplets, q, topk=topk, return_scores=True)
        for s, score in zip(res['strings'], res['scores']):
            if score < post_retrieve_threshold: continue
            v1, e, v2 = edge(s)
            for v in [v1, v2]:
                if v not in d:
                    queue.append(v)
                    d[v] = d[q] + 1
            if s not in result:
                #if verbose > 0: print(f'   [sim={score:.2f}]: {s}')
                result.append(s)

    return result

def get_graph7_triplets():
    import pickle
    from graphs.contriever_graph import ContrieverGraph

    graph = ContrieverGraph(model='gpt-4-turbo', system_prompt='', depth='1')

    with open('../graph_search/graph7.pkl', 'rb') as input_file:
        loaded_objects = pickle.load(input_file)

    graph_load = loaded_objects[0]
    graph.triplets = graph_load.triplets
    triplets = graph.triplets_to_str(graph.triplets)
    triplets = [tr for tr in  triplets if "associated with" not in tr]
    return triplets
    #graph.items_emb = graph_load.items_emb

def eval_triplets(triplets):
    reference_full = [
        'recipe #1, instructs, prepare meal',
        'recipe #1, requires, orange bell pepper',
        'orange bell pepper, to be, diced', 'orange bell pepper, to be, grilled', 'bbq, used for, grilling',
        'fridge, contains, orange bell pepper', 'kitchen, contains, fridge',
        'recipe #1, requires, green bell pepper', 'green bell pepper, to be, diced', 'green bell pepper, to be, fried',
        'stove, used for, frying', 'green bell pepper, is in, garden',
        'recipe #1, requires, yellow potato', 'yellow potato, to be, sliced', 'yellow potato, to be, grilled',
        'bbq, used for, grilling', 'yellow potato, is in, garden'
    ]
    is_found = [int(r in triplets) for r in reference_full]
    print(f"Found {sum(is_found)}/{len(is_found)} from reference_full")

if __name__ == "__main__":

    """
    with open("../graph_search/items.json") as f:
        items = json.load(f)

    with open("../graph_search/graph.json") as f:
        graphs = json.load(f)

    with open("../graph_search/obs.json") as f:
        obs = json.load(f)

    with open("../graph_search/plans.json") as f:
        plans = json.load(f)
        plans = [json.loads(p) for p in plans]

    """

    #triplets = get_graph7_triplets()
    #triplets = graphs[22] # old tests
    triplets = ['living room, has exit, east', 'living room, has exit, south', 'sofa, is in, living room', 'stove, used for, frying', 'oven, used for, roasting', 'bbq, used for, grilling', 'meal, to be prepared in, kitchen', 'kitchen, contains, fridge', 'fridge, contains, red bell pepper', 'fridge, contains, raw white tuna', 'kitchen, contains, oven', 'kitchen, contains, table', 'kitchen, contains, counter', 'kitchen, contains, stove', 'kitchen, has exit, south', 'kitchen, has exit, east', 'kitchen, has exit, north', 'kitchen, is south of, living room', 'living room, is north of, kitchen', 'cookbook, is in, inventory', 'cooking: a modern approach (3rd ed), contains, recipe', 'recipe, requires, green bell pepper', 'recipe, requires, orange bell pepper', 'recipe, requires, yellow potato', 'green bell pepper, to be, diced', 'green bell pepper, to be, fried', 'orange bell pepper, to be, diced', 'orange bell pepper, to be, grilled', 'yellow potato, to be, sliced', 'yellow potato, to be, grilled', 'recipe, instructs to, prepare meal', 'orange bell pepper, is in, inventory', 'corridor, has exit, east', 'corridor, has exit, north', 'corridor, has exit, south', 'corridor, has exit, west', 'corridor, is east of, kitchen', 'kitchen, is west of, corridor', 'bathroom, has exit, north', 'bathroom, contains, toilet', 'bathroom, is south of, corridor', 'corridor, is north of, bathroom', 'pantry, has exit, north', 'shelf, is made of, wood', 'shelf, has on it, nothing', 'pantry, is south of, kitchen', 'kitchen, is north of, pantry', 'backyard, has exit, east', 'backyard, has exit, west', 'backyard, has exit, north', 'backyard, contains, patio table', 'patio table, is empty, true', 'backyard, contains, patio chair', 'patio chair, is stylish, true', 'patio chair, is empty, true', 'backyard, contains, bbq', 'backyard, is east of, corridor', 'corridor, is west of, backyard', 'orange bell pepper, has been, grilled', 'shed, contains, toolbox', 'shed, contains, workbench', 'wall, opens up to reveal, toolbox', 'toolbox, is empty, true', 'workbench, is empty, true', 'shed, has exit, west', 'shed, is east of, backyard', 'backyard, is west of, shed', 'garden, has exit, south', 'green hot pepper, is on, floor', 'red hot pepper, is on, floor', 'yellow apple, is on, floor', 'purple potato, is on, floor', 'red onion, is on, floor', 'garden, is north of, backyard', 'backyard, is south of, garden', 'green bell pepper, is in, inventory', 'yellow potato, is in, inventory', 'counter, is, vast', 'stove, is, conventional', 'green bell pepper, has been, fried', 'score, has gone up, one point', 'knife, is in, inventory', 'yellow potato, has been, sliced']
    retriever = Retriever(model_name="facebook/contriever")
    #print('items:', items[22])
    #query = items[22][-1]
    #print(f"QUERY: {query}")
    #queries = ['green bell pepper',  'stove', 'bbq', 'recipe'] #items[22][-5:]:
    queries = ['green bell pepper', 'orange bell pepper', 'yellow potato', 'recipe']
    #queries = ['Prepare the ingredients as per the recipe.', 'Cook the meal using the appropriate kitchen appliance.']#items[22][-5:]:
    total_results = set()
    for query in queries: #items[22][-5:]:
        print(f"QUERY: {query}")
        results = graph_retr_search(
            query, triplets, retriever, max_depth=1,
            topk=15,
            post_retrieve_threshold=0.7, # for base contriever
            verbose=2
        )
        total_results.update(results)
        print(f'triplets total: {len(results)}')
        print("#######################################\n")

    print(f"ALL TRIPLETS\n Queries: {queries}")
    eval_triplets(total_results)
    print(f'Retrieved total of {len(total_results)} triplets.')
    print("Triplets (sorted): ")
    for s in sorted(total_results):
        print(s)
    # #query = ", ".join(items[22])
    # for t in graphs[22]:
    #     print(t)
    # G = build_graph(triplets)
    # print('Data about yellow potato in the graph:')
    # print(G['yellow potato'])

    #for v in G.nodes:
    #     print(v)
    # graph = [
    #     'dice', 'diced',
    #     "roast", 'roasted',
    #     'grilled', 'grill', 'grilling',
    #     'fried', 'frying', 'fry',
    # ]
    # claster(list(G.nodes), retriever)
    #result = retriever.search(graph, query, topk=9, return_scores=True)

    # result = retriever.search(obs, "cookbook", topk=2, return_scores=True)
    # for (s, score) in zip(result['strings'], result['scores']):
    #      print("=="*15)
    #      print(f"score={score:.2f}\n, nodes={s}")
         #print({for k,v in G[s].items()})
         # print(f"#{i}: triplet={edge(s)}")
         # print(f"#{i} [{result['scores'][i]:.3f}] :",  s)

    # print(f"Plans{type(plans[22])} at step 22:", plans[22]['plan_steps'])
    # for step, p in enumerate(plans[22:23]):
    #     print(f"======== TIME#{step} =========")
    #     for i, e in enumerate(p["plan_steps"]):
    #         print(f"STEP#{i}")
    #         for k,v in e.items():
    #             print(f"{k}: {v}")

    # queries = ['diced', 'fried', 'recipe']
    # result = retriever.search(graphs[22], queries, similarity_threshold=1., return_scores=True)
    #
    # for i, query in enumerate(queries):
    #     print('==='*15)
    #     print(f"#{i} SEARCH FOR ITEM: {query}")
    #     print("RESULTS:")
    #     for triplet, similarity in zip(result['strings'][i], result['scores'][i]):
    #         print(f"{similarity:.3f}: {triplet}")
    # print("\n\n\n")