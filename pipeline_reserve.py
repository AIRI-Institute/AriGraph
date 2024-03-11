from jericho import FrotzEnv

from agent_detective import GPTagent, MixtralAgent
from graph import KnowledgeGraph
from semi_bigraph import KnowledgeSemiBiGraph
from textworld_adapter import TextWorldWrapper, graph_from_facts, get_text_graph

def reflect(graph, agent, items, n_iters = 15):
    summary = graph.get_string_state("last")
    for i in range(n_iters):
        next_state_key = graph.find_best_state(items)
        if next_state_key is None:
            return summary
        next_state = graph.get_string_state(next_state_key)
        summary, items = agent.get_new_summary(summary, next_state)
        items = [graph.get_item(item, agent.get_embedding_local(item))["name"] for item in items if graph.get_item(item, agent.get_embedding_local(item)) is not None]
    return summary

def reflect_ground_truth(graph, agent, items, summary, n_iters = 5):
    triplets = []
    for i in range(n_iters):
        summary, items, triplets_ = agent.get_graph_items(graph, items, summary)
        triplets += triplets_
        if len(items) == 0:
            break
    return summary, triplets

def planning(graph, agent, n_branches = 3, depth = 10):
    branches = []
    for it in range(n_branches):
        current_state = graph.get_last_state()
        branch = {
            "actions": [],
            "final": graph.get_string_state(current_state),
            "experienced_states": [current_state],
            "consequences": [graph.get_string_state(current_state)],
            # "forbidden_actions": {}
        }
        for step in range(depth):
            is_loop = False
            associations, experienced_actions, n = graph.get_associations(state_key = current_state)
            action = agent.get_action_planning(branches, branch, associations, experienced_actions, n, step)
            current_state, is_unknown, graph_action = graph.get_next_step(action, current_state, agent.get_embedding_local(action), branch["consequences"])
            current_state = graph.get_state_key(current_state, agent.get_embedding_local(current_state, True)) if current_state != "Unknown" else current_state
            if current_state in branch["experienced_states"] and current_state != "Unknown":
                true_number = max(branch["experienced_states"].index(current_state) + 1, 2)
                is_loop = True
            # state_for_pred = graph.get_string_state(current_state) if current_state != "Unknown" else current_state
            # consequence = agent.get_predictions(branch, graph_action, state_for_pred, associations, experienced_actions, n)
            consequence = graph.get_string_state(current_state) if current_state != "Unknown" else current_state
            consequence += f"\nAction that led to this: {graph_action}"
            branch["actions"].append(graph_action)
            branch["final"] = consequence
            branch["consequences"].append(consequence)
            branch["experienced_states"].append(current_state)
            if is_unknown:
                break
            if is_loop:
                branch["actions"] = branch["actions"][:true_number - 1]
                branch["experienced_states"] = branch["experienced_states"][:true_number]
                branch["consequences"] = branch["consequences"][:true_number]
                branch["final"] = branch["consequences"][true_number - 1]
                # branch["forbidden_actions"][true_number - 1] = forbidden_action
        branches.append(branch)
    return branches


def pipeline(config):
    graph_name = "Detective"
    load = False
    graph = KnowledgeGraph(graph_name, load)
    agent = GPTagent()
    env = FrotzEnv("z-machine-games-master/jericho-game-suite/detective.z5")
    n_trying = 7
    start = 1
    n_steps = 150
    print_steps = 30
    K, M, maxIters, eps, damping = 150, 250, None, 1e-5, 1
    for one_try in range(start - 1, start - 1 + n_trying):
        observation, info = env.reset()
        valid_actions = env.get_valid_actions()
        done = False
        rewards, scores = [], []
        for step in range(n_steps):
            needful_memories = ""
            inventory = env.get_inventory()
            location = env.get_player_location().name
            if len(graph) > 0:
                source_embeddings = agent.query(observation, inventory, location, valid_actions)
                needful_memories = graph.get_triplets(source_embeddings, K, M, maxIters, eps, damping)
            new_facts = agent.get_new_memories(observation)
            for triplet in new_facts:
                graph.add_triplet(triplet)
            action = agent.act(observation, needful_memories, inventory, location, valid_actions)
            old_obs = observation
            observation, reward, done, info = env.step(action)
            new_memories = agent.reflection_on_action(old_obs, observation, action, reward)
            for triplet in new_memories:
                graph.add_triplet(triplet)
            rewards.append(reward)
            scores.append(info['score'])
            if step < print_steps:
                print("Observation:", observation)
                print("Valid actions:", valid_actions)
                print("Chosen action:", action)
                print("Reward:", reward)
                print("Needful memories:", needful_memories)
                print("====================================================================")
            if done:
                break
            valid_actions = env.get_valid_actions()
            graph.save()
        print("============================================================================================================================")
        print(f"{one_try + 1} Trying")
        print(f"Scored {info['score']} out of {env.get_max_score()}, total steps: {len(scores)}")
        print(f"Scores: {scores}")
        print(f"Rewards: {rewards}")
        print("============================================================================================================================")

def bigraph_pipeline(config, graph_name, game_path, log_file):
    graph_name = graph_name
    load = False
    graph = KnowledgeSemiBiGraph(graph_name, load)
    agent = GPTagent(model = "gpt-4-0125-preview")
    env = TextWorldWrapper(game_path)
    n_trying = 3
    start = 1
    n_steps = 70
    print_steps = n_steps
    # K, M, maxIters, eps, damping = 150, 250, None, 1e-5, 1
    observations = []
    inventory = []
    for trying in range(start - 1, start - 1 + n_trying):
        prev_action = None
        observation, info = env.reset()
        observations.append({"observation": observation, "trying": trying + 1, "step": 0})
        done = False
        rewards, scores = [], []
        action = "start"
        steps_from_reflection = 0
        selected_branch, branches = 0, [{"actions": [], "consequences": []}]
        reflection = {"insight": "Still nothing", "trying": trying + 1}
        for step in range(n_steps):
            observation = observation.split("$$$")[-1]
            old_obs = observation
            location = env.get_player_location() if env.get_player_location() is not None else "Room"
            valid_actions = env.get_valid_actions()

            observed_items, remembered_items = agent.bigraph_processing(observations, observation, location, 
                            valid_actions, trying + 1, step + 1)
            state_key = f'''
Observation: {observation}
Location: {location}
'''         
            state_embedding = agent.get_embedding_local(state_key, True)
            action_embedding = agent.get_embedding_local(action)
            graph.add_state(observation, action, action_embedding, location, trying + 1, step + 1, state_embedding)
            graph.observe_items(observed_items, observation, location, state_embedding)
            remembered_items.append({action: action_embedding})
            graph.remember_items(remembered_items, observation, location, state_embedding)
            graph.save()

            # filtered_items = [graph.get_item(list(item.keys())[0], list(item.values())[0])["name"] for item in remembered_items if graph.get_item(list(item.keys())[0], list(item.values())[0]) is not None]
            # associations, experienced_actions, n = graph.get_associations(filtered_items)
            items = [list(item.keys())[0] for item in observed_items + remembered_items]
            associations, experienced_actions, n = 1, 1, 1
            G = graph_from_facts(env.info)
            start_summary = f'''Previous 2 observations: {observations[-2:]} 
####
Current observation: {observation}
####
'''
            summary, triplets = reflect_ground_truth(G, agent, items, start_summary, n_iters = 3)
            action, use_graph, is_random, insight = agent.get_action_ground_truth(start_summary, summary, triplets, valid_actions, observations)

            # true_graph = get_text_graph(G)

            # breakpoint()
            # action, use_graph, is_random, insight = agent.choose_action(true_graph, observations, observation, location, 
            #                 valid_actions, trying, step, reflection,
            #                 associations, experienced_actions, steps_from_reflection > -1, n, inventory)
            # use_graph = use_graph or steps_from_reflection > 10
            # use_graph = False
            # with open("game_log.txt", "a") as file:
            #     file.write(action + "\n")
            # if use_graph:
            #     steps_from_reflection = 0
            #     reflection = reflect(graph, agent, filtered_items)
            #     reflection = {"insight": reflection, "trying": trying + 1, "step": step + 1}
            #     action, is_random, insight = agent.choose_action_with_reflection(observations, observation, location, 
            #                 valid_actions, trying, step,
            #                 associations, experienced_actions, reflection, n, inventory)
            # else:
            #     steps_from_reflection += 1

            # state_key = graph.get_state_key(state_key, state_embedding)
            # need_plan = False
            # if len(branches[selected_branch]["actions"]) == 0:
            #     need_plan = True
            # elif not (agent.is_equal(state_key, branches[selected_branch]["experienced_states"][0], graph.state_embeddin_treshold, True)):
            #     need_plan = True

            # if need_plan:
            #     branches = planning(graph, agent)
            #     selected_branch = agent.select_branch(branches, observations, observation, location, trying + 1, step + 1, associations, n)

            # if len(branches[selected_branch]["actions"]) + 1 != len(branches[selected_branch]["experienced_states"]):
            #     print("bad branch")
            #     breakpoint()
            # insight = "Now insight is absent"
            # action = branches[selected_branch]["actions"][0]
            # with open("game_log.txt", "a") as file:
            #     for branch in branches:
            #         file.write(f"Branch: {branch}\n")
            # branches[selected_branch]["actions"].pop(0)
            # branches[selected_branch]["consequences"].pop(0)
            # branches[selected_branch]["experienced_states"].pop(0)

            # graph.add_insight(insight, observation, location, state_embedding)

#             state_key = f'''
# Observation: {observation}
# Location: {location}
# '''    
#             state_embedding = agent.get_embedding_local(state_key, True)
#             state_key = graph.get_state_key(state_key, state_embedding)
#             new_obs = graph.get_string_state(state_key) + f"\nAction that led to this: {prev_action}" if prev_action is not None else graph.get_string_state(state_key)
#             observations.append(new_obs)

            observations.append(observation + f"\n\nAction: {action}")
            
            # action = agent.choose_action_vanilla(observations, observation, inventory, location, valid_actions)

            observation, reward, done, info = env.step(action)
            inventory = [item.name for item in env.get_inventory()] if isinstance(env.get_inventory(), list) else env.get_inventory()
            observation += f"\nInventory: {inventory}"
            valid_actions = env.get_valid_actions()
            observation += f"\nValid actions (just recommendation): {valid_actions}"
            
            prev_action = action

            rewards.append(reward)
            scores.append(info['score'])
            if step < print_steps:
                with open(log_file, "a") as file:
                    file.write(f"Step: {step + 1}\n")
                    for branch in branches:
                        file.write(f"Branch: {branch}\n")
                    # file.write(f"Is action chosen: {is_random}\n")
                    file.write(f"Location: {location}\n")
                    file.write(f"Observation: {old_obs}\n")
                    # file.write(f"Inventory: {inventory}\n")
                    temp = [list(item.keys())[0] for item in observed_items]
                    file.write(f"Observed items: {temp}\n")
                    file.write(f"insight: {insight}\n")
                    temp = [list(item.keys())[0] for item in remembered_items]
                    file.write(f"Remembered items: {temp}\n")
                    file.write(f"associations: {associations}\n")
                    file.write(f"Experienced actions: {experienced_actions}\n")
                    # file.write(f"Use graph: {use_graph}\n")
                    file.write(f"Summary: {reflection}\n")
                    file.write(f"Valid actions: {valid_actions}\n")
                    file.write(f"Chosen action: {action}\n")
                    file.write(f"Reward: {reward}\n")
                    file.write("====================================================================\n")
            if done:
                with open(log_file, "a") as file:
                    file.write(f"{observation}\n")
                observation = "***".join(observation.split("***")[:-1])
                state_key = f'''
Observation: {observation}
Location: {location}
'''    
                state_embedding = agent.get_embedding_local(state_key, True)
                action_embedding = agent.get_embedding_local(action)
                graph.add_state(observation, action, action_embedding, location, trying + 1, step + 2, state_embedding)
                graph.add_insight("Game over", observation, location, state_embedding)
                break
        with open(log_file, "a") as file:        
            file.write("============================================================================================================================\n")
            file.write(f"{trying + 1} Trying\n")
            file.write(f"Scored {info['score']} out of {env.get_max_score()}, total steps: {len(scores)}\n")
            file.write(f"Scores: {scores}\n")
            file.write(f"Rewards: {rewards}\n")
            file.write("============================================================================================================================\n")
            file.write("\n\n\n\n\n\n\n\n")


def walkthrough_pipeline(config):
    graph_name = "Detective_bigraph_walkthrough_gpt"
    load = False
    graph = KnowledgeSemiBiGraph(graph_name, load)
    agent = GPTagent()
    env = FrotzEnv("z-machine-games-master/jericho-game-suite/detective.z5")
    walkthrough = env.get_walkthrough()
    start = 1
    n_steps = 150
    print_steps = n_steps
    # K, M, maxIters, eps, damping = 150, 250, None, 1e-5, 1
    observations = []
    observation, info = env.reset()
    observations.append({"observation": observation, "trying": 1, "step": 0})
    done = False
    rewards, scores = [], []
    action = "start"
    steps_from_reflection = 0
    reflection = {"insight": "Still nothing", "trying": 1}
    prev_action = "just_start_game"
    d = {"S": "south", "N": "north", "W": "west", "E": "east", "s": "south", "n": "north", "w": "west", "e": "east"}
    for step, action in enumerate(walkthrough):
        if action in d:
            action = d[action]
        action = action.lower()
        old_obs = observation
        location = env.get_player_location().name
        valid_actions = env.get_valid_actions()

        observed_items, remembered_items = agent.bigraph_processing(observations, observation, location, 
                        valid_actions, 8, step + 1)
        # observed_items, remembered_items = [{"table": [1]}], [{"table": [1]}]
        state_key = f'''
Observation: {observation}
Location: {location}
'''         
        state_embedding = agent.get_embedding_local(state_key, True)
        action_embedding = agent.get_embedding_local(action)
        graph.add_state(observation, prev_action, action_embedding, location, 8, step + 1, state_embedding)
        graph.observe_items(observed_items, observation, location, state_embedding)
        remembered_items.append({action: action_embedding})
        graph.remember_items(remembered_items, observation, location, state_embedding)
        graph.save()

        # filtered_items = [graph.get_item(list(item.keys())[0], list(item.values())[0])["name"] for item in remembered_items if graph.get_item(list(item.keys())[0], list(item.values())[0]) is not None]
        # associations, experienced_actions, n = graph.get_associations(filtered_items)
        # action, use_graph, is_random, insight = agent.choose_action(observations, observation, location, 
        #                 valid_actions, 0, step, reflection,
        #                 associations, experienced_actions, steps_from_reflection > -1, n, inventory)
        # use_graph = use_graph or steps_from_reflection > 10
        # if use_graph:
        #     steps_from_reflection = 0
        #     reflection = reflect(graph, agent, filtered_items)
        #     reflection = {"insight": reflection, "trying": 1, "step": step + 1}
        #     action, is_random, insight = agent.choose_action_with_reflection(observations, observation, location, 
        #                 valid_actions, 0, step,
        #                 associations, experienced_actions, reflection, n, inventory)
        # else:
        #     steps_from_reflection += 1
        
        graph.add_insight("This is walkthrough", observation, location, state_embedding)

        state_key = f'''
Observation: {observation}
Location: {location}
'''    
        state_embedding = agent.get_embedding_local(state_key, True)
        state_key = graph.get_state_key(state_key, state_embedding)
        new_obs = graph.get_string_state(state_key) + f"\nAction that led to this: {prev_action}"
        observations.append(new_obs)
        
        # action = agent.choose_action_vanilla(observations, observation, inventory, location, valid_actions)

        observation, reward, done, info = env.step(action)
        inventory = [item.name for item in env.get_inventory()]
        observation += f"\nInventory: {inventory}"
        valid_actions = env.get_valid_actions()
        observation += f"\nValid actions (just recommendation): {valid_actions}"
        prev_action = action

        rewards.append(reward)
        scores.append(info['score'])
        if step < print_steps:
            with open("walkthrough_log.txt", "a") as file:
                file.write(f"Step: {step + 1}\n")
                # file.write(f"Branches: {branches}\n")
                # file.write(f"Is action chosen: {is_random}\n")
                file.write(f"Location: {location}\n")
                file.write(f"Observation: {old_obs}\n")
                # file.write(f"Inventory: {inventory}\n")
                temp = [list(item.keys())[0] for item in observed_items]
                file.write(f"Observed items: {temp}\n")
                # file.write(f"insight: {insight}\n")
                temp = [list(item.keys())[0] for item in remembered_items]
                file.write(f"Remembered items: {temp}\n")
                # file.write(f"associations: {associations}\n")
                # file.write(f"Experienced actions: {experienced_actions}\n")
                # file.write(f"Use graph: {use_graph}\n")
                file.write(f"Summary: {reflection}\n")
                file.write(f"Valid actions: {valid_actions}\n")
                file.write(f"Chosen action: {action}\n")
                file.write(f"Reward: {reward}\n")
                file.write("====================================================================\n")
        if done:
            with open("walkthrough_log.txt", "a") as file:
                    file.write(f"{observation}\n")
            observation = "***".join(observation.split("***")[:-1])
            state_key = f'''
Observation: {observation}
Location: {location}
'''    
            state_embedding = agent.get_embedding_local(state_key, True)
            action_embedding = agent.get_embedding_local(action)
            graph.add_state(observation, action, action_embedding, location, 8, step + 2, state_embedding)
            graph.add_insight("Game over", observation, location, state_embedding)
            break
    with open("walkthrough_log.txt", "a") as file:        
        file.write("============================================================================================================================\n")
        file.write(f"{8} Trying\n")
        file.write(f"Scored {info['score']} out of {env.get_max_score()}, total steps: {len(scores)}\n")
        file.write(f"Scores: {scores}\n")
        file.write(f"Rewards: {rewards}\n")
        file.write("============================================================================================================================\n")
        file.write("\n\n\n\n\n\n\n\n")


