from transformers import AutoTokenizer, AutoModelForCausalLM

from parent_agent import GPTagent

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