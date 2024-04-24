# from prompts import *
# from prompts_v2 import *
# from graphs.extended_graphs import ExtendedGraphPagerankStrategy

# main_goal = "Find the treasure"
# model, system_prompt = "gpt-4-0125-preview", actual_system_prompt.format(main_goal = main_goal)
# graph = ExtendedGraphPagerankStrategy(model, system_prompt)
# graph.load("exp_detective_extended_graph_with_walkthrough")
# breakpoint()

# from transformers import AutoModelForCausalLM
# import torch
# from llama_cpp import Llama

# llm = Llama(
#     model_path="/trinity/home/n.semenov/.cache/huggingface/hub/models--LLaMA3-70B-Instruct/Meta-Llama-3-70B-Instruct.fp16-00001-of-00004.gguf",
#     n_ctx=4000,  # Context length to use
#     n_threads=32,            # Number of CPU threads to use
#     n_gpu_layers=-1        # Number of model layers to offload to GPU
# )
# model = AutoModelForCausalLM.from_pretrained("/trinity/home/n.semenov/.cache/huggingface/hub/models--LLaMA3-70B-Instruct", torch_dtype = torch.bfloat16, device_map = "auto")

# from transformers import AutoTokenizer, AutoModelForCausalLM
# import torch

# tokenizer = AutoTokenizer.from_pretrained("Undi95/Meta-Llama-3-70B-Instruct-hf")
# model = AutoModelForCausalLM.from_pretrained("Undi95/Meta-Llama-3-70B-Instruct-hf", device_map = "auto", torch_dtype = torch.bfloat16)

import transformers
import torch

model_id = "Undi95/Meta-Llama-3-70B-Instruct-hf"

pipeline = transformers.pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
)

messages = [
    {"role": "system", "content": "You are a pirate chatbot who always responds in pirate speak!"},
    {"role": "user", "content": "Who are you?"},
]

prompt = pipeline.tokenizer.apply_chat_template(
        messages, 
        tokenize=False, 
        add_generation_prompt=True
)

terminators = [
    pipeline.tokenizer.eos_token_id,
    pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
]

outputs = pipeline(
    prompt,
    max_new_tokens=2048,
    eos_token_id=terminators,
    do_sample=True,
    temperature=0.6,
    top_p=0.9,
)
print(outputs[0]["generated_text"][len(prompt):])