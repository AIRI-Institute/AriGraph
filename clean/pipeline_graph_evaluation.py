from utils.utils import Logger
from utils.contriever import Retriever
from graphs.lazy_graph import LazyGraph
from prompts.prompts import prompt_refining_items
from utils.textworld_adapter import TextWorldWrapper
from prompts.system_prompts import default_system_prompt
from utils.envs_cfg import ENV_NAMES, WALKTHROUGH
from utils.utils import clear_triplet, parse_triplets_removing
from utils.textworld_adapter import TextWorldWrapper, graph_from_facts


# Changeable part of pipeline

log_file = "test_new_pipe_graph"
model = "gpt-4-0125-preview"

# env_name can be picked from:
# ["hunt", "cook", "clean"]
# for test another envs edit utils.envs_cfg
env_name = "cook"
retriever_device = "cpu"

# End of changeable part of pipeline

log = Logger(log_file)
retriever = Retriever(retriever_device)
graph = LazyGraph(model, default_system_prompt, retriever)
env = TextWorldWrapper(ENV_NAMES[env_name])

recalls, precisions = [], []
total_success, total_true, total_extr = 0, 0, 0
  
def run():
    for step, action in enumerate(WALKTHROUGH[env_name]):
        log("Step: " + str(step + 1))
        
        if done:
            break
        
        G_true = graph_from_facts(info)    
        full_graph = G_true.edges(data = True)

        full_graph = [triplet for triplet in full_graph if triplet[0] != "player" and triplet[1] != "player" and triplet[0] != "P" and triplet[1] != "P"]
        graph = LazyGraph(model, default_system_prompt, retriever)
        graph.add_triplets(full_graph)
        
        observation, reward, done, info = env.step(action)
        
        G_new = graph_from_facts(info)    
        full_graph_new = G_new.edges(data = True)
        full_graph_new = [triplet for triplet in full_graph_new if triplet[0] != "player" and triplet[1] != "player" and triplet[0] != "P" and triplet[1] != "P"]
        
        new_triplets_raw = [clear_triplet(triplet) for triplet in full_graph_new if triplet not in full_graph]
        log("New triplets: " + str(new_triplets_raw))
        
        predicted_outdated = get_predict(new_triplets_raw)

        true_outdated = [clear_triplet(triplet) for triplet in full_graph if triplet not in full_graph_new]
        log("True replacings: " + str(true_outdated))
        
        log("Recalls: " + str(recalls))
        log("Precisions: " + str(precisions))
        log("=" * 70)

    log("ITOG RECALL: " + str(total_success / total_true))
    log("ITOG PRECISION: " + str(total_success / total_extr))


def get_predict(new_triplets_raw):
    items_ = list({triplet[0] for triplet in new_triplets_raw} | {triplet[1] for triplet in new_triplets_raw})
    associated_subgraph = graph.get_associated_triplets(items_, steps = 1)
    prompt = prompt_refining_items.format(ex_triplets = associated_subgraph, new_triplets = [graph.str(triplet) for triplet in new_triplets_raw])
    response, cost = graph.generate(prompt, t = 0.2)
    log("Replacings: " + response)
    
    predicted_outdated = parse_triplets_removing(response)
    return predicted_outdated

def compute_scores(predicted_outdated, true_outdated):
    trueP = 0
    for triplet in predicted_outdated:
        if triplet in true_outdated:
            trueP += 1
    total_success += trueP
    total_true += len(true_outdated)
    total_extr += len(predicted_outdated)
    
    if true_outdated:
        recalls.append(trueP / len(true_outdated))
    else:
        recalls.append(1)
    if predicted_outdated:
        precisions.append(trueP / len(predicted_outdated))
    else:
        precisions.append(1)



if __name__ == "__main__":
    run()