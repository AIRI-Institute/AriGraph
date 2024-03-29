prompt_summary = '''Your task is to summarize game states which given below. 
This summary must be brief and must contain your insights about game environment and player actions. 
You should include only insights with concrete information (For example: "rooms usually locked", 
"clues usually can be found by moving", "examine action usually not provide additional information", 
"environment contains creatures except player" and etc.).
Be brief and extract only insights that you can't predict without STATES.'''

prompt_summary_obs = '''STATES: {observations}
Remember that you should be brief and include only insights that can be useful in the future. Your summary:'''

prompt_refining_meta = """The triplets denote facts about the environment where the player moves. The player takes actions and the environment changes, so some triplets from the list of existing triplets should be replaced with one of the new triplets. For example, the door was previously opened and now it is closed, so the triplet "Door, opened, itself" should be replaced with the triplet "Door, closed, itself". Another example, the player took the item from the locker and the triplet "Item, is in, Locker" should be replaced with the triplet "Player, has, Item".
In some cases there are no triplets to replace.
Example of existing triplets: Golden locker, state, open; "Room K, is west of, Room I".
Example of new triplets: "Room T, is north of, Room N".
Example of replacing: [].
####
Generate replacing from existing triplets and new_triplets by analogy with first and second examples.
Existing triplets: {ex_triplets}.
New triplets: {new_triplets}.
####
Warning! Replacing must be generated strictly in following format: [[outdated_triplet_1 -> actual_triplet_1], [outdated_triplet_2 -> actual_triplet_2], ...]
Replacing: """

prompt_refining_items = """The triplets denote facts about the environment where the player moves. The player takes actions and the environment changes, so some triplets from the list of existing triplets should be replaced with one of the new triplets. For example, the door was previously opened and now it is closed, so the triplet "Door, opened, itself" should be replaced with the triplet "Door, closed, itself". Another example, the player took the item from the locker and the triplet "Item, is in, Locker" should be replaced with the triplet "Player, has, Item".
In some cases there are no triplets to replace.
Example of existing triplets: Golden locker, state, open; "Room K, is west of, Room I".
Example of new triplets: "Room T, is north of, Room N".
Example of replacing: [].
####
Generate replacing from existing triplets and new_triplets by analogy with first and second examples.
Existing triplets: {ex_triplets}.
New triplets: {new_triplets}.
####
Warning! Replacing must be generated strictly in following format: [[outdated_triplet_1 -> actual_triplet_1], [outdated_triplet_2 -> actual_triplet_2], ...]
Replacing: """

prompt_extraction_current = '''Objective: The main goal is to meticulously gather information from game observations and organize this data into a clear, structured knowledge graph.

Guidelines for Building the Knowledge Graph:

Creating Nodes and Triplets: Nodes should depict entities or concepts, similar to Wikipedia nodes. Use a structured triplet format to capture data, as follows: "subject, relation, object." For example, from "Albert Einstein, born in Germany, is known for developing the theory of relativity," extract "Albert Einstein, country of birth, Germany; Albert Einstein, developed, Theory of Relativity." Simplification and Clarity: Aim for simplicity and readability in your knowledge graph to facilitate future use. If encountering complex objects within triplets, break them down into simpler, distinct triplets for clarity. Uniformity: Ensure uniformity in entities and relations. For example, similar entities like "House" and "house" should be standardized to a single form, e.g., "house." Use consistent relations for similar actions or states, like replacing "has friend" and "friend of" with a uniform relation. Special Cases in Triplets: Exclude triplets where the subject or object are collective entities or the object is a long phrase exceeding 5 words. When a subject possesses a state or property, the object should be marked as "itself." For instance, "Door, opened, itself." Coreference Resolution: Maintain entity consistency throughout the knowledge graph to ensure clarity and coherence. Use the most complete and accurate identifier for entities appearing multiple times under different names or pronouns. Application to the Text-based Adventure Game: Leverage these guidelines while navigating through the game. Pay attention to: Direct actions necessary for game progression. Exploration opportunities for discovering new items, locations, and information. Avoiding repetitive actions unless they contribute to new outcomes. Learning game mechanics through gameplay and incorporating meta-information about game rules into the knowledge graph. The essence of these instructions is to help you methodically record and organize knowledge as you progress through the game, enhancing your decision-making and strategic planning capabilities.

Observation: {observation}

Remember that triplets must be extracted in format: "subject_1, relation_1, object_1; subject_2, relation_2, object_2; ..."

Extracted triplets:'''

prompt_extraction_summary = '''Your task is to extract information from insight in structured formats to build a knowledge graph.
- **Nodes** represent entities and concepts. They are akin to Wikipedia nodes.
- The aim is to achieve simplicity and clarity in the knowledge graph, making it useful for you in the future.
- Triplets must save semantic structure of original text.
- Triplets must contain general knowledges about the game and must not contain particaular knowledges.
- Use the following triplet format for extracted data: "triplet1; triplet2; ...", more detailed - "subject1, relation1, object1; subject2, relation2, object2; ...", where a triplet is "subject1, relation1, object1" or "subject2, relation2, object2".
- Both subject and object in triplets should be akin to Wikipedia nodes. Object can be a date or number, objects should not contain citations or sentences.
- Instead of generating complex objects, divide triplet with complex object into two triplets with more precise objects. For example, the text "John Doe is a developer at Google" corresponds to two triplets: "John Doe, position, developer; John Doe, employed by, Google".
- Exclude from the extracted data triplets where object is a long phrase with more than 5 words.
- Similar relations, such as "has friend" and "friend of", replace with uniform relation, for example, "has friend"
- Similar entities, such as "House" and "house" or "small river" and "little river", replace with uniform relation, for example, "house" or "small river" 
- When extracting entities, it is vital to ensure consistency. If an entity, such as "John Doe", is mentioned multiple times in the text but is referred to by different names or pronouns (e.g., "Joe", "he"),
always use the most complete identifier for that entity throughout the knowledge graph. In this example, use "John Doe" as the entity ID.
Remember, the knowledge graph should be coherent and easily understandable, so maintaining consistency in entity references is crucial.
- Triplets must not include particular information, use generalizations instead (for example, from text "John see a rabbit, a horse and a dog" you should extract following data: "John, see, animals" and you should not include particular triplets like "John, see, rabbit", "John see, horse", "John, see, dog").
- Triplets that you are extracting must describe game rules, player's insights and generalization over past experience. You should not include triplets with current items unless this item isn't really crucial for game understanding. 

Observation: {observation}

Remember that triplets must be extracted in format: "subject_1, relation_1, object_1; subject_2, relation_2, object_2; ..."

Extracted triplets:'''