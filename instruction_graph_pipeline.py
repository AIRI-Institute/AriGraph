

from graphs.contriever_graph import ContrieverGraph
from utils.utils import process_triplets, Logger
from utils.retriever_search_drafts import graph_retr_search

graph = ContrieverGraph("gpt-4-0125-preview", "You are a helpful assistant", "anykey")

prompt_extraction = """Your task is to extract triplets from instruction.
This triplets must be in form 'subject, relation, object' and must accurate decompose instruction into elementary instructions for future use.
For example, from instruction 'triplets must be brief and contain no more than 7 words' you should extract following triplets: 
'triplets, must be, brief; brief, contain no more than, 7 words'.
####
Previously extracted triplets that you should follow: {instructions}.
####
Current raw instruction that must be decompose: {instruction}.
####

Give your answer strictly in the following format:
'subject1, relation1, object1; subject2, relation2, object2; ...'
Your answer: """

prompt_refining = """Your task is to identify outdated or inaccurate instructions with respect to the newest available instruction.
Previous instructions are given in format of triplets: 'subject1, relation1, object1; subject2, relation2, object2; ...'.
Your task is to identify outdated or inaccuratre triplets with respect to new instruction and list them in original format.
####
Previous instructions: {instructions}.
####
Newest instruction: {instruction}.
####

Some instructions may describe how to perform replacing. So, you should follow them when identifying outdated instructions. 
Remember that you should not include in answer previous instructions that not contradict with the newest instruction.
Give your answer strictly in the following format:
'subject1, relation1, object1; subject2, relation2, object2; ...'
Your answer: """

prompt_items = """Your task is to extract all entities which appear in the following text:
'{instruction}'.
If entity appears implicit, you also should include it into answer. For example, from text 'triplets must be no longer than 7 words' 
you should extract 'triplets, must be, length, constraint'.

Give your answer strictly in the following format:
'entity1, entity2, ...'
Your answer: """

done = False
log = Logger("test_instruction_graph")
while not done:
    instruction = input("Insert instruction: ")
    log("Instruction: " + instruction)

    prompt = prompt_items.format(instruction=instruction)
    response, _ = graph.generate(prompt, t = 0.8)
    log("Crucial items: " + response)
    items = response.strip('''. '"/?''').split(",")

    subgraph = set()
    if graph.triplets:
        for query in items: 
            results = graph_retr_search(
                query, graph.convert(graph.triplets), graph.retriever, max_depth=2,  
                topk=5,
                post_retrieve_threshold=0.75, 
                verbose=2
            )
            subgraph.update(results)


    log("Actual instructions: " + str(subgraph))
    prompt = prompt_extraction.format(instructions = subgraph, instruction = instruction)
    response, _ = graph.generate(prompt, t = 0.8)
    log("Raw new triplets: " + response)
    new_triplets_raw = process_triplets(response)
    new_triplets_str = graph.exclude(new_triplets_raw)

    prompt = prompt_refining.format(instructions = subgraph, instruction = instruction)
    response, _ = graph.generate(prompt, t = 0.8)
    log("Raw replacements: " + response)
    outdated_triplets_raw = process_triplets(response)
    outdated_triplets_str = graph.convert(outdated_triplets_raw)

    graph.delete_triplets(outdated_triplets_raw, [])
    graph.add_triplets(new_triplets_raw)

    log("\n\nNew triplets: " + str(new_triplets_str))
    log("Outdated triplets: " + str(outdated_triplets_str))

    done = input("Is done? ") == "True"
    log("===" * 18)