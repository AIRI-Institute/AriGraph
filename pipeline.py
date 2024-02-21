from jericho import FrotzEnv

from agent_detective import GPTagent
from graph import KnowledgeGraph
from semi_bigraph import KnowledgeSemiBiGraph

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

def bigraph_pipeline(config):
    graph_name = "Detective_bigraph"
    load = False
    graph = KnowledgeSemiBiGraph(graph_name, load)
    agent = GPTagent()
    env = FrotzEnv("z-machine-games-master/jericho-game-suite/detective.z5")
    n_trying = 9
    start = 1
    n_steps = 100
    print_steps = n_steps
    # K, M, maxIters, eps, damping = 150, 250, None, 1e-5, 1
    observations = []
    for trying in range(start - 1, start - 1 + n_trying):
        observation, info = env.reset()
        observations.append({"observation": observation, "trying": trying + 1, "step": 0})
        done = False
        rewards, scores = [], []
        action = "start"
        steps_from_reflection = 0
        reflection = {"insight": "Still nothing", "trying": trying + 1}
        for step in range(n_steps):
            old_obs = observation
            inventory = [item.name for item in env.get_inventory()]
            location = env.get_player_location().name
            valid_actions = env.get_valid_actions()

            observed_items, remembered_items = agent.bigraph_processing(observations, observation, location, 
                            valid_actions, trying + 1, step + 1, inventory)
            state_key = f'''
Observation: {observation}
Location: {location}
'''         
            state_embedding = agent.get_embedding_local(state_key)
            graph.add_state(observation, action, location, trying + 1, step + 1, inventory, state_embedding)
            graph.observe_items(observed_items, observation, location, state_embedding)
            graph.remember_items(remembered_items, observation, location, state_embedding)
            graph.save()

            filtered_items = [graph.get_item(list(item.keys())[0], list(item.values())[0])["name"] for item in remembered_items if graph.get_item(list(item.keys())[0], list(item.values())[0]) is not None]
            associations, experienced_actions, n = graph.get_associations(filtered_items)
            action, use_graph, is_random, insight = agent.choose_action(observations, observation, location, 
                            valid_actions, trying, step, reflection,
                            associations, experienced_actions, steps_from_reflection > -1, n, inventory)
            use_graph = use_graph or steps_from_reflection > 10
            if use_graph:
                steps_from_reflection = 0
                reflection = reflect(graph, agent, filtered_items)
                reflection = {"insight": reflection, "trying": trying + 1, "step": step + 1}
                action, is_random, insight = agent.choose_action_with_reflection(observations, observation, location, 
                            valid_actions, trying, step,
                            associations, experienced_actions, reflection, n, inventory)
            else:
                steps_from_reflection += 1
            graph.add_insight(insight, observation, location)

            state_key = f'''
Observation: {observation}
Location: {location}
'''    
            state_embedding = agent.get_embedding_local(state_key)
            state_key = graph.get_state_key(state_key, state_embedding)
            observations.append(graph.get_string_state(state_key))
            
            # action = agent.choose_action_vanilla(observations, observation, inventory, location, valid_actions)

            observation, reward, done, info = env.step(action)

            rewards.append(reward)
            scores.append(info['score'])
            if step < print_steps:
                with open("game_log.txt", "a") as file:
                    file.write(f"Step: {step + 1}\n")
                    file.write(f"Is action chosen: {is_random}\n")
                    file.write(f"Location: {location}\n")
                    file.write(f"Observation: {old_obs}\n")
                    file.write(f"Inventory: {inventory}\n")
                    temp = [list(item.keys())[0] for item in observed_items]
                    file.write(f"Observed items: {temp}\n")
                    file.write(f"insight: {insight}\n")
                    temp = [list(item.keys())[0] for item in remembered_items]
                    file.write(f"Remembered items: {temp}\n")
                    file.write(f"associations: {associations}\n")
                    file.write(f"Experienced actions: {experienced_actions}\n")
                    file.write(f"Use graph: {use_graph}\n")
                    file.write(f"Summary: {reflection}\n")
                    file.write(f"Valid actions: {valid_actions}\n")
                    file.write(f"Chosen action: {action}\n")
                    file.write(f"Reward: {reward}\n")
                    file.write("====================================================================\n")
            if done:
                with open("game_log.txt", "a") as file:
                    file.write(f"{observation}\n")
                observation = "***".join(observation.split("***")[:-1])
                state_key = f'''
Observation: {observation}
Location: {location}
'''    
                state_embedding = agent.get_embedding_local(state_key)
                graph.add_state(observation, action, location, trying + 1, step + 2, inventory, state_embedding)
                graph.add_insight("Game over", observation, location, state_embedding)
                break
        with open("game_log.txt", "a") as file:        
            file.write("============================================================================================================================\n")
            file.write(f"{trying + 1} Trying\n")
            file.write(f"Scored {info['score']} out of {env.get_max_score()}, total steps: {len(scores)}\n")
            file.write(f"Scores: {scores}\n")
            file.write(f"Rewards: {rewards}\n")
            file.write("============================================================================================================================\n")
            file.write("\n\n\n\n\n\n\n\n")


def walkthrough_pipeline(config):
    graph_name = "Detective_bigraph_walkthrough"
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
    for step, action in enumerate(walkthrough):
        old_obs = observation
        inventory = [item.name for item in env.get_inventory()]
        location = env.get_player_location().name
        valid_actions = env.get_valid_actions()

        observed_items, remembered_items = agent.bigraph_processing(observations, observation, location, 
                        valid_actions, 1, step + 1, inventory)
        graph.add_state(observation, action, location, 1, step + 1, inventory)
        graph.observe_items(observed_items, observation, location)
        graph.remember_items(remembered_items, observation, location)
        graph.save()

        filtered_items = [graph.get_item(list(item.keys())[0], list(item.values())[0])["name"] for item in remembered_items if graph.get_item(list(item.keys())[0], list(item.values())[0]) is not None]
        associations, experienced_actions, n = graph.get_associations(filtered_items)
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
        graph.add_insight("This is walkthrough", observation, location)

        state_key = f'''
Observation: {observation}
Location: {location}
'''    
        state_embedding = agent.get_embedding_local(state_key)
        state_key = graph.get_state_key(state_key, state_embedding)
        observations.append(graph.get_string_state(state_key))
        
        # action = agent.choose_action_vanilla(observations, observation, inventory, location, valid_actions)

        observation, reward, done, info = env.step(action)

        rewards.append(reward)
        scores.append(info['score'])
        if step < print_steps:
            print("Step:", step + 1)
            print("Location:", location)
            print("Observation:", old_obs)
            print("Inventory:", inventory)
            print("Observed items:", [list(item.keys())[0] for item in observed_items])
            print("Remembered items:", [list(item.keys())[0] for item in remembered_items])
            print("associations:", associations)
            print("Experienced actions:", experienced_actions)
            print("Summary:", reflection)
            print("Valid actions:", valid_actions)
            print("Chosen action:", action)
            print("Reward:", reward)
            print("====================================================================")
        if done:
            print(observation)
            observation = "***".join(observation.split("***")[:-1]) if "***" in observation else observation
            graph.add_state(observation, action, location, 1, step + 2, inventory)
            graph.add_insight("Game over", observation, location)
            break

    print("============================================================================================================================")
    print(f"Scored {info['score']} out of {env.get_max_score()}, total steps: {len(scores)}")
    print(f"Scores: {scores}")
    print(f"Rewards: {rewards}")
    print("============================================================================================================================")
    print("\n\n\n\n\n\n\n\n")


