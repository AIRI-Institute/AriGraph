system_prompt = '''You play at the text game, goal and some needful information are given in Task note. 
Please, try to achieve the goal fast and effective. 
If you think you haven’t some crucial knowledges about the game, explore new areas and items. 
Otherwise, go to the goal in the Task note and pay no attention to noisy things. 
If you forget or doesn't know main goal, you can always read Task note and remember main goal.'''

exploration_system_prompt = '''You play at the text game, goal and some needful information are given in Task note. 
Your main task now is to explore as much as possible. Find new locations, interact with objects you didn't interact with,
try unusual solutions and etc. Remember: now we construct a knowledge graph which contain all known information about game environment,
you should find locations, items and states which you haven't seen before. At each step graph contain all information which you already know.
Warning! Try to not visit locations that is contained in knowlrdge graph. Your task is TO EXPLORE and TO FIND NEW things and locations.
If you forget or doesn't know main goal, you can always read Task note and remember main goal.'''

actual_system_prompt = '''Your mission is to progress through a text-based adventure game. The main objective is: {main_goal}. This game requires you to navigate different areas, interact with various items, and think carefully about the outcomes of your decisions. Here is how to play effectively:
- Direct Action: If you know what you need to do to advance, focus on those actions. Ignore distractions or "noise" that don't contribute to your goal.
- Exploration and Learning: When you're unsure of your next steps or need to acquire new knowledge (this includes discovering items, places, and creatures), shift your focus to exploring. This approach helps you uncover new options and solutions.
- Avoid Repetition: As you explore, try not to revisit the same locations or repeat actions unless necessary. Your aim should be to uncover new areas and possibilities.
- Knowledge Graph: All the details and information you gather will be added to a "knowledge graph". Think of this as your game's database which provide you with necessary information. Expanding this graph through exploration will significantly aid in making informed decisions as the game progresses.

Remember, the key is to balance between acting on your current knowledge and exploring to gather new information. This strategy will guide you towards achieving your main goal in the game.'''


prompt_extracting_items = '''Based on the information provided, your task is to filter and identify objects, locations, or elements that are relevant to your specified goal from the current situation. Be sure to include items directly connected to your goal and exclude any that are not pertinent. The items you list should be succinctly named, using no more than three words per item. Also, focus only on identifying relevant elements without suggesting any actions.

Here's how you should structure your response:

Previous observations: {observations}
Current observation: {observation}
Your goal: {goal}
Given this setup, extract and list only the items from the current situation that are relevant to achieving your goal.

Example:

If the information provided is:

Previous observations: ["You are in the kitchen with exits to west and north"]
Current observation: "You are in the hall with a chest and a table"
Your goal: "Find a path to the rabbit which lives in the cabinet"
Then your response should be:

Crucial things: ["kitchen", "hall", "rabbit", "cabinet"]

Remember, your response must adhere to this format:
Crucial things: [item1, item2, ...]

Your response: '''

# For extraction triplets from observation
prompt_extraction = '''## 1. Overview
Your task is to extract information from game observations in structured formats to build a knowledge graph.
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
- If some subject just has some state or property, object in triplet must be "itself" (for example, from text "John open the door and fry chiken" you should extract the following data: "Door, opened, itself; Chiken, fried, itself").  
## 2. Coreference Resolution
- **Maintain Entity Consistency**: When extracting entities, it is vital to ensure consistency.
If an entity, such as "John Doe", is mentioned multiple times in the text but is referred to by different names or pronouns (e.g., "Joe", "he"),
always use the most complete identifier for that entity throughout the knowledge graph. In this example, use "John Doe" as the entity ID.
Remember, the knowledge graph should be coherent and easily understandable, so maintaining consistency in entity references is crucial.

####
Observation: {observation} 
####
Previous observations and actions: {observations}
####

Please, extract information from this data following instructions from begin of this prompt.

Extracted data: '''


# For setting intermediate goal at several steps
prompt_goal = '''#### Graph: {graph}
####
Previous goal: {goal}
####
Current plan: {plan}
####
Observation: {observation}
####
Previous observations and actions: {observations}
####

Based on the information provided above, your task is to set a clear and actionable goal for the next few steps in the game. This goal should be beneficial, directly contribute to winning the game, and be achievable given the current game context. Examples of appropriate goals include "Explore the east exit from the Kitchen", "Open the golden chest", "Find a path to the library", "Descend to the cellar", and "Deliver the red book to the home". Each of these goals could be relevant in different scenarios.

Please define a goal considering the current situation in the game.
Goal: '''


# For graph updating
prompt_refining = """The triplets denote facts about the environment where the player moves. The player takes actions and the environment changes, so some triplets from the list of existing triplets should be replaced with one of the new triplets. For example, the door was previously opened and now it is closed, so the triplet "Door, state, opened" should be replaced with the triplet "Door, state, closed". Another example, the player took the item from the locker and the triplet "Item, is in, Locker" should be replaced with the triplet "Player, has, Item".
First example of existing triplets: "Golden locker, state, open"; "Room K, is west of, Room I".
First example of new triplets: "Golden locker, state, closed"; "Room K, is west of, Room I".
First example of replacing: [["Golden locker, state, open" -> "Golden locker, state, closed"],].
In some cases there are no triplets to replace.
Second example of existing triplets: Golden locker, state, open; "Room K, is west of, Room I".
Second example of new triplets: "Room T, is north of, Room N".
Second example of replacing: [].
Generate replacing from existing triplets and new_triplets by analogy with first and second examples.
Existing triplets: {ex_triplets}.
New triplets: {new_triplets}.
Replacing: """


# For planning expermental
prompt_planning_new = '''I will provide you with graph of the environment. It consists of connected rooms with different items. 
####
Graph: {graph}
####

I will also provide you with current plan.
####
Current plan: {plan}
####


I will also provide you with current game state. It consist of current observation and previous observations.
####
Observation: {observation}
Previous observations: {observations}
####

Your task is to achieve the goal. 
####
Goal: {goal}
####

Write me a plan on how you will solve this task. 
Plan must consist of actions in environment. Examples of action: "take *something*", "open *something*", "go to *some location*".
Avoid to use actions like "north", "west", "south" and "east" to go to known location, use "go to" action instead.
Feel free to use actions like "north", "west", "south" and "east" for explore new locations.
When you use "go to" action you should not visiting intermediate locations, you should go directly to target (for example, if you are at kitchen and want to bedroom, you path would be "kitchen", "living room", "bedroom", and so you should just do "go to bedroom" without "go to living room" before).
Example of correct plan for making sandwich and give it to son: ["go to kitchen", "take bread", "take butter", "make sandwich", "go to living room", "give sandwich to son"]
If your previous actions didn't led to expected results (for example, game can't uderstand your action), try to rebuild or reformulate plan.
Aviod to use action "examine *something*", but if you want to "examine Task note", feel free to do it. 
####
Warning! Plan must be generated in format of list of actions (like in example above). Correct format of answer: [action_1, action_2, ...]
Generated plan: '''

# For planning
prompt_planning = '''I will provide you with graph of the environment. It consists of connected rooms with different items. 
####
Graph: {graph}
####

I will also provide you with current plan.
####
Current plan: {plan}
####


I will also provide you with current game state. It consist of current observation and previous observations.
####
Observation: {observation}
Previous observations: {observations}
####

Your task is to achieve the goal. 
####
Goal: {goal}
####

Write me a plan on how you will solve this task. 
Plan must consist of actions in environment. Examples of action: "take *something*", "examine *something*", "open *something*", "go to *some location*".
Avoid to use actions like "north", "west", "south" and "east" to go to known location, use "go to" action instead.
When you use "go to" action you should not visiting intermediate locations, you should go directly to target (for example, if you are at kitchen and want to bedroom, you path would be "kitchen", "living room", "bedroom", and so you should just do "go to bedroom" without "go to living room" before).
Example of correct plan for making sandwich and give it to son: ["go to kitchen", "take bread", "take butter", "make sandwich", "go to living room", "give sandwich to son"]
####
Warning! Plan must be generated in format of list of actions (like in example above). Correct format of answer: [action_1, action_2, ...]
Plan: '''


prompt_planning_without_obs = '''I will provide you with graph of the environment. It consists of connected rooms with different items. 
####
Graph: {graph}

I will also provide you with current plan.
####
Current plan: {plan}
####

Your task is to achieve the goal. 
####
Goal: {goal}
####

Write me new plan on how you will solve this task. 
Plan must consist of actions in environment. Examples of action: "take *something*", "examine *something*", "open *something*", "go to *some location*".
Avoid to use actions like "north", "west", "south" and "east" to go to known location, use "go to" action instead.
When you use "go to" action you should not visiting intermediate locations, you should go directly to target (for example, if you are at kitchen and want to bedroom, you path would be "kitchen", "living room", "bedroom", and so you should just do "go to bedroom" without "go to living room" before).
Example of correct plan for making sandwich and give it to son: ["go to kitchen", "take bread", "take butter", "make sandwich", "go to living room", "give sandwich to son"]
####
Warning! Plan must be generated in format of list of actions (like in example above). Correct format of answer: [action_1, action_2, ...]
Plan: '''

prompt_action = '''I will provide you with graph of the environment. It consists of connected rooms with different items. 
####
Graph: {graph}
####

I will also provide you with current game state. It consist of current observation and previous observations.
####
Observation: {observation}
Previous observations: {observations}
####

Please, according to information above give some reasoning in format of Chain of Thought and choose next action in game. Examples of action: "take *something*", "examine *something*", "open *something*", "go to *some location*".
Avoid to use actions like "north", "west", "south" and "east" to go to known location, use "go to" action instead.
When you use "go to" action you should not visiting intermediate locations, you should go directly to target (for example, if you are at kitchen and want to bedroom, you path would be "kitchen", "living room", "bedroom", and so you should just do "go to bedroom" without "go to living room" before).
####
Warning! Correct format of answer: 
Reasoning: your reasoning
Action: your action
'''

prompt_action_wGoal = '''Imagine you're playing a game set in an environment visualized through a graph. This graph outlines various rooms connected to each other, each containing different items.
I'll provide you with the layout of this environment, represented as a graph. Here's how it's structured:

Graph: {subgraph}

Additionally, you'll be given a snapshot of the current game state, which includes what you're observing right now and what you've observed in the past. Here's the information on that:

Current Observation: {observation}
Previous Observations: {observations}
Your mission, should you choose to accept it, is as follows:

Your Goal: {goal}

To accomplish your mission, you'll need to think carefully about the information provided and plan your next step in the game. This could involve picking up an item, examining something more closely, opening an object, or moving directly to a specific room without passing through intermediate locations. Remember, use direct actions like "go to a specific room" instead of compass directions. Your path should leap over intermediate locations directly to your target.
When formulating your response, please start by outlining your thought process that leads to your decision. This should be a logical explanation of how you arrived at your next action based on the available information. Conclude with the specific action you decide to take to advance towards your goal.

Here's how to structure your answer correctly:

Reasoning: Explain your thought process here.
Action: Specify your next step in the game here.
Keep in mind, this format helps keep the advice clear and actionable. Happy gaming!
'''

prompt_acceptor_goal = """You are playing a game.
Your current goal is: {goal}.
You get an observation: {observation}
Define, if you achieved the goal in the current observation. Generate a short answer: "yes" or "no".
Answer: """

prompt_generate_goal = """You are playing the game.
### Your main goal: {main_goal}
### Facts about the environment
{subgraph}
### Already achieved goals
{achieved_goals}
### Current observation
{observation}
### Previous observations
{observations}
### Instruction
Using facts about the environment, generate the chain of intermediate goals, the achievement of which will lead to the main goal. Adoid including already achieved goals into the chain. 
Use the following format for intermediate goals: [goal1, goal2, ...]

If the facts are not enough to understand how to achieve the goal, generate the intermediate goal: "explore".
Warning! Carefully follow the format of answer: [goal1, goal2, ...]
### Intermediate goals 
# """