import textworld as tw
import textworld.gym as tw_gym
import networkx as nx
import matplotlib.pyplot as plt
import re
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
            env_id = tw_gym.register_game(self.gamepath, self.request_infos)
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
        # loc_result = re.search(r'-= (\D+) =-', self.curr_obs)
        # breakpoint()
        # if loc_result:
        #     self.curr_location = loc_result.group(1)
        if "-=" in self.curr_obs and "=-" in self.curr_obs:
            self.curr_location = self.curr_obs.split("-=")[-1].split("=-")[0].strip(" \n'")

    def get_player_location(self):
        return self.curr_location

    def get_max_score(self):
        return self.curr_info['max_score']

    def get_valid_actions(self):
        return self.curr_info['admissible_commands']


def graph_from_facts(info, only_entities=False, verbose=False, need_tags = True):
    G = nx.DiGraph()
    objects = info['entities']
    # print(info['facts'])
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
    # pos = nx.planar_layout(G, )
    labels = nx.get_edge_attributes(G, 'label')
    fig = plt.figure(figsize=(12, 10))
    nx.draw(G, pos, with_labels=True, font_size=10, node_size=700, node_color='lightblue', edge_color='gray', alpha=0.6)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=8, label_pos=0.3, verticalalignment='baseline')
    plt.title('Knowledge Graph')
    plt.savefig(path)
    
def get_text_graph(G):
    graph_text = ""
    for edge in G.edges(data = True):
        graph_text += f'''\n{edge[0]} {edge[2]["label"]} {edge[1]},'''
    return graph_text

if __name__ == "__main__":

    try:
        env = TextWorldWrapper(
            "game_data/cooking_games/tw-cooking-recipe2+take2+go1-bBPgiel3Fo8qSb6q.z8"
        )
        done = False
        reward = 0
        score = 0
        obs, infos = env.reset()
        nb_moves = 0
        while not done:
            # builds a graph with current state of the world:
            graph = graph_from_facts(infos)
            #draw_graph(graph)
            print(f"============= STEP#{nb_moves} OBS =================")
            print(f"STEP #{nb_moves+1}")
            print("Your current observation:\n", infos['feedback'])

            print("\nYour inventory:\n", env.get_inventory())
            print(f'\nYour possible Actions:\n', infos["admissible_commands"])
            print()

            print(f"reward:", reward, "score:", score, "max possible score:", infos["max_score"])
            #print("info keys:", list(infos.keys()))
            command = input("enter your command: ")
            obs, reward, done, infos = env.step(command)
            score += reward
            nb_moves += 1
        print("GAME OVER.")
    except KeyboardInterrupt:
        pass  # Press the stop button in the toolbar to quit the game.

    print("Played {} steps, scoring {} out of {} points".format(nb_moves, score, infos["max_score"]))