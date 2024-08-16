import transformers
import torch
import requests
from time import sleep

from agents.parent_agent import GPTagent


class LLaMAagent(GPTagent):
    def __init__(self, system_prompt, pipeline = None):
        super().__init__("", "", "")
        self.system_prompt = system_prompt
        self.pipeline = transformers.pipeline(
            "text-generation",
            model="Undi95/Meta-Llama-3-70B-Instruct-hf",
            model_kwargs={"torch_dtype": torch.bfloat16},
            device_map="auto"
        ) if pipeline is None else pipeline
        
    def generate(self, prompt, jsn = False, t = 0.2):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt},
        ]

        prompt = self.pipeline.tokenizer.apply_chat_template(
                messages, 
                tokenize=False, 
                add_generation_prompt=True
        )

        terminators = [
            self.pipeline.tokenizer.eos_token_id,
            self.pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]
        
        outputs = self.pipeline(
            prompt,
            max_new_tokens=2048,
            eos_token_id=terminators,
            do_sample=True,
            temperature=t,
            top_p=0.9,
        )
        
        return outputs[0]["generated_text"][len(prompt):], 0