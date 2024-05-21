ENV_NAMES = {
    "hunt": "./envs/hunt/hunt.z8",
    "hunt_hard": "./envs/hunt_hard/hunt_hard.z8",
    "cook": "./envs/cook/game.z8",
    "cook_hard": "./envs/cook_hard/game.z8",
    "cook_rl_baseline": "./envs/cook_rl_baseline/game.z8",
    "clean": "./envs/clean_3x3/clean_3x3_mess_1.z8",
}

FIRST_OBS = {
    "hunt": '\nYour task is to get a treasure. Treasure is hidden in the golden locker. You need a golden key to unlock it. The key is hidden in one of the other lockers located in the environment. All lockers are locked and require a specific key to unlock. The key 1 you found in room A unlocks white locker. Read the notes that you find, they will guide you further.',
    "hunt_hard": '\nYour task is to get a treasure. Treasure is hidden in the golden locker. You need a golden key to unlock it. The key is hidden in one of the other lockers located in the environment. All lockers are locked and require a specific key to unlock. The key 1 you found in room A unlocks white locker. Read the notes that you find, they will guide you further.',
    "cook": '\nYour task is to prepare the meal by following the recipe from a cookbook and eating it aftewards. Do not forget the content of recipe when you find it. When you will prepare food, remember that frying is done only with stove, roasting is done only with oven and grilling is done only with BBQ. Meal shoud be prepared in the kitchen. Do not forget to prepate meal after you gathered and processed all individual ingredients.',
    "cook_hard": '\nYour task is to prepare the meal by following the recipe from a cookbook and eating it aftewards. Do not forget the content of recipe when you find it. When you will prepare food, remember that frying is done only with stove, roasting is done only with oven and grilling is done only with BBQ. Meal shoud be prepared in the kitchen. Do not forget to prepate meal after you gathered and processed all individual ingredients.',
    "cook_rl_baseline": '\nYour task is to prepare the meal by following the recipe from a cookbook and eating it aftewards. Do not forget the content of recipe when you find it. When you will prepare food, remember that frying is done only with stove, roasting is done only with oven and grilling is done only with BBQ. Meal shoud be prepared in the kitchen. Do not forget to prepate meal after you gathered and processed all individual ingredients.',
    "clean": '\nYour task is to clean the house by locating and taking items that are out of place and returning them to their proper locations in the house.'
}

MAIN_GOALS = {
    "hunt": "Find the treasure",
    "hunt_hard": "Find the treasure",
    "cook": "Prepare meal by following the recipe and eat it",
    "cook_hard": "Prepare meal by following the recipe and eat it",
    "cook_rl_baseline": "Prepare meal by following the recipe and eat it",
    "clean": "Clean the house by returning items that are out of place to their proper locations"
}

WALKTHROUGH = {
    "hunt": ["take Key 1", "go west", "go south", "go east", "go east", "unlock White locker with Key 1", 
            "open White locker", "take Key 2 from White locker", "examine Note 2", "go west", "go west", "unlock Red locker with Key 2", 
            "open Red locker", "take Key 3 from Red locker", "take Note 3 from Red locker", "examine Note 3", "go east", "go east", 
            "go north", "go north", "go west", "go east", "go east", "unlock Cyan locker with Key 3", "open Cyan locker", 
            "take Golden key from Cyan locker", "go west", "go south", "go south", "go west", "go west", "go north", 
            "go east", "unclock Golden locker with Golden key", "unlock Golden locker with Golden key", "open Golden locker", 
            "take treasure from Golden locker"],
    "clean":  ['take toothbrush', 'go north', 'take dumbbell', 'take dirty plate', 'go east', 'take raw meat', 'go south', 
               'take wet towel', 'go south', 'take swimming fins', 'go west', 'take toy car', 
               'put swimming fins on equipment rack', 'go west', 'take fantasy book', 'put dumbbell on dumbbell stand', 
               'go north', 'take business suit', 'open refrigerator', 'put raw meat in refrigerator', 'close refrigerator', 
               'open dishwasher', 'put dirty plate in dishwasher', 'close dishwasher', 'go north', 'take sleeping lamp', 
               'take elegant table runner', 'put toothbrush on bathroom sink', 'put wet towel on towel rack', 'go east', 
               'open toy storage cabinet', 'put toy car in toy storage cabinet', 'close toy storage cabinet', 'go east', 
               'go south', 'open wardrobe', 'put business suit in wardrobe', 'close wardrobe', 
               'put sleeping lamp on bedside table', 'go south', 'put fantasy book on bookcase', 'go west', 'go north', 
               'put elegant table runner on dining table'],
    "cook": ['south', 'examine cookbook', 'take orange bell pepper', 'east', 'east', 'north', 'take green bell pepper', 
             'take yellow potato', 'south', 'cook orange bell pepper with BBQ', 'cook yellow potato with BBQ', 'west', 'west', 
             'take knife', 'dice green bell pepper', 'dice orange bell pepper', 'slice yellow potato', 
             'cook green bell pepper with stove', 'prepare meal', 'eat meal']
}

