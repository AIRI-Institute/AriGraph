import numpy as np
import networkx as nx
import textworld as tw
import textworld.gym as tw_gym
import matplotlib.pyplot as plt

from graphs.parent_graph import clear_triplet

class TextWorldWrapper:

    def __init__(self, gamefile):
        super().__init__()
        self.gamepath = gamefile
        self.request_infos = tw.EnvInfos(
            admissible_commands=True,  # All commands relevant to the current state.
            entities=True,  # List of all interactable entities found in the game.
            facts=True,
            feedback=True,
            max_score=True,
            inventory=True,
            location=True,
            policy_commands = True

        )
        self.score = 0.
        self.env = None
        self.curr_info = None
        self.curr_location = None
        self.curr_obs = None

    def reset(self, new_gamefile=None):
        if new_gamefile is not None or self.env is None:
            env_id = tw_gym.register_game(self.gamepath, self.request_infos, max_episode_steps = 100000000)
            self.env = tw_gym.make(env_id)

        obs, infos = self.env.reset()
        self._update(obs, infos)
        self.score = 0.
        infos['score'] = self.score
        return obs, infos

    def step(self, action):
        obs, new_score, done, infos = self.env.step(action)
        self._update(obs, infos)
        reward = new_score - self.score
        self.score = new_score
        infos['score'] = self.score
        return obs, reward, done, infos

    def get_inventory(self):
        return self.curr_info['inventory']
    
    def walkthrough(self):
        return self.curr_info['policy_commands']

    def _update(self, obs, infos):
        self.curr_info = infos
        self.curr_obs = obs
        if "-=" in self.curr_obs and "=-" in self.curr_obs:
            self.curr_location = self.curr_obs.split("-=")[-1].split("=-")[0].strip(" \n'")

    def get_player_location(self):
        return self.curr_location

    def get_max_score(self):
        return self.curr_info['max_score']

    def get_valid_actions(self):
        return self.curr_info['admissible_commands']
    
    def expand_action_space(self):
        new_actions = set()
        need_expand = all(["take" not in action for action in self.curr_info['admissible_commands']])
        needful_facts = [fact for fact in self.curr_info['facts'] if len(fact.arguments) > 1]
        can_be_taked = {obj.arguments[0].name for obj in needful_facts if obj.arguments[0].type == 'f' and obj.arguments[1].name.lower() == self.curr_location.lower()}         
        if need_expand:
            for entity in self.curr_info['entities']:
                if entity in can_be_taked:
                    new_actions.add(f"take {entity}")
        return list(new_actions)
                    
            


def graph_from_facts(info, only_entities=False, verbose=False, need_tags = True):
    G = nx.MultiDiGraph()
    objects = info['entities']
    for f in info['facts']:
        if len(f.arguments) == 1 and need_tags:
            edge = f.name
            a, b = f.arguments[0].name, "itself"
            
        elif len(f.arguments) == 2:
            edge = f.name
            a, b = f.arguments[0].name, f.arguments[1].name
            
        else:
            continue

        if only_entities and (a not in objects or b not in objects):
            continue

        if verbose:
            print(f"add edge ({a}, {edge}, {b})")
        G.add_edge(a, b, label=edge)

    return G

def draw_graph(G, path = "default"):
    pos = nx.spring_layout(G, seed=1, k=0.15)
    labels = nx.get_edge_attributes(G, 'label')
    fig = plt.figure(figsize=(12, 10))
    nx.draw(G, pos, with_labels=True, font_size=10, node_size=700, node_color='lightblue', edge_color='gray', alpha=0.6)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=8, label_pos=0.3, verticalalignment='baseline')
    plt.title('Knowledge Graph')
    plt.savefig(path)
    
def get_text_graph(G):
    graph_text = ""
    for edge in G.edges(data = True):
        clear_edge = clear_triplet(edge)
        graph_text += f'''\n{clear_edge[0]} {clear_edge[2]["label"]} {clear_edge[1]},'''
    return graph_text
