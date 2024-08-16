import json
import torch
import numpy as np
import transformers

from graphs.contriever_graph import LLaMAContrieverGraph
from agents.llama_agent import LLaMAagent
from utils.utils import Logger

with open('musique_ans_v1.0_dev.jsonl', 'r') as json_file:
    json_list = list(json_file)

tasks = []
for json_str in json_list:
    result = json.loads(json_str)
    tasks.append(result)
ids = np.random.RandomState(seed=42).permutation(len(tasks))[:200]
tasks = [tasks[i] for i in ids]


log_path = "MusiqueTestBig/final"
topk_episodic = 2

pipeline = transformers.pipeline(
            "text-generation",
            model="Undi95/Meta-Llama-3-70B-Instruct-hf",
            model_kwargs={"torch_dtype": torch.bfloat16},
            device_map="auto"
        )
graph = LLaMAContrieverGraph("", "You are a helpful assistant", "", pipeline, "cuda")
global_graph = LLaMAContrieverGraph("", "You are a helpful assistant", "", pipeline, "cuda")
agent = LLaMAagent("You are a helpful assistant", pipeline)
log = Logger(log_path)

trueP, pred_len, true_len, EM = [], [], [], []
for task in tasks:
    graph.clear()
    for text in task["paragraphs"]:
        full_text = text["title"] + '\n' + text["paragraph_text"]
        triplets, episodic = graph.update_without_retrieve(text["paragraph_text"], [], log)
        global_graph.add_triplets(triplets)
        global_graph.obs_episodic[text["paragraph_text"]] = episodic
    question = task["question"]
    log("-" * 15)
    log("QUESTION: " + str(question))
    items = agent.item_processing_scores_musique(question)[0]
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
    answer = agent.generate(prompt)[0]
    log("AGENT ANSWER: " + str(answer))
    log("TRUE ANSWER: " + str(task["answer"]))
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
    log("="* 56 + "\n")



log("\n" * 5 + "NOW GLOBAL RESULTS\n\n")
trueP, pred_len, true_len, EM = [], [], [], []
for task in tasks:
    question = task["question"]
    log("-" * 15)
    log("QUESTION: " + str(question))
    items = agent.item_processing_scores_musique(question)[0]
    if not isinstance(items, dict):
        true_answer = task["answer"].strip('''. \n'"?''').lower().split()
        trueP.append(0), pred_len.append(0), true_len.append(len(true_answer))
        EM.append(False)
        log("INCORRECT FORMAT OF ITEMS: " + str(items))
        continue
    log("CRUCIAL ITEMS: " + str(items))
    subgraph, episodic = global_graph.retrieve(items, question, [], topk_episodic)
    log("ASSOCIATED SUBGRAPH: " + str(subgraph))
    log("EPISODIC MEMORY: " + str(episodic))
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
    answer = agent.generate(prompt)[0]
    log("AGENT ANSWER: " + str(answer))
    log("TRUE ANSWER: " + str(task["answer"]))
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
    log("="* 56 + "\n")
    
