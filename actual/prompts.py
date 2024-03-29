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
- Knowledge Graph: All the details and information you gather will be added to a "knowledge graph". Think of this as your game's database which provide you with necessary information. Expanding this graph through exploration will significantly aid in making informed decisions as the game progresses.'''


prompt_extracting_items = '''Based on the information provided, your task is to filter and identify objects, locations, or elements that are relevant to your specified goal from the current situation. Be sure to include objects directly connected to your goal and exclude any that are not pertinent. The objects you list should be succinctly named, using no more than three words per item. Feel free to add objects that relative to game rules (for example: "search", "new data", "environment", "game", "action")

Here's how you should structure your response:

Previous observations: {observations}
Current observation: {observation}
Your goal: {goal}
Given this setup, extract and list only the objects from the current situation that are relevant to achieving your goal.

Example:

If the information provided is:

Previous observations: ["You are in the kitchen with exits to west and north"]
Current observation: "You are in the hall with a chest and a table"
Your goal: "Find a path to the rabbit which lives in the cabinet"
Then your response should be:

Crucial things: ["kitchen", "hall", "rabbit", "cabinet", "search", "moving"]

Remember, your response must adhere to this format:
Crucial things: [item1, item2, ...]

Your response: '''

# For extraction triplets from observation
prompt_extraction = '''Extracting Information:

- Your main job is to process game observations and extract meaningful data from them.
- This data should be formatted as triplets: "subject, relation, object".
- A subject is the main entity (e.g., "Albert Einstein").
- A relation describes the connection between the subject and the object (e.g., "born in").
- An object is what the subject is related to (e.g., "Germany").

## Formatting Triplets:

- Triplets must be simple and to the point.
- If any information is complex, break it down into simpler, separate triplets.
- Avoid including collective entities or long phrases as objects.
- Standardize similar terms to maintain uniformity.

## Handling States and Properties:

- If an entity simply possesses a state or feature, use "itself" as the object in your triplet (e.g., "Door, opened, itself").

## Maintaining Entity Consistency:

- Ensure that you consistently reference entities using the most complete and clear identifier, even if they are mentioned in different ways throughout the text.

## Extracting Meta Information and Insights:

- Besides observations, extract information about game rules and unique qualities of the game environment that might affect gameplay.
- Concentrate on game properties that are unexpected for you.
- You can also extract your insights which are based on game observation.
- You shouldn't extract all valid actions, extract only needful from its.

A practical example from the text "Albert Einstein, born in Germany, is known for developing the theory of relativity" becomes:
"Albert Einstein, country, Germany; Albert Einstein, developed, Theory of relativity".
A practical example from the text "There is a small room. Action that led to this: turn on flashlight. \n Previous observation: You are at dark." becomes:
"light, can provide, new data".
A practical example from the text "I can't understand yout command. Action that lead to this: use key and explore chest" becomes:
"use, incorrect, action; explore, incorrect, action; game, can't perform, several actions".

This approach aims to make complex text data easily understandable and useful, particularly for creating knowledge graphs that enhance comprehension and future use.
Please, extract triplets from this game state following the instructions above:
####
Observation: {observation}
Previous observations: {observations}
####
Triplets must be extracted in format: subject_1, relation_1, object_1; subject_2, relation_2, object_2; ...
Extracted triplets: '''


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
####
Generate replacing from existing triplets and new_triplets by analogy with first and second examples.
Existing triplets: {ex_triplets}.
New triplets: {new_triplets}.
####
Warning! Replacing must be generated strictly in following format: [[outdated_triplet_1 -> actual_triplet_1], [outdated_triplet_2 -> actual_triplet_2], ...]
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

prompt_action = '''Imagine you're playing a game set in an environment visualized through a graph. This graph outlines various rooms connected to each other, each containing different items.
I'll provide you with the layout of this environment, represented as a graph. Here's how it's structured:

Graph: {subgraph}

Additionally, you'll be given a snapshot of the current game state, which includes what you're observing right now and what you've observed in the past and also actions you did before. Pay attention on previous actions and try to find meaningful clues for now. You shouldn't repeat actions that you have already tried at current location without necessity. Here's the information on that:

Current Observation: {observation}
Previous Observations: {observations}

To accomplish your mission, you'll need to think carefully about the information provided and plan your next step in the game. This could involve picking up an item, examining something more closely, opening an object, or moving directly to a specific room without passing through intermediate locations. Remember, use direct actions like "go to a specific room" instead of compass directions. Your path should leap over intermediate locations directly to your target.
When formulating your response, provide the specific action you decide to take to advance towards your goal. Action must be clear and brief, example of correct actions contains in observations. Any descriptions of chosen action are redundant.
Remember that you shouldn't repeat actions that you have already tried at current location (list of them is provided in Current observation) without necessity.

Here's how to structure your answer correctly:
Action: chosen action.

Keep in mind, this format helps keep the advice clear and actionable. Happy gaming and remember that you shouldn't repeat actions that you have already tried at current location (list of them is provided in Current observation) without necessity!
####
Action: '''

prompt_action_wGoal = '''Imagine you're playing a game set in an environment visualized through a graph. This graph outlines various rooms connected to each other, each containing different items.
I'll provide you with the layout of this environment, represented as a graph. Here's how it's structured:

Graph: {subgraph}

Additionally, you'll be given a snapshot of the current game state, which includes what you're observing right now and what you've observed in the past and also actions you did before. Pay attention on previous actions and try to find meaningful clues for now. You shouldn't repeat actions that you have already tried at current location without necessity. Here's the information on that:

Current Observation: {observation}
Previous Observations: {observations}
Your mission, should you choose to accept it, is as follows:

Your Goal: {goal}

To accomplish your mission, you'll need to think carefully about the information provided and plan your next step in the game. This could involve picking up an item, examining something more closely, opening an object, or moving directly to a specific room without passing through intermediate locations. Remember, use direct actions like "go to a specific room" instead of compass directions. Your path should leap over intermediate locations directly to your target.
When formulating your response, provide the specific action you decide to take to advance towards your goal. Action must be clear and brief, example of correct actions contains in observations. Any descriptions of chosen action are redundant.
Remember that you shouldn't repeat actions that you have already tried at current location (list of them is provided in Current observation) without necessity.

Here's how to structure your answer correctly:
Action: chosen action.

Keep in mind, this format helps keep the advice clear and actionable. Happy gaming and remember that you shouldn't repeat actions that you have already tried at current location (list of them is provided in Current observation) without necessity!
####
Action: '''

prompt_acceptor_goal = """You are playing a game.
Your current goal is: {goal}.
You get an observation: {observation}.
Previous observations: {observations}
Define, if you achieved the goal in the current observation. Generate a short answer: "yes" or "no".
Pay attention to the action that lead to this observation. Many information about current state contains in action that lead to it.
If goal is smooth (like "examine"), be more loyal in your assessment.
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