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