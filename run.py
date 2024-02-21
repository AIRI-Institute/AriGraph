import subprocess
import yaml
import sys
import os

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# install("datasets==2.16.1")
# install("transformers==4.31.0")

from pipeline import pipeline, bigraph_pipeline, walkthrough_pipeline

with open('KG/config.yaml') as f:
    config = yaml.safe_load(f)

if config["pipeline"] == "standart":
    pipeline(config)
if config["pipeline"] == "bigraph":
    bigraph_pipeline(config)
if config["pipeline"] == "walkthrough":
    walkthrough_pipeline(config)
