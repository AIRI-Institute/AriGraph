import textworld.gym
import textworld
import textworld.render
from textworld_adapter import TextWorldWrapper, graph_from_facts, get_text_graph, draw_graph
import networkx as nx


class ObservedGraph:
    def __init__(self):
        self.graph = nx.MultiDiGraph()  # Using MultiDiGraph to handle multiple edges between two nodes

    def update_graph_based_on_observation(self, observation, full_graph):
        """Update the observed graph based on a single observation."""
        words_in_observation = observation.lower()

        for edge in full_graph:
            source, target, attributes = edge
            # Check if both entities are in the observation or if the source entity has a state change
            if (source.lower() in words_in_observation and target.lower() in words_in_observation) or \
               ('itself' == target.lower() and source.lower() in words_in_observation and attributes['label'] in words_in_observation):
                if self.graph.has_edge(source, target):
                # This loop removes all edges between 'source' and 'target'
                    for _ in range(self.graph.number_of_edges(source, target)):
                        self.graph.remove_edge(source, target)
                self.graph.add_edge(source, target, **attributes)

    def update_graph_based_on_action(self, observation, action, full_graph):
        """Update the observed graph based on action."""
        words_in_observation = observation.lower()

        for edge in full_graph:
            source, target, attributes = edge
            # Check if both entities are in the observation or if the source entity has a state change
            if (source.lower() in words_in_observation and source.lower() in action.lower()):
                if self.graph.has_edge(source, target):
                # This loop removes all edges between 'source' and 'target'
                    for _ in range(self.graph.number_of_edges(source, target)):
                        self.graph.remove_edge(source, target)
                

    def update_graph_for_movement(self, previous_observation, action, current_observation, full_graph):
        """Update the observed graph based on movement from one location to another."""
        words_in_previous_obs = previous_observation.lower()
        words_in_current_obs = current_observation.lower()
        words_tot = words_in_current_obs + words_in_previous_obs
        

        for edge in full_graph:
            source, target, attributes = edge
            directions = ["west", "east", "south", "north"]
            if (source.lower() in words_tot and target.lower() in words_tot) and any(direction in attributes['label'] for direction in directions):
                if self.graph.has_edge(source, target):
                # This loop removes all edges between 'source' and 'target'
                    for _ in range(self.graph.number_of_edges(source, target)):
                        self.graph.remove_edge(source, target)
                self.graph.add_edge(source, target, **attributes)
                

    def replace_state_change_edges(self, entity, new_state):
        """Replace edges for entities that have changed state (e.g., unlocked)."""
        for edge in list(self.graph.edges(entity, data=True)):
            if edge[1] == 'itself':  # Check if the edge describes the state of the entity
                self.graph.remove_edge(edge[0], edge[1])
                self.graph.add_edge(edge[0], edge[1], label=new_state)

    def print_observed_graph(self):
        print(self.graph.edges(data=True))


request_infos = textworld.EnvInfos(
    admissible_commands=True, 
    entities=True,             
    facts=True,
    inventory=True,
    location=True,
    policy_commands = True
)


env_id = textworld.gym.register_game("tw_games/benchmark/navigation2/navigation2.z8", request_infos,
                                     max_episode_steps=200)
env = textworld.gym.make(env_id)
obs, infos = env.reset()  # Start new episode.
env.render()


observed_graph = ObservedGraph()

score, moves, done = 0, 0, False
for i in range(200):
    G_true = graph_from_facts(infos)
    full_graph = G_true.edges(data = True)
    observed_graph.update_graph_based_on_observation(obs, full_graph)
    observed_graph.print_observed_graph()

    command = input("> ")
    obs_new, score, done, infos = env.step(command)
    env.render()
    moves += 1
    
    # Update the knowledge graph based on observations and actions
    if any(direction in command for direction in ["west", "east", "south", "north"]):
        observed_graph.update_graph_for_movement(obs, command, obs_new, full_graph)
    else:
        observed_graph.update_graph_based_on_action(obs_new, command, full_graph)   
    
    
    obs = obs_new
    
    if done:
         break
    
env.close()