from time import time

from parent_agent import GPTagent
from textworld_adapter import TextWorldWrapper
from parent_graph import TripletGraph
from graphs.subgraph_strategy import SubgraphStrategy
from agents.direct_action_agent import DirectActionAgent
from agents.plan_in_json_agent import PlanInJsonAgent
from graphs.history import History, HistoryWithPlan
from graphs.extended_graphs import ExtendedGraphSubgraphStrategy, ExtendedGraphPagerankStrategy, \
    ExtendedGraphMixtralPagerankStrategy, ExtendedGraphDescriptionPagerankStrategy
from graphs.description_graphs import DescriptionGraphBeamSearchStrategy
from graphs.parent_without_emb import GraphWithoutEmbeddings
from graphs.dummy_graph import DummyGraph
from graphs.steps_in_triplets import StepsInTripletsGraph
from prompts import *
from utils import *
from prompts_diff_agents import *

graph = StepsInTripletsGraph(model = "gpt-4-0125-preview", system_prompt = system_prompt)
graph.triplets += [
    ["room a", "room b", {"label": "east of"}],
    ["room b", "room c", {"label": "north of"}],
    ["room b", "room f", {"label": "south of"}],
    ["room e", "room c", {"label": "south of"}],
    ["room c", "room d", {"label": "west of"}],
    ["room d", "room g", {"label": "west of"}]
]

locations = {"room a", "room b", "room c", "room f", "room e", "room d", "room g"}

action = input("Insert action: ")
destination = action.split('go to ')[1]
spat_graph = graph.compute_spatial_graph(locations)
breakpoint()
path = graph.find_path("room a", destination, locations)
print("path", path)
breakpoint()