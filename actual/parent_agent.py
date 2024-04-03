import requests
import numpy as np
import torch
from time import time, sleep
from InstructorEmbedding import INSTRUCTOR
from scipy.spatial.distance import cosine

from utils import *
from prompts import *

VPS_IP = "146.0.73.157"
port = 8000
API_KEY = "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"

class GPTagent:
    def __init__(self, model, system_prompt, goal_freq = 10):
        self.system_prompt = system_prompt
        self.model = model
        self.instructor = INSTRUCTOR('hkunlp/instructor-large')
        self.achieved_goals, self.goal = [], None
        self.goal_freq = goal_freq
        self.goals = []
        self.total_amount = 0
        
    def generate(self, prompt, t = 1, jsn = False):
        messages = [{"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}]

        response = requests.post(
            f"http://{VPS_IP}:{port}/openai_api",
            json={"api_key": API_KEY, "messages": messages, "model_type": self.model, "temperature": t, "jsn": jsn}
        )
        resp = response.json()["response"]
        usage = response.json()["usage"]
        cost = usage["completion_tokens"] * 3 / 100000 + usage["prompt_tokens"] * 1 / 100000
        self.total_amount += cost
        sleep(1)
        return resp, cost
    
    def is_equal(self, text_1, text_2, threshold, is_state = True):
        embedding_1, embedding_2 = self.get_embedding_local(text_1, is_state), self.get_embedding_local(text_2, is_state)
        return cosine(embedding_1, embedding_2) < threshold

    def get_embedding_local(self, text, is_state = False):
        text = text.replace("\n", " ")
        instruction = "Represent the entity in knowledge graph:" if not is_state else \
            "There is a description of game state. Pay attention to location and inventory. Location and inventory are the most crucial parameters."
        embeddings = self.instructor.encode([[instruction, text]])
        return list(map(float, list(embeddings[0])))
    
    def get_embedding(self, text):
        response = requests.post(
            f"http://{VPS_IP}:8000/openai_api_embedding",
            json={"api_key": API_KEY, "messages": [text], "model_type": "text-embedding-ada-002"}
        )
        emb = response.json()["response"]
        sleep(1)
        return emb       
    
    def reset(self):
        self.achieved_goals = [] 
        self.goal = None
        self.goals = []
    
    # Main function
    def make_decision(self, observation, observations, subgraph, main_goal, step, log):
        self.goal_setting(observation, observations, main_goal, step, subgraph, log)
        prompt = prompt_action_wGoal.format(observation = observation, observations = observations, goal = self.goal, subgraph = subgraph)
        response, cost = self.generate(prompt)
        log("Model response: " + response)
        action = response.split("Action:")[-1].strip(''' '"\n.''')
        log("Action: " + action)
        
        return action, self.goal, "go to" in action.lower()
    
    # Setting current goal
    def goal_setting(self, observation, observations, main_goal, step, subgraph, log):        
        self.check_achieved_goals(observation, observations, log)
        if step % self.goal_freq == 0 or self.goal is None or len(self.goals) == 0:
            prompt = prompt_generate_goal.format(main_goal = main_goal, subgraph = subgraph, achieved_goals = self.achieved_goals, observation = observation, observations = observations)
            response, cost = self.generate(prompt)
            self.goals = parse_plan(response)
            if not self.goals:
                log("WARNING! Goals were generated incorrect")
                self.goals = [main_goal]
            log("Generated goals: " + str(self.goals))
        self.goal = self.goals[0]
        
    # Acceptor of action
    def check_achieved_goals(self, observation, observations, log):
        new_goals = self.goals
        for goal in self.goals:
            prompt = prompt_acceptor_goal.format(goal = goal, observation = observation, observations = observations)
            response, cost = self.generate(prompt)
            log("Checked goal: " + goal + ", result: " + response)
            if "no" in response.lower():
                break
            self.achieved_goals.append(goal)
            new_goals = new_goals[1:]
        self.goals = new_goals
        
        
            
            
        

        
