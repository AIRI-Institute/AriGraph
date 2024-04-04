import json

from prompts import *
from prompts_v2 import *
from parent_agent import GPTagent

class PlanInJsonAgent(GPTagent):
    def __init__(self, main_goal, model = "gpt-4-1106-preview", system_prompt = None):
        super().__init__(model, system_prompt)
        self.plan = f'''{{
  "main_goal": {main_goal},
  "plan_steps": [
    {{
      "sub_goal_1": "Start the game",
      "reason": "You should start the game"
    }},
  ],
}}'''
        
        
    def make_decision(self, observation, observations, subgraph, main_goal, log):
        prompt = prompt_plan_new.format(main_goal = main_goal, observations = observations, observation = observation, plan = self.plan, subgraph = subgraph)
        self.plan, cost_plan = self.generate(prompt, jsn=True)
        log("Generated plan: " + self.plan)
        plan_json = json.loads(self.plan)
       
        sub_goal_1 = plan_json["plan_steps"][0]["sub_goal_1"]
        reason1 = plan_json["plan_steps"][0]["reason"]

        #Generate action
        prompt = prompt_action_with_plan.format(main_goal = main_goal, observations = observations, observation = observation, plan = self.plan, subgraph = subgraph)
        action, cost_action = self.generate(prompt)
        log("Chosen action: " + action)
        
        return action, sub_goal_1, "go to" in action.lower()