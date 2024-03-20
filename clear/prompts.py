system_prompt = '''You play at the text game, goal and some needful information are given in Task note. Please, try to achieve the goal fast and effective. If you think you haven’t some crucial knowledges about the game, explore new areas and items. Otherwise, go to the goal and pay no attention to noisy things.'''

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


# For planning
prompt_planning = '''I will provide you with graph of the environment. It consists of connected rooms with different items. 
####
Graph: {graph}
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
Example of correct plan for making sandwich and give it to son: ["go to kitchen", "take bread", "take butter", "make sandwich", "go to living room", "give sandwich to son"]
####
Generated plan: '''


prompt_planning_without_obs = '''I will provide you with graph of the environment. It consists of connected rooms with different items. 
####
Graph: {graph}

I will also provide you curent plan.
####
Current plan: {plan}
####

Your task is to achieve the goal. 
####
Goal: {goal}
####

Write me new plan on how you will solve this task. 
Plan must consist of actions in environment. Examples of action: "take *something*", "examine *something*", "open *something*", "go to *some location*".
Avoid to use actions like "north", "west", "south" and "east", use "go to" action instead to move at chosen location.
Example of correct plan for making sandwich and give it to son: ["go to kitchen", "take bread", "take butter", "make sandwich", "go to living room", "give sandwich to son"]
####
Generated plan: '''