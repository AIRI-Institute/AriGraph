# AriGraph: Learning Knowledge Graph World Models with Episodic Memory for LLM Agents

AriGraph is the architecture of external memory for large language models (LLMs) that utilize a knowledge graph which is building from scratch. In its current implementation, it constitutes the core component of the Ariadne agent, which is designed to navigate text-based games within the [TextWorld](https://github.com/microsoft/TextWorld) framework. This agent significantly outperforms all established baselines in text-based game scenarios and demonstrates robust scalability in larger environments. Detailed information about the AriGraph and the Ariadne agent can be found in the [paper](https://arxiv.org/abs/2304.11062).

![**Ariadne agent and his results**](img/Architecture.png?raw=True)

## Performance
We implement five TextWorld environments for three different tasks: Treasure Hunt, Cleaning and Cooking. The first task involves navigating a maze and searching for treasure, the second entails tidying up a house by placing items in their designated spots, and the third focuses on gathering ingredients and preparing a dish. Each tested LLM agent had an identical decision-making module, and the agents differed from each other only in the implementation of memory. There is a mean normalized game scores in the following table: 
Type of memory | Treasure Hunt | Cleaning | Cooking | Treasure Hunt Hard | Cooking Hard
-- | -- | -- | -- | -- | -- 
AriGraph (ours) | 1.0 | 0.79 | 1.0 | 1.0 | 1.0
Full History | 0.49 | 0.05 | 0.18 | - | -
Summary | 0.33 | 0.39 | 0.52 | 0.17 | 0.21
RAG | 0.33 | 0.35 | 0.36 | 0.17 | 0.17

## Requirements
Due to TextWorld dependencies, our code can run only on Linux, after installing some system libraries.
On a Debian/Ubuntu-based system, these can be installed with

    sudo apt update && sudo apt install build-essential libffi-dev python3-dev curl git

And on macOS, with

    brew install libffi curl git

To complete requirements installation, you need Python 3.11+ and to run 

    pip install -r requirements.txt

## Repository structure
- **agents** contains GPTagent.
- **envs** contains TextWorld files for environment loading.
- **graphs** contains TripletGraph in parent_graph.py and other graphs which inherit it.
- **logs** contains logs of every reported run of our agent.
- **prompts** contains prompts used in pipelines.
- **src** and **utils** contains service classes and functions.
  
Other python files contains pipeline for every agent and also code for running game in interactive mode in console. Each pipeline has highlighted changeable part with parameters of running.

## Citation
If you find our work useful, please cite the [AriGraph](https://arxiv.org/abs/2207.06881):
```
@misc{
anokhin2024arigraph,
title={AriGraph: Learning Knowledge Graph World Models with Episodic Memory for LLM Agents},
author={Petr Anokhin and Nikita Semenov and Artyom Sorokin and Dmitry Evseev and Michail Burtsev and Evgeny Burnaev},
year={2024}
}
```
