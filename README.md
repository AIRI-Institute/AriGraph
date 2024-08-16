# AriGraph: Learning Knowledge Graph World Models with Episodic Memory for LLM Agents

AriGraph functions as the external memory architecture for large language models (LLMs), featuring a knowledge graph that is built from the ground up. This memory, configured as a semantic knowledge graph with added episodic vertices and edges, greatly improves the performance of Retrieval-Augmented Generation (RAG) in text-based games. Currently, AriGraph is a key component of the Ariadne agent, crafted to navigate the challenges of text-based games within the [TextWorld](https://github.com/microsoft/TextWorld) framework. This agent markedly surpasses all pre-existing baselines in these scenarios and showcases exceptional scalability in more expansive environments. For more detailed information about AriGraph and the Ariadne agent, please refer to the accompanying [paper](https://arxiv.org/abs/2407.04363). Experience the games used to evaluate our agent by following the provided [link](http://158.255.5.225/).

![**Ariadne agent and its results**](img/Architecture.png?raw=True)

## Performance
We implemented five TextWorld environments for three distinct tasks: Treasure Hunt, Cleaning, and Cooking. The Treasure Hunt task requires navigating a maze and searching for treasure, while the Cleaning task involves tidying up a house by placing items in their designated spots. The Cooking task focuses on gathering ingredients and preparing a meal. Each LLM agent tested had the same decision-making module, differing only in memory implementation. We reported average human scores across all runs and for the top-3 performing runs. The table below presents the mean normalized game scores: 
Type of memory | Treasure Hunt | Cleaning | Cooking | Treasure Hunt Hard | Cooking Hard
-- | -- | -- | -- | -- | -- 
AriGraph (ours) | 1.0 | 0.79 | 1.0 | 1.0 | 1.0
Human Players Top-3 | 1.0 | 0.85 | 1.0 | - | -
Human Players All | 0.96 | 0.59 | 0.32 | - | -
Full History | 0.49 | 0.05 | 0.18 | - | -
Summary | 0.33 | 0.39 | 0.52 | 0.17 | 0.21
RAG | 0.33 | 0.35 | 0.36 | 0.17 | 0.17

## Requirements
Due to dependencies required by TextWorld, our code can only be executed on Linux systems, specifically after installing certain system libraries.
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
  
The other Python files contain a pipeline for each agent as well as code for running the game in interactive mode in the console. Each pipeline includes a highlighted, changeable section with parameters for execution.

## Citation
If you find our work useful, please cite the [AriGraph](https://arxiv.org/abs/2407.04363):
```
@misc{anokhin2024arigraphlearningknowledgegraph,
      title={AriGraph: Learning Knowledge Graph World Models with Episodic Memory for LLM Agents}, 
      author={Petr Anokhin and Nikita Semenov and Artyom Sorokin and Dmitry Evseev and Mikhail Burtsev and Evgeny Burnaev},
      year={2024},
      eprint={2407.04363},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2407.04363}, 
}
```
