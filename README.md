# AriGraph: Learning Knowledge Graph World Models with Episodic Memory for LLM Agents

AriGraph is the architecture of external memory for large language models (LLMs) that utilize a knowledge graph which is building from scratch. In its current implementation, it constitutes the core component of the Ariadne agent, which is designed to navigate text-based games within the [TextWorld]([https://arxiv.org/abs/2304.11062](https://github.com/microsoft/TextWorld) framework. This agent significantly outperforms all established baselines in text-based game scenarios and demonstrates robust scalability in larger environments. Detailed information about the AriGraph and the Ariadne agent can be found in the [paper](https://arxiv.org/abs/2304.11062).
![**Ariadne agent and his results**](img/Architecture.png?raw=True)

## Performance
We implement five TextWorld environments for three different tasks: Treasure Hunt, Cleaning and Cooking. The first task involves navigating a maze and searching for treasure, the second entails tidying up a house by placing items in their designated spots, and the third focuses on gathering ingredients and preparing a dish. Each tested LLM agent had an identical decision-making module, and the agents differed from each other only in the implementation of memory. There is a mean normalized game scores in the following table: 
Type of memory | Treasure Hunt | Cleaning | Cooking | Treasure Hunt Hard | Cooking Hard
-- | -- | -- | -- | -- | -- 
AriGraph (ours) | 1.0 | 0.79 | 1.0 | 1.0 | 1.0
Full History | 0.49 | 0.05 | 0.18 |  | 
Summary | 0.33 | 0.39 | 0.52 | 0.17 | 0.21
RAG | 0.33 | 0.35 | 0.36 | 0.17 | 0.17
