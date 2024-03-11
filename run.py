import subprocess
import yaml
import sys
import os

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# install("datasets==2.16.1")
# install("transformers==4.31.0")

from pipeline import pipeline, bigraph_pipeline, walkthrough_pipeline
from pipeline_reserve import bigraph_pipeline as bigraph_reserve

with open('KG/config.yaml') as f:
    config = yaml.safe_load(f)

if config["pipeline"] == "standart":
    pipeline(config)
if config["pipeline"] == "bigraph":
    bigraph_pipeline(config)
if config["pipeline"] == "walkthrough":
    walkthrough_pipeline(config)
if config["pipeline"] == "reserve":
    bigraph_reserve(config)
if config["pipeline"] == "consequence":
    configs = [
        # ["gpt", "Recipe_3_cook_cut", "benchmark/recipe3_cook_cut/tw-cooking-recipe3+take3+cook+cut+drop+go1-7yGrcV9pTE8DF75n.z8", "game_gpt_recipe3_cook_cut.txt"],
        # ["gpt", "Take2_go9", "benchmark/take2_go9/tw-cooking-recipe2+take2+go9-Q9nDu630U5j3tqBG.z8", "game_gpt_take2_go9.txt"],
        # ["agent", "Recipe_3_cook_cut", "benchmark/recipe3_cook_cut/tw-cooking-recipe3+take3+cook+cut+drop+go1-7yGrcV9pTE8DF75n.z8", "game_agent_recipe3_cook_cut.txt"],
        ["agent", "Take2_go9", "benchmark/take2_go9/tw-cooking-recipe2+take2+go9-Q9nDu630U5j3tqBG.z8", "game_agent_take2_go9.txt"],
        ["agent", "Navigation4", "benchmark/navigation4/navigation4.z8", "game_agent_navigation4.txt"],
        ["agent", "Navigation2", "benchmark/navigation2/navigation2.z8", "game_agent_navigation2.txt"],
        ["gpt", "Navigation4", "benchmark/navigation4/navigation4.z8", "game_gpt_navigation4.txt"],
        ["gpt", "Navigation2", "benchmark/navigation2/navigation2.z8", "game_gpt_navigation2.txt"],
    ]
    for value in configs:
        if value[0] == "gpt":
            bigraph_pipeline(config, *value[1:])
        elif value[0] == "agent":
            bigraph_reserve(config, *value[1:])
