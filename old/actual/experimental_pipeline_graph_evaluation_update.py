from time import time

from parent_agent import GPTagent
from textworld_adapter import TextWorldWrapper
from parent_graph import TripletGraph
from graphs.subgraph_strategy import SubgraphStrategy
from agents.direct_action_agent import DirectActionAgent
from agents.plan_in_json_agent import PlanInJsonAgent
from graphs.history import History, HistoryWithPlan
from graphs.extended_graphs import ExtendedGraphSubgraphStrategy, ExtendedGraphPagerankStrategy, \
    ExtendedGraphMixtralPagerankStrategy, ExtendedGraphDescriptionPagerankStrategy
from graphs.description_graphs import DescriptionGraphBeamSearchStrategy
from graphs.parent_without_emb import GraphWithoutEmbeddings
from graphs.dummy_graph import DummyGraph
from graphs.steps_in_triplets import StepsInTripletsGraph
from graphs.lazy_graph import LazyGraph
from graphs.contriever_graph import ContrieverGraph
from prompts import *
from prompts_v2 import *
from utils import *
from prompts_diff_agents import *
from textworld_adapter import *
from observedgpaph import ObservedGraph

# There is configs of exp, changeable part of pipeline
# If you add some parameters, please, edit config
log_file = "exp_clean_graph_test_update"
env_name = "benchmark/clean_3x3/clean_3x3_mess_1.z8"
main_goal = "Find the treasure"
model = "gpt-4-0125-preview"
game = "clean"
goal_freq = 10
threshold = 0.02
n_prev, majority_part = 3, 0.51

max_steps, n_attempts = 150, 1
n_neighbours = 4

system_prompt = system_prompt
# End of changeable part

log = Logger(log_file)

# Flexible init with only arguments class need
env = TextWorldWrapper(env_name)
walkthrough = {
    "nav3": ["take Key 1", "go west", "go south", "go east", "go east", "unlock White locker with Key 1", 
            "open White locker", "take Key 2 from White locker", "examine Note 2", "go west", "go west", "unlock Red locker with Key 2", 
            "open Red locker", "take Key 3 from Red locker", "take Note 3 from Red locker", "examine Note 3", "go east", "go east", 
            "go north", "go north", "go west", "go east", "go east", "unlock Cyan locker with Key 3", "open Cyan locker", 
            "take Golden key from Cyan locker", "go west", "go south", "go south", "go west", "go west", "go north", 
            "go east", "unclock Golden locker with Golden key", "unlock Golden locker with Golden key", "open Golden locker", 
            "take treasure from Golden locker"],
    "clean": ['take toothbrush', 'go north', 'take dumbbell', 'take dirty plate', 'go east', 'take raw meat', 'go south', 
               'take wet towel', 'go south', 'take swimming fins', 'go west', 'take toy car', 
               'put swimming fins on equipment rack', 'go west', 'take fantasy book', 'put dumbbell on dumbbell stand', 
               'go north', 'take business suit', 'open refrigerator', 'put raw meat in refrigerator', 'close refrigerator', 
               'open dishwasher', 'put dirty plate in dishwasher', 'close dishwasher', 'go north', 'take sleeping lamp', 
               'take elegant table runner', 'put toothbrush on bathroom sink', 'put wet towel on towel rack', 'go east', 
               'open toy storage cabinet', 'put toy car in toy storage cabinet', 'close toy storage cabinet', 'go east', 
               'go south', 'open wardrobe', 'put business suit in wardrobe', 'close wardrobe', 
               'put sleeping lamp on bedside table', 'go south', 'put fantasy book on bookcase', 'go west', 'go north', 
               'put elegant table runner on dining table'],
    "cook": ['south', 'examine cookbook', 'take orange bell pepper', 'east', 'east', 'north', 'take green bell pepper', 
             'take yellow potato', 'south', 'cook orange bell pepper with BBQ', 'cook yellow potato with BBQ', 'west', 'west', 
             'take knife', 'dice green bell pepper', 'dice orange bell pepper', 'slice yellow potato', 
             'cook green bell pepper with stove', 'prepare meal', 'eat meal']
}


locations = set()
    
total_amount, total_time = 0, 0

for i in range(n_attempts):
    graph = ContrieverGraph(model, system_prompt, 8, None, 8)
    observed_graph = ObservedGraph()
    log("\n\n\n\n\n\n\nAttempt: " + str(i + 1))
    action = "start"
    plan0 = "Explore all locations"
    subgraph = "Nothing there"
    description = "Nothing there"
    prev_action = "start"
    observation, info = env.reset()
    done = False
    recalls, precisions = [], []
    prev_location = env.curr_location
    observations = []
    for step, action in enumerate(walkthrough[game]):
        start = time()
        log("Step: " + str(step + 1))
        observation = observation.split("$$$")[-1]
        if step == 0:
            observation += f""" \n Your task is to get a treasure. Treasure is hidden in the golden locker. You need a golden key to unlock it. The key is hidden in one of the other lockers located in the environment. All lockers are locked and require a specific key to unlock. The key 1 you found in room A unlocks white locker. Read the notes that you find, they will guide you further."""
        observation = "Step: " + str(step + 1) + "\n" + observation
        inventory = env.get_inventory()

        if done:
            log("Game itog: " + observation)
            log("\n" * 10)
            break

        observation += f"\nInventory: {inventory}"
        observation += f"\nAction that led to this observation: {prev_action}\n\n"
        prev_action = action
        
        locations.add(env.curr_location.lower())
        
        G_true = graph_from_facts(info)    
        full_graph = G_true.edges(data = True)
        full_graph = [clear_triplet(triplet) for triplet in full_graph]
        full_graph = [triplet for triplet in full_graph if triplet[0] != "player" and triplet[1] != "player" and triplet[0] != "P" and triplet[1] != "P"]
        observed_graph.update_graph_based_on_observation(observation, full_graph)
        true_graph = observed_graph.graph.edges(data = True)

        graph.update(observation, observations, "{}", locations, env.curr_location.lower(), prev_location, prev_action, log, step, [])
        
        trueP = 0
        not_found = []
        for true_triplet_ in true_graph:
            found = False
            true_triplet = clear_triplet(true_triplet_)
            for triplet in graph.triplets:
                if (triplet[0] == true_triplet[0] and triplet[1] == true_triplet[1]) or (triplet[1] == true_triplet[0] and triplet[0] == true_triplet[1]):
                    found = True
                    trueP += 1
                    break
            if not found:
                not_found.append(graph.str(true_triplet))
        log("Not found triplets: " + str(not_found))
        
        recalls.append(trueP / len(true_graph))
        precisions.append(trueP / len(graph.triplets))
        
        log("Recall: " + str(np.mean(recalls)))
        log("Precision: " + str(np.mean(precisions)))
        log("Recalls: " + str(recalls))
        log("Precisions: " + str(precisions))
        
        
        prev_obs = observation
        observations.append(observation)
        observations = observations[-n_prev:]
        prev_location = env.curr_location.lower()
        observation, reward, done, info = env.step(action)
        
        G_true = graph_from_facts(info)    
        full_graph = G_true.edges(data = True)
        full_graph = [clear_triplet(triplet) for triplet in full_graph]
        full_graph = [triplet for triplet in full_graph if triplet[0] != "player" and triplet[1] != "player" and triplet[0] != "P" and triplet[1] != "P"]
        if any(direction in prev_action for direction in ["west", "east", "south", "north"]):
            observed_graph.update_graph_for_movement(prev_obs, action, observation, full_graph)
        else:
            observed_graph.update_graph_based_on_action(observation, action, full_graph) 
        
        step_amount = graph.total_amount - total_amount
        total_amount += step_amount
        log(f"\nTotal amount: {round(total_amount, 2)}$, step amount: {round(step_amount, 2)}$")
        
        step_time = time() - start
        total_time += step_time
        log(f"Total time: {round(total_time, 2)} sec, step time: {round(step_time, 2)} sec")
        log("=" * 70)