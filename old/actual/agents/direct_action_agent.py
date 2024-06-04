from prompts import *
from parent_agent import GPTagent

class DirectActionAgent(GPTagent):
    def __init__(self, model = "gpt-4-1106-preview", system_prompt = None):
        super().__init__(model, system_prompt)
        
    def make_decision(self, observation, observations, subgraph, main_goal, step, log):
        prompt = prompt_action.format(observation = observation, observations = observations, subgraph = subgraph)
        response, cost = self.generate(prompt)
        log("Model response: " + response)
        action = response.split("Action:")[-1].strip(''' '"\n.''')
        log("Action: " + action)
        
        return action, "Without goal", "go to" in action.lower()