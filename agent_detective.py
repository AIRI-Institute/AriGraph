import requests
import numpy as np
from time import time, sleep
from InstructorEmbedding import INSTRUCTOR
from scipy.spatial.distance import cosine

VPS_IP = "176.222.54.59"
API_KEY = "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"

class GPTagent:
    def __init__(self, model = "gpt-4-1106-preview", system_prompt = None):
        self.system_prompt = '''
        Your objective is to navigate through the interactive world of a text-based 
        detective game. You are a detective in a fictional world filled with puzzles, clues and ill-wishers. 
        Your goal is to explore this world, avoiding dangers and following clues, and ultimately find the way to achieve the highest score possible. 
        Remember, the game involves navigating through various locations, 
        interacting with objects, and understanding the consequences of your actions. 

Key points to remember:
1. Pay attention to the descriptions given by the game. They contain crucial information for solving puzzles and moving forward.
2. You can interact with the environment using simple actions.
3. Keep track of your inventory and the locations you have visited. This information is critical for solving puzzles.
4. Think creatively and try different approaches if you are stuck.
5. Prioritize your safety. Avoid dangerous situations that could end the game prematurely.
6. Avoid repeating situations, play more creative and different when such situations repeat.
7. Your game history is writing to knowledge graph, sometimes I give you needful information about previous experience, please, pay attention to number of attempt and game step. 
''' if system_prompt is None else system_prompt
        self.model = model
        self.instructor = INSTRUCTOR('hkunlp/instructor-large')
        
    def generate(self, prompt):
        messages = [{"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}]

        response = requests.post(
            f"http://{VPS_IP}:8000/openai_api",
            json={"api_key": API_KEY, "messages": messages, "model_type": self.model}
        )
        resp = response.json()["response"]
        sleep(8)
        return resp
    
    def process_triplets(self, raw_triplets):
        raw_triplets = raw_triplets.split(";")
        triplets = []
        for triplet in raw_triplets:
            if len(triplet.split(",")) > 3:
                continue
            elif len(triplet.split(",")) < 3:
                continue
            else:
                subj, relation, obj = triplet.split(",")
                subj, relation, obj = subj.strip(" \n"), relation.strip(" \n"), obj.strip(" \n")
                if len(subj) == 0 or len(relation) == 0 or len(obj) == 0:
                    continue
                triplets.append([
                    {"name": subj, "embedding": self.get_embedding_local(subj)},
                    {"name": relation, "embedding": self.get_embedding_local(relation)},
                    {"name": obj, "embedding": self.get_embedding_local(obj)}
                ])
            
        return triplets
    
    def process_objects(self, needful_objects):
        objects = needful_objects.split(";")
        return [self.get_embedding_local(obj.strip(" \n")) for obj in objects if len(obj.strip(" \n")) > 0]
    
    def process_action(self, action, valid_actions):
        action = action.strip(" \n")
        if len(action) == 0:
            return valid_actions[0]
        if action in valid_actions:
            return action
        act_emb = self.get_embedding_local(action)
        scores = [cosine(act_emb, self.get_embedding_local(action)) for action in valid_actions]
        idx = np.argmin(scores)
        return valid_actions[idx]

    def process_bigraph_response(self, response):
        observed_items, remembered_items = \
            [], []
        if "Crucial things: " in response:
            observed_items = response.split("Crucial things: ")[1].split(";")[0].strip("[]").split(",")
            for i in range(len(observed_items)):
                observed_items[i] = observed_items[i].strip(" \n.")
                observed_items[i] = { observed_items[i]: self.get_embedding_local(observed_items[i]) }
        if "Potentially useful things: " in response:
            remembered_items = response.split("Potentially useful things: ")[1].split(";")[0].strip("[]").split(",")
            for i in range(len(remembered_items)):
                remembered_items[i] = remembered_items[i].strip(" \n.")
                remembered_items[i] = { remembered_items[i]: self.get_embedding_local(remembered_items[i]) }
        
        return observed_items, remembered_items

    def get_embedding_local(self, text):
        text = text.replace("\n", " ")
        instruction = "Represent the entity in knowledge graph:"
        embeddings = self.instructor.encode([[instruction, text]])
        return list(map(float, list(embeddings[0])))
    
    def get_embedding(self, text):
        response = requests.post(
            f"http://{VPS_IP}:8000/openai_api_embedding",
            json={"api_key": API_KEY, "messages": [text], "model_type": "text-embedding-ada-002"}
        )
        emb = response.json()["response"]
        sleep(8)
        return emb
    
    def get_new_memories(self, observation):
        prompt = f'## 1. Overview\n\
Your task is to extract information from game observation in structured formats to build a knowledge graph.\n\
- **Nodes** represent entities and concepts. They are akin to Wikipedia nodes.\n\
- The aim is to achieve simplicity and clarity in the knowledge graph, making it useful for you in the future.\n\
- Use the following triplet format for extracted data: "triplet1; triplet2; ...", more detailed - "subject1, relation1, object1; subject2, relation2, object2; ...", where a triplet is "subject1, relation1, object1" or "subject2, relation2, object2".\n\
- For example, from the text "Albert Einstein, born in Germany, is known for developing the theory of relativity" you should extract the following data: "Albert Einstein, country, Germany; Albert Einstein, developed, Theory of relativity".\n\
- Both subject and object in triplets should be akin to Wikipedia nodes. Object can be a date or number, objects should not contain citations or sentences.\n\
- Instead of generating complex objects, divide triplet with complex object into two triplets with more precise objects. For example, the text "John Doe is a developer at Google" corresponds to two triplets: "John Doe, position, developer; John Doe, employed by, Google".\n\
- Exclude from the extracted data triplets where subject or object are collective entities such as "People".\n\
- Exclude from the extracted data triplets where object is a long phrase with more than 5 words.\n\
- Similar relations, such as "has friend" and "friend of", replace with uniform relation, for example, "has friend"\n\
- Similar entities, such as "House" and "house" or "small river" and "little river", replace with uniform relation, for example, "house" or "small river"\n\
## 2. Coreference Resolution\n\
- **Maintain Entity Consistency**: When extracting entities, it is vital to ensure consistency.\n\
If an entity, such as "John Doe", is mentioned multiple times in the text but is referred to by different names or pronouns (e.g., "Joe", "he"), \n\
always use the most complete identifier for that entity throughout the knowledge graph. In this example, use "John Doe" as the entity ID. \n\
Remember, the knowledge graph should be coherent and easily understandable, so maintaining consistency in entity references is crucial. \n\
Observation:\n\
{observation} \n\
Extracted data: \n'
        raw_triplets = self.generate(prompt)
        triplets = self.process_triplets(raw_triplets)
        return triplets
    
    def query(self, observation, inventory, location, valid_actions):
        prompt = f'''
I will provide you with your current observation, your inventory, your location and a list of possible actions to take. Your task is to choose which objects (events, places, objects, etc.) you would like to get information from external memory. Please don't ask for too much (more than 10 objects) and too little (less than 3 objects). The response must be in the format "Object1; Object2;...".
Observation: {observation} 
Inventory: {inventory} 
Location: {location} 
Possible actions: {valid_actions} 
'''
        needful_objects = self.generate(prompt)
        print("Needful objects", needful_objects)
        source_embeddings = self.process_objects(needful_objects)
        return source_embeddings
    
    def act(self, observation, needful_memories, inventory, location, valid_actions):
        for i in range(len(needful_memories)):
            needful_memories[i][0] = needful_memories[i][0]["name"]
            needful_memories[i][1] = needful_memories[i][1]["name"]
            needful_memories[i][2] = needful_memories[i][2]["name"]
        prompt = f'''
I will provide you with needful knowledges in format of triplets "subject, relation, object" about game environment (include knowledges from previous games). 
I will also provide you with your current observation, your inventory, your location and a list of possible actions to take. Your task is to select the best action. Answer only with this action.
Needful knowledges: {needful_memories}
Observation: {observation} 
Inventory: {inventory} 
Location: {location} 
Possible actions: {valid_actions} 
'''
        action = self.generate(prompt)
        print("action:", action)
        action = self.process_action(action, valid_actions)
        return action
    
    def reflection_on_action(self, old_obs, observation, action, reward):
        prompt = f'''
While playing game you turned up in following situation: "{old_obs}"
In this situation you preferred to do following action: "{action}"
This action led to following reward: "{reward}" and following situation: "{observation}".

Your task is to extract needful to future game information from your action based on previous situation and current situation. This information must be in structured formats to build a knowledge graph.
- **Nodes** represent entities and concepts. They are akin to Wikipedia nodes.
- The aim is to achieve simplicity and clarity in the knowledge graph, making it useful for you in the future.
- Use the following triplet format for extracted data: "triplet1; triplet2; ...", more detailed - "subject1, relation1, object1; subject2, relation2, object2; ...", where a triplet is "subject1, relation1, object1" or "subject2, relation2, object2".
- For example, from the text "Albert Einstein, born in Germany, is known for developing the theory of relativity" you should extract the following data: "Albert Einstein, country, Germany; Albert Einstein, developed, Theory of relativity".
- Both subject and object in triplets should be akin to Wikipedia nodes. Object can be a date or number, objects should not contain citations or sentences.
- Instead of generating complex objects, divide triplet with complex object into two triplets with more precise objects. For example, the text "John Doe is a developer at Google" corresponds to two triplets: "John Doe, position, developer; John Doe, employed by, Google".
- Exclude from the extracted data triplets where subject or object are collective entities such as "People".
- Exclude from the extracted data triplets where object is a long phrase with more than 5 words.
- Similar relations, such as "has friend" and "friend of", replace with uniform relation, for example, "has friend"
- Similar entities, such as "House" and "house" or "small river" and "little river", replace with uniform relation, for example, "house" or "small river"
## 2. Coreference Resolution
- **Maintain Entity Consistency**: When extracting entities, it is vital to ensure consistency.
If an entity, such as "John Doe", is mentioned multiple times in the text but is referred to by different names or pronouns (e.g., "Joe", "he"), 
always use the most complete identifier for that entity throughout the knowledge graph. In this example, use "John Doe" as the entity ID. 
Remember, the knowledge graph should be coherent and easily understandable, so maintaining consistency in entity references is crucial. 
Extracted data: 
'''
        raw_triplets = self.generate(prompt)
        triplets = self.process_triplets(raw_triplets)
        return triplets

    def bigraph_processing(self, observations, observation, location, 
                            valid_actions, trying, step, inventory):
        prompt = f'''
Previous 2 observations: {observations[-2:]} 
Current observation: {observation}
Location: {location} 
Inventory: {inventory}
Recommended actions (may not contain all useful actions, it is a recommendation): {valid_actions} 
Number of current attempt: {trying}
Step number on the current attempt: {step}

Please, based on given information choose things that relative to current situation. This things may be items or tools, locations, surrounding stuff,
creatures and etc. This things also may be your thoughts about current situation. Things must NOT include any actions and must be named shortly (no longer than 3 words).
Example:
    Situation: You are at small square near the library. Apple and flashlight are in your hands, you hear bird's song and woman's cry. You are fearing.
    Crucial things: [small square, library, apple, flashlight, bird, bird's song, woman, woman's cry, fear, help, running]  

Next, based on given information, name things which might be useful
at current situation. Things must be named like Crucial things. 
Example:
    Situation: You are at small square near the library. Apple and flashlight are in your hands, you hear bird's song and woman's cry. You are fearing.
    Potentially useful things: [pistol, police, partner, flashlight, cry, help]  

Warning! Answer must be in following format:
Crucial things: [thing_1, thing_2, ...];
Potentially useful things: [thing_1, thing_2, ...];

Pay attention that if you mislead format of answer, action might be incorrect
and game consequences will be unexpected.
'''
        response = self.generate(prompt)
        observed_items, remembered_items = \
            self.process_bigraph_response(response)

        return observed_items, remembered_items
    
#     def choose_action(self, observations, observation, inventory, location, 
#                             valid_actions, trying, step, reflection,
#                             associations, experienced_actions, allow_reflection, n):
#         prompt = f'''
# Previous 4 observations: {observations[-4:]} 
# Current observation: {observation}
# Inventory: {inventory} 
# Location: {location} 
# Your associations: {associations}
# Your plan which is based on knowledge graph: {reflection}
# How many times you have visited this state (include current one): {n}
# Actions which you tried at previous steps (useful for repeat good moves and effective exploration): {experienced_actions}
# Recommended actions (may not contain all useful actions, it is a recommendation): {valid_actions} 
# Number of current attempt: {trying}
# Step number on the current attempt: {step}
# Allow using knowledge graph: {allow_reflection}

# Please, based on given information give some reasoning about current situation and choose an action to perform in the game. 
# Remember that action must be valid for Detective game, otherwise game consequences will be unexpected.
# If you nave not a sufficient reason to ignore plan, please follow it.
# If you want to use knowledge graph for summarizing information you collected before and produce new plan, 
# you can do it with specific action "use graph" (which is valid when "Allow using knowledge graph" is True).
# Use graph when you repeat actions or for navigation, for solving difficult puzzles with several steps plan
# or in case when you need new plan.

# Warning! Your answer must contain your reasoning about current situation and
# action you want to perform (if you want to use knowledge graph, action must be "use graph", any another answer will be 
# process as Detective game action). Format of answer:
# Reasoning: your reasoning
# Chosen action: action
# '''
#         response = self.generate(prompt)
#         action = response.split("Chosen action: ")[-1] if "Chosen action: " in response else np.random.choice(valid_actions)
#         use_graph = action == "use graph" and allow_reflection
#         return action, use_graph, "Chosen action: " in response
    
#     def choose_action_with_reflection(self, observations, observation, inventory, location, 
#                             valid_actions, trying, step, 
#                             associations, experienced_actions, reflection, n):
#         prompt = f'''
# Previous 4 observations: {observations[-4:]} 
# Current observation: {observation}
# Inventory: {inventory} 
# Location: {location} 
# Your associations: {associations}
# How many times you have visited this state (include current one): {n}
# Actions which you tried at previous steps (useful for repeat good moves and effective exploration): {experienced_actions}
# Recommended actions (may not contain all useful actions, it is a recommendation): {valid_actions} 
# Number of current attempt: {trying}
# Step number on the current attempt: {step}
# Your plan which is based on knowledge graph: {reflection}

# Please, based on given information give some reasoning about current situation and choose an action to perform in the game. 
# Remember that action must be valid for Detective game, otherwise game consequences will be unexpected.
# If you nave not a sufficient reason to ignore plan, please follow it.

# Warning! Your answer must contain your reasoning about current situation and
# action you want to perform. Format of answer:
# Reasoning: your reasoning
# Chosen action: action
# '''
#         response = self.generate(prompt)
#         action = response.split("Chosen action: ")[-1] if "Chosen action: " in response else np.random.choice(valid_actions)
#         return action, "Chosen action: " in response
    
    def choose_action(self, observations, observation, location, 
                            valid_actions, trying, step, reflection,
                            associations, experienced_actions, allow_reflection, n, inventory):
        prompt = f'''
Previous 2 observations: {observations[-2:]} 
Current observation: {observation}
Location: {location} 
Inventory: {inventory}
Your associations: {associations}
Your plan which is based on knowledge graph: {reflection}
How many times you have visited this state (include current one): {n}
Actions which you tried at previous steps (useful for repeat good moves and effective exploration): {experienced_actions}
Recommended actions (may not contain all useful actions, it is a recommendation): {valid_actions} 
Number of current attempt: {trying}
Step number on the current attempt: {step}

Please, based on given information give some reasoning about current situation. Reasoning must contain 
crucial information about player state, based on this reasoning will be perform an action in the game.
Please, ignore all information which is useless to make current decision. Please, DO NOT make a decision,
just collect crucial information for it.

After reasoning make plan at two or three steps forward and write them after reasoning. Your reasoning must be a paragraph of text,
your plan must be another paragraph of text.

'''
        response = self.generate(prompt)
        prompt = f'''
{response}

Allow using knowledge graph: {allow_reflection}
Recommended actions (may not contain all useful actions, it is a recommendation): {valid_actions} 

Based on this information, choose an action to perform in the game. Your answer must contain ONLY action you chose without any descriptions.
If you want to use knowledge graph for summarizing information you collected before and produce new plan, 
you can do it with specific action "use graph" (which is valid when "Allow using knowledge graph" is True).
Use graph when you repeat actions or for navigation, for solving difficult puzzles with several steps plan
or in case when you need new plan. Please choose ONLY action which is valid for Detective game. 
Pay attention that if you mislead format of answer, action might be incorrect
and game consequences will be unexpected.
Action: 
'''
        action = self.generate(prompt)
        # action = response.split("Chosen action: ")[-1] if "Chosen action: " in response else np.random.choice(valid_actions)
        use_graph = action == "use graph" and allow_reflection
        return action, use_graph, "Chosen action: " in response, response
    
    def choose_action_with_reflection(self, observations, observation, location, 
                            valid_actions, trying, step, 
                            associations, experienced_actions, reflection, n, inventory):
        prompt = f'''
Previous 2 observations: {observations[-2:]} 
Current observation: {observation}
Location: {location} 
Inventory: {inventory}
Your associations: {associations}
How many times you have visited this state (include current one): {n}
Actions which you tried at previous steps (useful for repeat good moves and effective exploration): {experienced_actions}
Number of current attempt: {trying}
Step number on the current attempt: {step}
Your plan which is based on knowledge graph: {reflection}

Please, based on given information give some reasoning about current situation. Reasoning must contain 
crucial information about player state, based on this reasoning will be perform an action in the game.
Please, ignore all information which is useless to make current decision. Please, DO NOT make a decision,
just collect crucial information for it.

After reasoning make plan at two or three steps forward and write them after reasoning. Your reasoning must be a paragraph of text,
your plan must be another paragraph of text.
'''
        response = self.generate(prompt)
        prompt = f'''
{response}

Recommended actions (may not contain all useful actions, it is a recommendation): {valid_actions} 

Based on this information, choose an action to perform in the game. Your answer must contain ONLY action you chose without any descriptions.
Please choose ONLY action which is valid for Detective game. Pay attention that if you mislead format of answer, action might be incorrect
and game consequences will be unexpected.
Action: 
'''
        action = self.generate(prompt)
        # action = response.split("Chosen action: ")[-1] if "Chosen action: " in response else np.random.choice(valid_actions)
        return action, "Chosen action: " in response, response
    
    def get_new_summary(self, summary, next_state):
        prompt = f'''
Previous plan: {summary}
Observation: {next_state}

Please, update Previous plan with information from Observation. You should remove useless or inactual information and steps
from Previous plan and add to it relevant information from Observation. Feel free to change plan sufficiently 
if you think it is necessary. Plan must contain concrete game steps (in form of actions) and rarely may contain some reasoning about chosen steps.
Please, make simple and concrete plan, keep length of plan not more than 500 words and no more than 7 actions. 
Your answer will be interpret as a new plan and will be used for playing Detective game. After formulate 
new plan, name things (tools, items, rooms, entities, creatures, thoughts and etc.) which is relevant to it. 
Things must be named shortly (no longer than 3 words). Things must NOT include any actions.

Warning! Answer must be in following format:
New plan: generated plan
Relevant things: [thing_1, thing_2, ...]
'''
        response = self.generate(prompt)
        summary = response.split("New plan: ")[1].split("Relevant things: ")[0].strip(" \n") if "New plan: " in response else summary
        items = response.split("Relevant things: ")[1].strip("[]").split(",") if "Relevant things: " in response else []
        return summary, items

    def choose_action_vanilla(self, observations, observation, inventory, location, 
                            valid_actions):
        prompt = f'''
Previous 4 observations: {observations[-4:]} 
Current observation: {observation}
Inventory: {inventory} 
Location: {location} 
Recommended actions (may not contain all useful actions, it is a recommendation): {valid_actions} 

Please, based on given information give some reasoning about current situation and choose an action to perform in the game. 
Remember that action must be valid for Detective game, otherwise game consequences will be unexpected.

Warning! Your answer must contain your reasoning about current situation and
action you want to perform (if you want to use knowledge graph, action must be "use graph", any another answer will be 
process as Detective game action). Format of answer:
Reasoning: your reasoning
Chosen action: action
'''
        response = self.generate(prompt)
        action = response.split("Chosen action: ")[-1] if "Chosen action: " in response else np.random.choice(valid_actions)
        return action
        