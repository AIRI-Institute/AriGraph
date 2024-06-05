prompt_refining_items = """You will be provided with list of existing triplets and list of new triplets. Triplets are in the following format: "subject, relation, object".
The triplets denote facts about the environment where the player moves. The player takes actions and the environment changes, so some triplets from the list of existing triplets can be replaced with one of the new triplets. For example, the player took the item from the locker and the existing triplet "item, is in, locker" should be replaced with the new triplet "item, is in, inventory".

Sometimes there are no triplets to replace:
Example of existing triplets: "Golden locker, state, open"; "Room K, is west of, Room I"; "Room K, has exit, east".
Example of new triplets: "Room T, is north of, Room N"; "Room T, has exit, south".
Example of replacing: []. Nothisg to replace here

Sometimes several triplets can be replaced with one:
Example of existing triplets: "kitchen, contains, broom"; "broom, is on, floor".
Example of new triplets: "broom, is in, inventory".
Example of replacing: [["kitchen, contains, broom" -> "broom, is in, inventory"], ["broom, is on, floor" -> "broom, is in, inventory"]]. Because broom changed location from the floor in the kitchen to players inventory.

Ensure that triplets are only replaced if they contain redundant or conflicting information about the same aspect of an entity. Triplets should not be replaced if they provide distinct or complementary information about entities compared to the new triplets. Specifically, consider the relationships, properties, or contexts described by each triplet and verify that they align before replacement. If there is uncertainty about whether a triplet should be replaced, prioritize retaining the existing triplet over replacing it. When comparing existing and new triplets, if they refer to different aspects or attributes of entities, do not replace them. Replacements should only occur when there is semantic duplication between an existing triplet and a new triplet.
Example of existing triplets: "apple, to be, cooked", 'knife, used for, cutting', 'apple, has been, sliced'
Example of new triplets: "apple, is on, table", 'kitchen, contsins, knife', 'apple, has beed, grilled'.
Example of replacing: []. Nothing to replace here. These triplets describe different properties of items, so they should not be replaced. 

Another example of when not to replase existung triplets:
Example of existing triplets: "brush, used for, painting".
Example of new triplets: "brush, is in, art class".
Example of replacing: []. Nothing to replace here. These triplets describe different properties of brush, so they should not be replaced. 

I repeat, do not replace triplets, if they carry differend type of information about entities!!! It is better to leave a tripplet, than to replace the one that has important information. Do not state that triplet needs to be replaced if you are not sure!!!
If you find triplet in Existing triplets which semantically duplicate some triplet in New triplets, replace such triplet from Existing triplets. However do not replace triplets if they refer to different things. 
####

Generate only replacing, no descriptions are needed.
Existing triplets: {ex_triplets}.
New triplets: {new_triplets}.
####
Warning! Replacing must be generated strictly in following format: [[outdated_triplet_1 -> actual_triplet_1], [outdated_triplet_2 -> actual_triplet_2], ...], you MUST NOT include any descriptions in answer.
Replacing: """

prompt_extraction_current = '''Objective: The main goal is to meticulously gather information from game observations and organize this data into a clear, structured knowledge graph.

Guidelines for Building the Knowledge Graph:

Creating Nodes and Triplets: Nodes should depict entities or concepts, similar to Wikipedia nodes. Use a structured triplet format to capture data, as follows: "subject, relation, object". For example, from "Albert Einstein, born in Germany, is known for developing the theory of relativity," extract "Albert Einstein, country of birth, Germany; Albert Einstein, developed, Theory of Relativity." 
Remember that you should break complex triplets like "John, position, engineer in Google" into simple triplets like "John, position, engineer", "John, work at, Google".
Length of your triplet should not be more than 7 words. You should extract only concrete knowledges, any assumptions must be described as hypothesis.
For example, from phrase "John have scored many points and potentially will be winner" you should extract "John, scored many, points; John, could be, winner" and should not extract "John, will be, winner".
Remember that object and subject must be an atomary units while relation can be more complex and long.
If observation states that you take item, the triplet shoud be: 'item, is in, inventory' and nothing else. 

Do not miss important information. If observation is 'book involves story about knight, who needs to kill a dragon', triplets should be 'book, involves, knight', 'knight, needs to kill, dragon'. If observation involves some type of notes, do not forget to include triplets about entities this note includes.
There could be connections between distinct parts of observations. For example if there is information in the beginning of the observation that you are in location, and in the end it states that there is an exit to the east, you should extract triplet: 'location, has exit, east'. 
Several triplets can be extracted, that contain information about the same node. For example 'kitchen, contains, apple', 'kitchen, contains, table', 'apple, is on, table'. Do not miss this type of connections.
Other examples of triplets: 'room z, contains, black locker'; 'room x, has exit, east', 'apple, is on, table', 'key, is in, locker', 'apple, to be, grilled', 'potato, to be, sliced', 'stove, used for, frying', 'recipe, requires, green apple', 'recipe, requires, potato'.
Do not include triplets that state the current location of an agent like 'you, are in, location'.
Do not use 'none' as one of the entities.
If there is information that you read something, do not forget to incluse triplets that state that entitie that you read contains information that you extract.

Example of triplets you have extracted before: {example}

Observation: {observation}

Remember that triplets must be extracted in format: "subject_1, relation_1, object_1; subject_2, relation_2, object_2; ..."

Extracted triplets:'''



prompt_extraction_thesises = '''Your task is to decompose input text into set of expressive, accurate and short thesises with their entities.
Every thesis must contain completed truth information which contains in the input text. Pay attention on full text and extract only contextually and factologically truth information.
For example, from text "Little boy always like sweety and that's because he is going to kitchen to pick up candies" you should extract following thesises:
{
    "thesises": [
        {
            "thesis": "Little boy always like sweety",
            "entities": ["little boy", "sweety"]
        },
        {
            "thesis": "Little boy is going to kitchen",
            "entities": ["little boy", "kitchen"]
        },
        {
            "thesis": "Little boy is going to pick up candies",
            "entities": ["little boy", "candies", "kitchen"]
        },
        {
            "thesis": "Kitchen contains candies",
            "entities": ["kitchen", "candies"]
        },
    ]
}
Remember that thesises must be absolutely truth and contain strictly information that is contained into input text. Entities must not be
a verb and must explicitly or implicitly appear in the thesis. Don't forget to include entities which aren't explicitly appeared
in the text but crucial for current thesis (like entity "kitchen" for thesis "Little boy is going to pick up candies" from example).
Thesises must be consistency without context, so, you should not to use phrases like "there is",
"that", "now" and etc. For example, from text "Step 1. Now you are at the kitchen. There is a table and fridge" you should not extract thesises 
"There is a table", "There is a fridge", "Now you are at kitchen", better extract "table located at the kitchen", "fridge located at the kitchen", 
"At step 1 you are at the kitchen".
You should add the context into thesises for better understanding in the future. Thesises must be complete and useful
without source text. For example, thesis "north window is open" is not clear since "north window" can appears at many different locations.
You should extract "north window at kitchen is open" (if you are at the kitchen) instead.
Pay attention on full text and extract only contextually and factologically truth information.

Write your answer strictly in following json format:
{
    "thesises": [
        {
            "thesis": your first thesis,
            "entities": list of entities in the first thesis
        },
        ...
    ]
}'''

prompt_refining_thesises = '''Your task is to remove inaccurate knowledges from database.
You provide with new truth thesises and old thesises. You should list old thesises which are inaccurate with respect to new thesises.
Example:
Old thesises: ["fridge is open", "fridge located at kitchen", "fridge contain apple", "inventory contain meat", "table located at kitchen"]
New thesises: ["player closed fridge", "inventory contain apple", "meat located at table"]
Inaccurate thesises: ["fridge is open", "fridge contain apple", "inventory contain meat"]
Be accurate and list ONLY old thesises which explicitly contradict with new thesises. If some old thesis contain information
which has no interaction with new thesises, you MUST NOT include it into inaccurate thesises.
For example, if new thesises are ["table at the kitchen", "fridge in the kithcen"] and old thesises are ["you are at living room", "sofa located at living room"],
you must include nothing into inaccurate thesises because new information isn't contradict with old thesises.
Your answer must contain exactly list of inaccurate old thesises and nothing else.
####
Old thesises: {ex_thesises}
New thesises: {new_thesises}
Inaccurate thesises: '''

reflex_prompt = '''You are a learner in system of AI agents which play in text games. Your task is to find useful patterns in observations and explain it for future usage. Namely, you should find the unefficiency in previous behaviour and the patterns that can help to avoid this unefficiency.
Your answer must be brief and accurate and contain only three sentences. 
####
{for_reflex}
####
Your answer: '''
