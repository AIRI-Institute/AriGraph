import json
import torch
import numpy as np
import transformers

from graphs.contriever_graph import LLaMAContrieverGraph, ContrieverGraph
from agents.llama_agent import LLaMAagent
from agents.parent_agent import GPTagent
from utils.utils import Logger


log_path = "MusiqueTestGPTmini"
# musique | hotpotqa 
task_name = "musique"
topk_episodic = 2
graph_model, qa_model = "gpt-4o-mini", "gpt-4o-mini"
log = Logger(log_path)

def run():
    tasks = get_data(task_name)
    agent_items, agent_qa, graph = load_setup(graph_model, qa_model)
    trueP, pred_len, true_len, EM = [], [], [], []

    for task in tasks:
        graph.clear()
        for text in task["paragraphs"]:
            triplets, episodic = graph.update_without_retrieve(text["paragraph_text"], [], log)

        question = task["question"]
        log("-" * 15)
        log("QUESTION: " + str(question))
        items = agent_items.item_processing_scores_qa(question)[0]
        if not isinstance(items, dict):
            true_answer = task["answer"].strip('''. \n'"?''').lower().split()
            trueP.append(0), pred_len.append(0), true_len.append(len(true_answer))
            EM.append(False)
            log("INCORRECT FORMAT OF ITEMS: " + str(items))
            continue
        log("CRUCIAL ITEMS: " + str(items))

        subgraph, episodic = graph.retrieve(items, question, [], topk_episodic)
        log("ASSOCIATED SUBGRAPH: " + str(subgraph))
        log("EPISODIC MEMORY: " + str(episodic))

        answer = get_answer(agent_qa, question, subgraph, episodic)
        log("AGENT ANSWER: " + str(answer))
        log("TRUE ANSWER: " + str(task["answer"]))

        compute_and_print_metrics(answer, task, trueP, true_len, pred_len, EM)
        log("="* 56 + "\n")



def get_data(task_name):
    if task_name == "musique":
        with open('qa_data/musique_ans_v1.0_dev.jsonl', 'r') as json_file:
            json_list = list(json_file)

        tasks = []
        for json_str in json_list:
            result = json.loads(json_str)
            tasks.append(result)
    if task_name == "hotpotqa":
        with open('qa_data/hotpot_dev_distractor_v1.json', 'r') as inp:
            data = json.load(inp)
        tasks = [" ".join(task["context"][-1]) for task in data]
    ids = np.random.RandomState(seed=42).permutation(len(tasks))[:200]
    tasks = [tasks[i] for i in ids]
    return tasks

def get_answer(agent, question, subgraph, episodic):
    prompt = f'''Your task is answer the following question: "{question}"

    Relevant facts from your memory: {subgraph}

    Relevant texts from your memory: {episodic}

    Answer the question "{question}" with Chain of Thoughts in the following format:
    "CoT: your chain of thoughts
    Direct answer: your direct answer to the question"
    Direct answer must be concrete and must not contain alternatives, descriptions or reasoning.
    Write "Unknown" if you have doubts.
    Do not write anything except answer in the given format.

    Your answer: '''
    return agent.generate(prompt)[0]

def compute_and_print_metrics(answer, task, trueP, true_len, pred_len, EM):
    answer = answer.split("Direct answer:")[-1].strip('''. \n`'"?''').lower().split()
    answer = [el.strip('''. \n'`"?''') for el in answer]
    true_answer = task["answer"].strip('''. \n'`"?''').lower().split()
    true_answer = [el.strip('''. \n'`"?''') for el in true_answer]
    true_P = len({word for word in answer if word in true_answer})
    trueP.append(true_P), pred_len.append(len(answer)), true_len.append(len(true_answer))
    EM.append(answer == true_answer)
    prec = np.sum(trueP) / np.sum(pred_len)
    rec = np.sum(trueP) / np.sum(true_len)
    f1 = 2 * prec * rec / (prec + rec)
    em = np.mean(EM)
    log(f"F1: {f1}, RECALL: {rec}, PRECISION: {prec}, EXACT MATCH: {em}")

def load_setup(graph_model, qa_model):
    if "llama" in graph_model or "llama" in qa_model:
        pipeline = transformers.pipeline(
            "text-generation",
            model="Undi95/Meta-Llama-3-70B-Instruct-hf",
            model_kwargs={"torch_dtype": torch.bfloat16},
            device_map="auto"
        )
    
    if "llama" in graph_model:
        graph = LLaMAContrieverGraph("", "You are a helpful assistant", "", pipeline, "cuda")
        agent_items = LLaMAagent("You are a helpful assistant", pipeline)

    else:
        graph = ContrieverGraph(graph_model, "You are a helpful assistant", "YOUR KEY HERE", "cuda")
        agent_items = GPTagent(graph_model, "You are a helpful assistant", "YOUR KEY HERE")

    if "llama" in qa_model:
        agent_qa = LLaMAagent("You are a helpful assistant", pipeline)

    else:
        agent_qa = GPTagent(graph_model, "You are a helpful assistant", "YOUR KEY HERE")

    return agent_items, agent_qa, graph


if __name__ == "__main__":
    run()