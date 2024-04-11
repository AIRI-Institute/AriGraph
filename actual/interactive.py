from prompts import *
from prompts_v2 import *
from graphs.extended_graphs import ExtendedGraphPagerankStrategy

main_goal = "Find the treasure"
model, system_prompt = "gpt-4-0125-preview", actual_system_prompt.format(main_goal = main_goal)
graph = ExtendedGraphPagerankStrategy(model, system_prompt)
graph.load("exp_detective_extended_graph_with_walkthrough")
breakpoint()