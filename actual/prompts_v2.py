prompt_summary = '''Your task is to summarize game states which given below. 
This summary must be brief and must contain your insights about game environment and player actions. 
You should include only insights with concrete information (For example: "rooms usually locked", 
"clues usually can be found by moving", "examine action usually not provide additional information", 
"environment contains creatures except player" and etc.).
Be brief and extract only insights that you can't predict without STATES. All your insights must be formulated in one paragraph of text.'''

prompt_summary_obs = '''STATES: {observations}
Remember that you should be brief and include only insights that can be useful in the future. Also remember that your summary must not be longer than one paragraph of text.
Try to formulate insights like set of thesises. Your summary:'''

prompt_summary_wplan = '''Your task is to summarize game states which given below. 
Please, include in summary only information that can be useful with respect to plan: {plan}
This summary must be brief and must contain your insights about game environment and player actions. 
This summary must include not more than 3 sentences.
You should include only insights with concrete information (For example: "rooms usually locked", 
"clues usually can be found by moving", "examine action usually not provide additional information", 
"environment contains creatures except player" and etc.).
Be brief and extract only insights that are not a common knowledge and are specific to current game (for example, "locker usually locked" is good insight, but "lockers can be unlock with key" is bad insight). '''

prompt_summary_wplan_obs = '''STATES: {observations}
Remember that you should be brief and include only insights that can be useful with respect to plan given above in json format. Also remember that your summary must include not more than 3 insights.
Try to formulate insight like current thesis. Your summary:'''

prompt_refining_meta = """The triplets denote facts about the environment where the player moves. The player takes actions and the environment changes, so some triplets from the list of existing triplets should be replaced with one of the new triplets. For example, the door was previously opened and now it is closed, so the triplet "Door, opened, itself" should be replaced with the triplet "Door, closed, itself". Another example, the player took the item from the locker and the triplet "Item, is in, Locker" should be replaced with the triplet "Player, has, Item".
In some cases there are no triplets to replace.
Example of existing triplets: Golden locker, state, open; "Room K, is west of, Room I".
Example of new triplets: "Room T, is north of, Room N".
Example of replacing: [].
If you find triplet in Existing triplets which semantically duplicate some triplet in New triplets, replace such triplet from Existing triplets.
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
If you find triplet in Existing triplets which semantically duplicate some triplet in New triplets, replace such triplet from Existing triplets.
####
Generate replacing from existing triplets and new_triplets by analogy with first and second examples.
Existing triplets: {ex_triplets}.
New triplets: {new_triplets}.
####
Warning! Replacing must be generated strictly in following format: [[outdated_triplet_1 -> actual_triplet_1], [outdated_triplet_2 -> actual_triplet_2], ...]
Replacing: """

prompt_extraction_current = '''Objective: The main goal is to meticulously gather information from game observations and organize this data into a clear, structured knowledge graph.

Guidelines for Building the Knowledge Graph:

Creating Nodes and Triplets: Nodes should depict entities or concepts, similar to Wikipedia nodes. Use a structured triplet format to capture data, as follows: "subject, relation, object." For example, from "Albert Einstein, born in Germany, is known for developing the theory of relativity," extract "Albert Einstein, country of birth, Germany; Albert Einstein, developed, Theory of Relativity." Simplification and Clarity: Aim for simplicity and readability in your knowledge graph to facilitate future use. If encountering complex objects within triplets, break them down into simpler, distinct triplets for clarity. Uniformity: Ensure uniformity in entities and relations. For example, similar entities like "House" and "house" should be standardized to a single form, e.g., "house." Use consistent relations for similar actions or states, like replacing "has friend" and "friend of" with a uniform relation. Special Cases in Triplets: Exclude triplets where the subject or object are collective entities or the object is a long phrase exceeding 5 words. Coreference Resolution: Maintain entity consistency throughout the knowledge graph to ensure clarity and coherence. Use the most complete and accurate identifier for entities appearing multiple times under different names or pronouns. Application to the Text-based Adventure Game: Leverage these guidelines while navigating through the game. Pay attention to: Direct actions necessary for game progression. Exploration opportunities for discovering new items, locations, and information. Avoiding repetitive actions unless they contribute to new outcomes. Learning game mechanics through gameplay and incorporating meta-information about game rules into the knowledge graph. The essence of these instructions is to help you methodically record and organize knowledge as you progress through the game, enhancing your decision-making and strategic planning capabilities.

Observation: {observation}

Remember that triplets must be extracted in format: "subject_1, relation_1, object_1; subject_2, relation_2, object_2; ..."

Extracted triplets:'''

prompt_extraction_summary = '''Your task is to extract information from insight in structured formats to build a knowledge graph.
- **Nodes** represent entities and concepts. They are akin to Wikipedia nodes.
- The aim is to achieve simplicity and clarity in the knowledge graph, making it useful for you in the future.
- Triplets must save semantic structure of original text.
- Triplets must contain general knowledges about the game.
- Use the following triplet format for extracted data: "triplet1; triplet2; ...", more detailed - "subject1, relation1, object1; subject2, relation2, object2; ...", where a triplet is "subject1, relation1, object1" or "subject2, relation2, object2".
- Both subject and object in triplets should be akin to Wikipedia nodes. Object can be a date or number, objects should not contain citations or sentences.
- Instead of generating complex objects, divide triplet with complex object into two triplets with more precise objects. For example, the text "John Doe is a developer at Google" corresponds to two triplets: "John Doe, position, developer; John Doe, employed by, Google".
- Exclude from the extracted data triplets where object is a long phrase with more than 5 words.
- Similar relations, such as "has friend" and "friend of", replace with uniform relation, for example, "has friend"
- Similar entities, such as "House" and "house" or "small river" and "little river", replace with uniform relation, for example, "house" or "small river" 
- When extracting entities, it is vital to ensure consistency. If an entity, such as "John Doe", is mentioned multiple times in the text but is referred to by different names or pronouns (e.g., "Joe", "he"),
always use the most complete identifier for that entity throughout the knowledge graph. In this example, use "John Doe" as the entity ID.
Remember, the knowledge graph should be coherent and easily understandable, so maintaining consistency in entity references is crucial.
- Triplets must not include generalizations together with particular information (for example, from text "John see a rabbit, a horse and a dog" you should extract following data: "John, see, animals" with particular triplets like "John, see, rabbit", "John see, horse", "John, see, dog").
- Triplets that you are extracting must describe game rules, player's insights and generalization over past experience.

Observation: {observation}

Remember that triplets must be extracted in format: "subject_1, relation_1, object_1; subject_2, relation_2, object_2; ..."

Extracted triplets:'''

prompt_action_with_plan = '''You are an action selector within an agent system designed to navigate an environment in a text-based game. Your role involves receiving information about an agent and the state of the environment alongside a list of valid actions.
Your primary objective is to choose an action that aligns with the goals outlined in the plan, giving precedence to sub-goals in the order they appear (with sub_goal_1 being of the highest priority). However do not miss on actions that can benefit your main goal or can be dirrectly applied to achive one of the sub-goals, without disterbing you to much from hier order sub-goals.
In tasks centered around exploration or locating something, prioritize actions that guide the agent to previously unexplored areas. You can deduce which locations have been visited based on the history of observations or knowledge triples stored in your memory.
Respond only with the action you select.
####
Current data:
\n1. Main goal: {main_goal}
\n2. History of last observations and actions: {observations} 
\n3. Your current observation: {observation}
\n4. Information from the memory module that can be relevant to current situation. Pay attention to it it can contain information about location of different objects that an agent encountered earlier:  {subgraph}
\n5. Your current plan: {plan}

Please, in answer write only action you have chosen without any descriptions. Action: '''

prompt_plan_new = prompt = '''You are a planner within the agent system tasked with navigating the environment in a text-based game. 
Your role is to create a concise plan to achieve your primary goal or modify your current plan based on new information received. 

If you wish to alter or delete a sub-goal within the current plan, confirm that this sub-goal has been achieved according to the current observation. Untill then do not change wording in "sub_goal_..." elements of your plan, you may only change wording in "reason" behind this sub-goal, taking into account the events occurring in the environment. If you think sub-goal was achived, replase it with new one or with other sub-goals from the plan. 
Current data:
\n1. Main goal: {main_goal}
\n2. History of last observations and actions: {observations} 
\n3. Your current observation: {observation}
\n4. Information from the memory module that can be relevant to current situation. Pay attention to it it can contain information about location of different objects that an agent encountered earlier:  {subgraph}
\n5. Your current plan: {plan}

Write your answer exactly in this json format:
{{
  "main_goal": "...",
  "plan_steps": [
    {{
      "sub_goal_1": "...",
      "reason": "..."
    }},
    {{
      "sub_goal_2": "...",
      "reason": "..."
    }},
    {{
      "sub_goal_...": "...",
      "reason": "..."
    }}
  ],
}}
Answer: '''