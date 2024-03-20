import requests
import numpy as np
import torch
from time import time, sleep
from InstructorEmbedding import INSTRUCTOR
from scipy.spatial.distance import cosine
from transformers import AutoTokenizer, AutoModelForCausalLM

VPS_IP = "146.0.73.157"
port = 8000
# VPS_IP = "176.222.54.59"
# port = 8000
API_KEY = "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"

class GPTagent:
    def __init__(self, model = "gpt-4-1106-preview", system_prompt = None):
        self.system_prompt = '''
        Your objective is to navigate through the interactive world of a text-based game. 
        Remember, the game involves navigating through various locations, 
        interacting with objects, and understanding the consequences of your actions. Try to explore world and collect treasures and clues.

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
        
    def generate(self, prompt, t = 1):
        messages = [{"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}]

        response = requests.post(
            f"http://{VPS_IP}:{port}/openai_api",
            json={"api_key": API_KEY, "messages": messages, "model_type": self.model, "temperature": t}
        )
        resp = response.json()["response"]
        sleep(8)
        return resp

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
    
    def is_equal(self, text_1, text_2, threshold, is_state = True):
        embedding_1, embedding_2 = self.get_embedding_local(text_1, is_state), self.get_embedding_local(text_2, is_state)
        return cosine(embedding_1, embedding_2) < threshold

    def get_embedding_local(self, text, is_state = False):
        text = text.replace("\n", " ")
        instruction = "Represent the entity in knowledge graph:" if not is_state else \
            "There is a description of game state. Pay attention to location and inventory. Location and inventory are the most crucial parameters."
        embeddings = self.instructor.encode([[instruction, text]])
        return list(map(float, list(embeddings[0])))

    def bigraph_processing(self, observations, observation):
        prompt = f'''####
Previous observations: {observations[-1:]} 
####
Current observation: {observation}
####

Please, based on given information choose things that relative to current situation. This things may be items or tools, locations, surrounding stuff,
creatures and etc. This things also may be your thoughts about current situation. Things must be named shortly (no longer than 3 words). 
You shouldn't include any actions.
Example:
    Situation: You are at small square near the library. Apple and flashlight are in your hands, you hear bird's song and woman's cry. You are fearing.
    Crucial things: [small square, library, apple, flashlight, bird, bird's song, woman, woman's cry, fear, help, running]  

Next, based on given information, name things which might be useful
at current situation. Things must be named like Crucial things. If yo want to include actions, choose only crucial ones.
Example:
    Situation: You are at small square near the library. Apple and flashlight are in your hands, you hear bird's song and woman's cry. You are fearing.
    Potentially useful things: [pistol, police, partner, flashlight, cry, help, run]  

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
    
    def choose_action(self, true_graph, observations, observation, valid_actions, allow_reflection):
        prompt = f'''
Your knowledges about game: {true_graph}
####
Previous 2 states: {observations[-2:]} 
####
Current observation: {observation} 
####

Based on this information, choose an action to perform in the game. Your answer must contain short reasoning about current situation
and action you chose without any descriptions.
Pay attention that if you mislead format of answer, action might be incorrect
and game consequences will be unexpected.

Warning! Your answer must contain your reasoning about current situation and
action you want to perform. Format of answer:
Reasoning: your reasoning
Chosen action: action'''
        response = self.generate(prompt)
        action = response.split("Chosen action: ")[-1] if "Chosen action: " in response else np.random.choice(valid_actions)
        use_graph = action == "use graph" and allow_reflection
        return action, use_graph, "Chosen action: " in action, response.split("Reasoning: ")[-1].split("\n")[0]
        
        
class MixtralAgent(GPTagent):
    def __init__(self, model = "gpt-4-1106-preview", system_prompt = None):
        super().__init__(model, system_prompt)
        self.tokenizer = AutoTokenizer.from_pretrained("mistralai/Mixtral-8x7B-Instruct-v0.1")
        self.mixtral = AutoModelForCausalLM.from_pretrained("mistralai/Mixtral-8x7B-Instruct-v0.1", device_map = "auto", torch_dtype = torch.bfloat16)    
        self.device = list(self.mixtral.parameters())[0].device
        
    def t(self, text):
        return self.tokenizer.encode(text, add_special_tokens=False)    
        
    def generate(self, prompt):
        prompt = f"<s>[INST] {self.system_prompt} Hi [/INST] Hello! how can I help you</s>[INST] {prompt} [/INST]"
        inputs = self.tokenizer.encode(prompt, return_tensors="pt", add_special_tokens = False).to(self.device)
        outputs = self.mixtral.generate(inputs, max_new_tokens=1024, do_sample=True)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    
        

        
