import ast
import requests
from time import sleep
from openai import OpenAI

VPS_IP = "146.0.73.157"
port = 8000
API_KEY = "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" 


class GPTagent:
    def __init__(self, model, system_prompt, api_key):
        self.system_prompt = system_prompt
        self.model = model
        self.total_amount = 0
        self.client = OpenAI(
            api_key=api_key,
        )

    # def generate(self, prompt, jsn = False, t = 0.7):
    #     if jsn:   
    #         chat_completion = self.client.chat.completions.create(
    #             messages=[
    #                 {
    #                     "role": "system",
    #                     "content": self.system_prompt,
    #                 },
    #                 {
    #                     "role": "user",
    #                     "content": prompt,
    #                 }
    #             ],
    #             model=self.model,
    #             response_format={"type": "json_object"},
    #             temperature=t
    #         )
    #     else:
    #         chat_completion = self.client.chat.completions.create(
    #             messages=[
    #                 {
    #                     "role": "system",
    #                     "content": self.system_prompt,
    #                 },
    #                 {
    #                     "role": "user",
    #                     "content": prompt,
    #                 }
    #             ],
    #             model=self.model,
    #             temperature=t
    #         )
    #     response = chat_completion.choices[0].message.content
    #     prompt_tokens = chat_completion.usage.prompt_tokens
    #     completion_tokens = chat_completion.usage.completion_tokens

    #     cost = completion_tokens * 3 / 100000 + prompt_tokens * 1 / 100000
    #     self.total_amount += cost
    #     return response, cost
           
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
    
    def item_processing_scores(self, observation, plan):
        prompt = "####\n" + \
             "You are a retriever part of the agent system that navigates the environment in a text-based game.\n" + \
             "You will be provided with agents' observation, what it carries and a plan that it follows.\n" + \
             "Your task is to extract entities from this data that can later be used to queue the agent's memory module to find relevant information that can help to solve the task. Assign a relevance score from 1 to 2 to every entity, that will reflect the importance of this entity and potential memories connected to this entity for the current plan and goals of the agent. Do not extract items like 'west', 'east', 'east exit', 'south exit'. Pay attention to the main goal of the plan. \n\n" + \
             "Current observation: {}\n".format(observation) + \
             "Current plan: {}\n\n".format(plan) + \
             "Answer in the following format:\n" + \
             '{"entity_1": score1, "entity_2": score2, ...}\n' + \
             "Do not write anything else\n"
        response, cost = self.generate(prompt)
        entities_dict = ast.literal_eval(response)
        return entities_dict, cost
        
        
            
            
        

        
