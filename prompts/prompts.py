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

Extracted triplets: '''



prompt_extraction_thesises = '''Objective: The main goal is to meticulously gather information from input text and organize this data into a clear, structured knowledge graph.

Guidelines for Building the Knowledge Graph:

Creating Nodes and Thesises: Nodes should depict entities or concepts, similar to Wikipedia nodes. Use a structured thesises format to capture data. For example, from "Albert Einstein, born in Germany, is known for developing the theory of relativity," extract 
"Albert Einstein was born in Germany; ['Albert Einstein', 'Germany', 'birth']. Albert Einstein developed Theory of Relativity; ['Albert Einstein', 'developing', 'Theory of Relativity']." 
You should extract only concrete knowledges, any assumptions must be described as hypothesis.
For example, from phrase "John have scored many points and potentially will be winner" you should extract "John scored many points; ['John', 'scoring', 'point']. John could be winner; ['John', 'winner']." and should not extract "John will be winner".
Remember that nodes must be an atomary units while thesis can be more complex and long.
If observation states that you take item, the triplet shoud be: 'item is in inventory' and nothing else. 

Do not miss important information. If observation is 'book involves story about knight, who needs to kill a dragon', thesises should be 'book involves knight', 'knight needs to kill dragon'. If observation involves some type of notes, do not forget to include thesises about entities this note includes.
There could be connections between distinct parts of observations. For example if there is information in the beginning of the observation that you are in location, and in the end it states that there is an exit to the east, you should extract thesis: 'location has exit east'. 
Several thesises can be extracted, that contain information about the same node. For example 'kitchen contains apple', 'kitchen contains table', 'apple is on table'. Do not miss this type of connections.
Other examples of thesises: 'room z contains black locker', 'room x has exit east', 'apple is on table', 'key is in locker', 'apple need to be grilled', 'potato need to be sliced', 'stove used for frying', 'recipe requires green apple', 'recipe requires potato'.
Do not include thesises that state the current state of an agent like 'you are in location'.
Do not use 'none' as one of the nodes.
If there is information that you read something, do not forget to incluse thesises that state that entitie that you read contains information that you extract.
Thesises MUST BE comprehension and consistent, so you can make them in form of sentense. You better make a much longer thesis than split it into two which inconsistent separately.
For example, you better extract thesis "North exit from kitchen is blocked by door" than " kitchen has door" and "north exit is blocked by door"
because without context of kitchen "north exit is blocked by door" can be related to every room at home.

Text: {observation}
Remember that thesises must be extracted in format: "thesis_1; [list of entites for thesis_1]. thesis2; [list of entites for thesis_2]. etc.'''

prompt_refining_thesises = '''You will be provided with list of existing thesises and list of new thesises. 
The thesises denote facts about the environment where the player moves. The player takes actions and the environment changes, so some thesises from the list of existing thesises can be replaced with one of the new thesises. For example, the player took the item from the locker and the existing thesis "item is in locker" should be replaced with the new thesis "item is in inventory".

Sometimes there are no thesises to replace:
Example of existing thesises: ["Golden locker is open", "Room K is west of Room I", "Room K has exit to east"]
Example of new thesises: ["Room T is north of Room N", "Room T has exit to south"]
Example of replacing: []. Nothisg to replace here

Sometimes several thesises can be replaced with one:
Example of existing thesises: ["kitchen contains broom", "broom is on floor"]
Example of new thesises: ["broom is in inventory"]
Example of replacing: ["broom is in inventory; kitchen contains broom", "broom is in inventory; broom is on floor"]. Because broom changed location from the floor in the kitchen to players inventory.

Ensure that thesises are only replaced if they contain redundant or conflicting information about the same aspect of an entity. Thesises should not be replaced if they provide distinct or complementary information about entities compared to the new thesises. Specifically, consider the relationships, properties, or contexts described by each thesis and verify that they align before replacement. If there is uncertainty about whether a thesis should be replaced, prioritize retaining the existing thesis over replacing it. When comparing existing and new thesises, if they refer to different aspects or attributes of entities, do not replace them. Replacements should only occur when there is semantic duplication between an existing thesis and a new thesis.
Example of existing thesises: ["apple need to be cooked", 'knife used for cutting', 'apple has been sliced']
Example of new thesises: ["apple is on table", 'kitchen contsins knife', 'apple has beed grilled']
Example of replacing: []. Nothing to replace here. These thesises describe different properties of items, so they should not be replaced. 

Another example of when not to replase existung thesises:
Example of existing thesises: ["brush is used for painting"]
Example of new thesises: ["brush is in art class"]
Example of replacing: []. Nothing to replace here. These thesises describe different properties of brush, so they should not be replaced. 

I repeat, do not replace thesises if they carry differend type of information about entities!!! It is better to leave a thesis, than to replace the one that has important information. Do not state that thesis needs to be replaced if you are not sure!!!
If you find thesis in Existing thesises which semantically duplicate some thesis in New thesises, replace such thesis from Existing thesises. However do not replace thesis if they refer to different things. 
For every thesis you want to replace you must find replacement from new thesises. If there is no clear replacement, you must not replace existing thesis.
The replacements should contain information about the same properties as the statements being replaced, but must include more recent information.
You MUST save existing thesis if it contains unique or actual information about entities. 
For example, you MUST NOT replace thesis "running is done with sneakers" with "sneakers located at store".
####

Generate only list of replacing, no descriptions are needed.
Existing thesises: {ex_thesises}.
New thesises: {new_thesises}.
####
Warning! Replacing must be generated strictly in following format: ["new_thesis_1 <- outdated_thesis_1"; "new_thesis_2 <- outdated_thesis_2"; ...], you MUST NOT include any descriptions in answer.
Replacing: '''

reflex_prompt = '''You are a learner in system of AI agents which play in text games. Your task is to find useful patterns in observations and explain it for future usage. Namely, you should find the unefficiency in previous behaviour and the patterns that can help to avoid this unefficiency.
Your answer must be brief and accurate and contain only three sentences. 
####
{for_reflex}
####
Your answer: '''
