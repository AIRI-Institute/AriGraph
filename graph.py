import os
import json
import numpy as np
from copy import deepcopy
from scipy.spatial.distance import cosine

def merge_dicts(primal_dict, side_dict):
    keys = set(list(primal_dict.keys()) + list(side_dict.keys()))
    merged_dict = {}
    for key in keys:
        if key in primal_dict:
            merged_dict[key] = primal_dict[key]
        else:
            merged_dict[key] = side_dict[key]
    return merged_dict

class KnowledgeGraph:
    def __init__(self, path, load = False):
        os.makedirs(path, exist_ok=True)
        self.path = path
        self.triplets, self.nodes = [], {}
        self.metainf = {}
        if load:
            with open(path + "/triplets.json", "r") as file:
                self.triplets = json.load(file)
            with open(path + "/nodes.json", "r") as file:
                self.nodes = json.load(file)
            with open(path + "/metainf.json", "r") as file:
                self.metainf = json.load(file)
        self.create_maps()

    def create_maps(self):
        self.subj_map, self.obj_map = {}, {}
        for node in self.nodes.values():
            self.subj_map[node["name"]], self.obj_map[node["name"]] = [], []
            for triplet in self.triplets:
                if triplet[0]["name"] == node["name"]:
                    self.subj_map[node["name"]].append(triplet)
                if triplet[2]["name"] == node["name"]:
                    self.obj_map[node["name"]].append(triplet)

    def __len__(self):
        return len(self.nodes)
    
    def save(self):
        with open(self.path + "/triplets.json", "w") as file:
            json.dump(self.triplets, file)
        with open(self.path + "/nodes.json", "w") as file:
            json.dump(self.nodes, file)
        with open(self.path + "/metainf.json", "w") as file:
            json.dump(self.metainf, file)

    def add_node(self, node):
        node = deepcopy(node)
        add = np.all([node["name"] != node_["name"] for node_ in self.nodes.values()])
        if add:
            self.subj_map[node["name"]], self.obj_map[node["name"]] = [], []
            self.nodes[node["name"]] = node
        else:
            self.change_node(node)

    def add_triplet(self, triplet):
        assert len(triplet) == 3
        triplet = deepcopy(triplet)
        self.add_node(triplet[0])
        self.add_node(triplet[2])
        add = np.all([trplt[1]["name"] != triplet[1]["name"] \
                        or trplt[0]["name"] != triplet[0]["name"] \
                        or trplt[2]["name"] != triplet[2]["name"] for trplt in self.subj_map[triplet[0]["name"]]])
        if add:
            self.triplets.append(triplet)
            self.subj_map[triplet[0]["name"]].append(triplet)
            self.obj_map[triplet[2]["name"]].append(triplet)
        else:
            self.change_triplet(triplet)

    def get_node(self, name):
        if name not in self.nodes:
            return None
        return deepcopy(self.nodes[name])
    
    def get_triplet(self, subj_name, relation, obj_name):
        exist = False
        for i, triplet in enumerate(self.triplets):
            if triplet[1]["name"] == relation and triplet[2]["name"] == obj_name and triplet[0]["name"] == subj_name:
                exist = True
                idx = i
        if not exist:
            return None
        subj = self.nodes[self.triplets[idx][0]["name"]]
        relation = self.triplets[idx][1]
        obj = self.nodes[self.triplets[idx][2]["name"]]
        return deepcopy([subj, relation, obj])

    def change_node(self, new_node):
        new_node = deepcopy(new_node)
        if new_node["name"] not in self.nodes:
            return False
        self.nodes[new_node["name"]] = merge_dicts(new_node, self.nodes[new_node["name"]])
        return True
    
    def change_triplet(self, new_triplet):
        new_triplet = deepcopy(new_triplet)
        exist = False
        for i, triplet in enumerate(self.triplets):
            if triplet[1]["name"] == new_triplet[1]["name"] and triplet[2]["name"] == new_triplet[2]["name"] and triplet[0]["name"] == new_triplet[0]["name"]:
                exist = True
                idx = i
        if not exist:
            return False
        relation = merge_dicts(new_triplet[1], self.triplets[idx][1])
        self.triplets[idx][1] = relation
        for i in range(len(self.obj_map[new_triplet[0]["name"]])):
            if self.obj_map[new_triplet[0]["name"]][i][1]["name"] == relation["name"]:
                self.obj_map[new_triplet[0]["name"]][i][1] = relation
        for i in range(len(self.subj_map[new_triplet[2]["name"]])):
            if self.subj_map[new_triplet[2]["name"]][i][1]["name"] == relation["name"]:
                self.subj_map[new_triplet[2]["name"]][i][1] = relation
        return True

    def PersonalizedArticleRang(self, source_nodes_names, maxIters = None, eps = 1e-3, damping = 1):
        maxIters = len(self.nodes) if maxIters is None else maxIters
        degree = 0
        for node in self.nodes.values():
            node["ArticleRangScorePrev"] = 1 if node["name"] in source_nodes_names else 0
            degree += (len(self.subj_map[node["name"]]) + len(self.obj_map[node["name"]])) / len(self.nodes)
        for it in range(maxIters):
            delta = 0
            for node in self.nodes.values():
                summ = 0
                for incoming in self.subj_map[node["name"]]:
                    n_outcomings = len(self.subj_map[incoming[2]["name"]]) + len(self.obj_map[incoming[2]["name"]])
                    summ += self.nodes[incoming[2]["name"]]["ArticleRangScorePrev"] / n_outcomings
                for incoming in self.obj_map[node["name"]]:
                    n_outcomings = len(self.subj_map[incoming[2]["name"]]) + len(self.obj_map[incoming[2]["name"]])
                    summ += self.nodes[incoming[2]["name"]]["ArticleRangScorePrev"] / n_outcomings
                node["ArticleRangScore"] = (1 - damping) + damping * summ
            for node in self.nodes.values():
                delta = max(delta, np.abs(node["ArticleRangScore"] - node["ArticleRangScorePrev"]))
                node["ArticleRangScorePrev"] = node["ArticleRangScore"]

            if delta < eps:
                break
        
        summ = np.sum([node["ArticleRangScore"] for node in self.nodes.values()])
        return {node["name"]: node["ArticleRangScore"] / (summ + 1e-9) for node in self.nodes.values()}
    
    def choose_source_nodes(self, source_embeddings):
        source_nodes_names = set()
        for embedding in source_embeddings:
            try:
                idx = np.argmin([cosine(embedding, node["embedding"]) for node in self.nodes.values()])
            except:
                print(np.array(embedding).shape)
                print([np.array(node["embedding"]).shape for node in self.nodes.values()])
                raise "anything"
            source_nodes_names.add([node["name"] for node in self.nodes.values()][idx])
        return source_nodes_names

    def get_triplets(self, source_embeddings, K, M = 100000000, maxIters = None, eps = 1e-3, damping = 1):
        source_nodes_names = self.choose_source_nodes(source_embeddings)
        scores_ = self.PersonalizedArticleRang(source_nodes_names, maxIters, eps, damping)
        scores = list(reversed(sorted([(score, name) for name, score in scores_.items()])))[:K]
        scores = list(set(([(scores_[name], name) for name in source_nodes_names] + scores)))[:K]
        target_names = {score[1] for score in scores}

        triplets = []
        triplet_scores = []
        for triplet in self.triplets:
            if triplet[0]["name"] in target_names and triplet[2]["name"] in target_names:
                triplet_scores.append(scores_[triplet[0]["name"]] + scores_[triplet[2]["name"]])
                triplets.append(self.get_triplet(triplet[0]["name"], triplet[1]["name"], triplet[2]["name"]))
        idx = list(reversed(np.argsort(triplet_scores)))[:M]
        return list(np.array(triplets)[idx])