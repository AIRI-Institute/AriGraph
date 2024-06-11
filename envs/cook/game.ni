Use MAX_STATIC_DATA of 500000.
When play begins, seed the random-number generator with 1234.

container is a kind of thing.
door is a kind of thing.
ingredient-like is a kind of thing.
object-like is a kind of thing.
supporter is a kind of thing.
oven-like is a kind of container.
toaster-like is a kind of container.
food is a kind of object-like.
key is a kind of object-like.
stove-like is a kind of supporter.
meal-like is a kind of food.
A recipe-like is a kind of thing. A recipe-like has a list of ingredient-like called ingredients. A recipe-like has a thing called meal. A recipe-like has a room called cooking location.
a thing can be drinkable. a thing is usually not drinkable. a thing can be cookable. a thing is usually not cookable. a thing can be damaged. a thing is usually not damaged. a thing can be sharp. a thing is usually not sharp. a thing can be cuttable. a thing is usually not cuttable. a thing can be a source of heat. Type of cooking is a kind of value. The type of cooking are raw, grilled, roasted and fried. a thing can be needs cooking. Type of cutting is a kind of value. The type of cutting are uncut, sliced, diced and chopped.
containers are openable, lockable and fixed in place. containers are usually closed.
door is openable and lockable.
ingredient-like has a thing called base. ingredient-like has a type of cooking. ingredient-like has a type of cutting.
object-like is portable.
supporters are fixed in place.
oven-like is a source of heat.
toaster-like is a source of heat.
food is usually edible. food is cookable. food has a type of cooking. food has a type of cutting. food can be cooked. food can be burned. food can be consumed. food is usually not consumed. food is usually cuttable.
stove-like is a source of heat.
A room has a text called internal name.


[Ingredient]
Rule for printing the name of an ingredient-like (called I):
	if type of cutting of I is not uncut:
		say  "[type of cutting of I] ";
	if type of cooking of I is not raw:
		say  "[type of cooking of I] ";
	say  "[base of I]";

[Preparing a meal]
Preparing meal is an action applying to nothing.
Before preparing meal:
	if location is not the cooking location of the recipe:
		say "Can only prepare meal in the [cooking location of the recipe].";
		rule fails;
	Repeat with ingredient running through the ingredients of the recipe:
		let F be the base of the ingredient;
		if player does not carry the F:
			[say "The recipe requires [a ingredient].";]
			say "You still miss something.";
			rule fails;
		if type of cooking of F is not type of cooking of ingredient:
			[say "The recipe requires [a ingredient].";]
			say "Something still needs to be cooked.";
			rule fails;
		if type of cutting of F is not type of cutting of ingredient:
			[say "The recipe requires [a ingredient].";]
			say "Something still needs to be cut.";
			rule fails;

Carry out preparing meal:
	say "Adding the meal to your inventory.";
	Repeat with ingredient running through the ingredients of recipe:
		now the base of the ingredient is nowhere;
	now the player carries the meal of the recipe;
	set pronouns from the meal of the recipe.

Understand "prepare meal" as preparing meal.


[Drinking liquid]
Drinking carried thing is an action applying to one carried thing.
The block drinking rule is not listed in any rulebook.
Understand nothing as drinking.
Understand "drink [something]" as drinking carried thing.

After drinking carried thing:
	Now the noun is consumed;
	Continue the action.

Check an actor drinking carried thing (this is the can’t drink unless drinkable rule):
	if the noun is not a thing or the noun is not drinkable:
		say "You cannot drink [the noun].";
		rule fails;

Carry out an actor drinking carried thing (this is the drinking rule):
	remove the noun from play.

Report an actor drinking carried thing (this is the report drinking rule):
	if the actor is the player:
		say "You drink [the noun]. Not bad.";
	otherwise:
		say "[The person asked] just drunk [the noun].".

[Eating food]
After eating a food (called target):
	Now the target is consumed;
	Continue the action.

Check eating inedible food (called target):
	if target is needs cooking:
		say "You should cook [the target] first.";
		rule fails.

[Understanding things by their properties - http://inform7.com/learn/man/WI_17_15.html]
Understand the type of cutting property as describing food.
Understand the type of cooking property as describing food.

[Processing food]
Understand the commands  "slice", "prune" as something new.
The block cutting rule is not listed in any rulebook.
Dicing it with is an action applying to two carried things.
Slicing it with is an action applying to two carried things.
Chopping it with is an action applying to two carried things.

Slicing something with something is a cutting activity.
Dicing something with something is a cutting activity.
Chopping something with something is a cutting activity.

Does the player mean slicing something with something carried (called target):
	if target is not sharp:
		it is very unlikely;

Does the player mean chopping something with something carried (called target):
	if target is not sharp:
		it is very unlikely;

Does the player mean dicing something with something carried (called target):
	if target is not sharp:
		it is very unlikely;

Check an actor cutting (this is the generic cut is now allowed rule):
	say "You need to specify how you want to cut [the noun]. Either slice, dice, or chop it.";
	rule fails.

Before a cutting activity when the noun is not cuttable:
	say "Can only cut cuttable food.";
	rule fails.

Before a cutting activity when the noun is cuttable and the noun is not uncut:
	say "[The noun] is already [type of cutting of the noun].";
	rule fails.

Before a cutting activity when the second noun is not sharp:
	say "Cutting something requires a knife.";
	rule fails.

Before printing the name of a food (called the food item) which is not uncut while looking, examining, listing contents or taking inventory:
	say "[type of cutting of food item] ".

[Slicing food]
Carry out slicing a carried food (called the food item) with a thing (called the tool):
	if the food item is not uncut:
		say "[The food item] is already [type of cutting of the food item].";
		stop;
	Now the food item is sliced;
	say "You slice the [food item].".

Understand "slice [something] with/using [something]" as slicing it with.

[Dicing food]
Carry out dicing a carried food (called the food item) with a thing (called the tool):
	if the food item is not uncut:
		say "The [food item] has already been cut.";
		stop;
	Now the food item is diced;
	say "You dice the [food item].".

Understand "dice [something] with/using [something]" as dicing it with.

[Chopping food]
Carry out chopping a carried food (called the food item) with a thing (called the tool):
	if the food item is not uncut:
		say "The [food item] has already been cut.";
		stop;
	Now the food item is chopped;
	say "You chop the [food item].".

Understand the command "chop" as something new. [Remove its association with slicing]
Understand "chop [something] with/using [something]" as chopping it with.

[Cooking food]
Cooking it with is an action applying to one carried thing and one thing.

Does the player mean cooking something with something carried:
	it is very unlikely;

Check cooking something not cookable with something (this is the cook only cookable things rule):
	say "Can only cook food." instead.

Check cooking something cookable with something not a source of heat (this is the cooking requires a source of heat rule):
	say "Cooking requires a source of heat." instead.

Carry out cooking a carried food (called the food item) with a thing (called a the source of heat):
	if the food item is cooked:
		Now the food item is burned;
		Now the food item is not edible;
		say "You burned the [food item]!";
		stop;
	otherwise:
		Now the food item is cooked;
	if the food item is needs cooking:
		Now the food item is edible;
		Now the food item is not needs cooking;
	if the source of heat is a stove-like:
		Now the food item is fried;
		say "You fried the [food item].";
	else if the source of heat is a oven-like:
		Now the food item is roasted;
		say "You roasted the [food item].";
	else if the source of heat is a toaster-like:
		Now the food item is grilled;
		say "You grilled the [food item].".

Understand "cook [something] with/in/on/using [something]" as cooking it with.

Before printing the name of a food (called the food item) while looking, examining, listing contents or taking inventory:
	if the food item is needs cooking:
		say "raw ";
	else if the food item is burned:
		say "burned ";
	else if the food item is not raw:
		say "[type of cooking of food item] ".



The r_0 and the r_1 and the r_2 and the r_4 and the r_6 and the r_8 and the r_3 and the r_5 and the r_7 are rooms.

Understand "kitchen" as r_0.
The internal name of r_0 is "kitchen".
The printed name of r_0 is "-= Kitchen =-".
The kitchen part 0 is some text that varies. The kitchen part 0 is "You find yourself in a kitchen. An usual one.

 [if c_0 is locked]A locked[else if c_0 is open]An open[otherwise]A closed[end if]".
The kitchen part 1 is some text that varies. The kitchen part 1 is " fridge is in the corner.[if c_0 is open and there is something in the c_0] The fridge contains [a list of things in the c_0].[end if]".
The kitchen part 2 is some text that varies. The kitchen part 2 is "[if c_0 is open and the c_0 contains nothing] Empty! What kind of nightmare TextWorld is this?[end if]".
The kitchen part 3 is some text that varies. The kitchen part 3 is " Were you looking for an oven? Because look over there, it's an oven.[if oven_0 is open and there is something in the oven_0] The oven contains [a list of things in the oven_0].[end if]".
The kitchen part 4 is some text that varies. The kitchen part 4 is "[if oven_0 is open and the oven_0 contains nothing] What a letdown! The oven is empty![end if]".
The kitchen part 5 is some text that varies. The kitchen part 5 is " You can make out a table. [if there is something on the s_0]You see [a list of things on the s_0] on the table.[end if]".
The kitchen part 6 is some text that varies. The kitchen part 6 is "[if there is nothing on the s_0]But the thing is empty, unfortunately.[end if]".
The kitchen part 7 is some text that varies. The kitchen part 7 is " You can make out a counter. I guess it's true what they say, if you're looking for a counter, go to TextWorld. The counter is vast.[if there is something on the s_1] On the counter you can make out [a list of things on the s_1].[end if]".
The kitchen part 8 is some text that varies. The kitchen part 8 is "[if there is nothing on the s_1] But the thing hasn't got anything on it. Aw, and here you were, all excited for there to be things on it![end if]".
The kitchen part 9 is some text that varies. The kitchen part 9 is " Look out! It's a- oh, never mind, it's just a stove. The stove is conventional.[if there is something on the stove_0] On the stove you make out [a list of things on the stove_0].[end if]".
The kitchen part 10 is some text that varies. The kitchen part 10 is "[if there is nothing on the stove_0] Looks like someone's already been here and taken everything off it, though.[end if]".
The kitchen part 11 is some text that varies. The kitchen part 11 is "

 There is [if d_0 is open]an open[otherwise]a closed[end if]".
The kitchen part 12 is some text that varies. The kitchen part 12 is " frosted-glass door leading south. You need an exit without a door? You should try going east. You don't like doors? Why not try going north, that entranceway is not blocked by one.".
The description of r_0 is "[kitchen part 0][kitchen part 1][kitchen part 2][kitchen part 3][kitchen part 4][kitchen part 5][kitchen part 6][kitchen part 7][kitchen part 8][kitchen part 9][kitchen part 10][kitchen part 11][kitchen part 12]".

south of r_0 and north of r_5 is a door called d_0.
The r_4 is mapped north of r_0.
The r_1 is mapped east of r_0.
Understand "corridor" as r_1.
The internal name of r_1 is "corridor".
The printed name of r_1 is "-= Corridor =-".
The corridor part 0 is some text that varies. The corridor part 0 is "You arrive in a corridor. An usual one. You can barely contain your excitement.



 There is [if d_1 is open]an open[otherwise]a closed[end if]".
The corridor part 1 is some text that varies. The corridor part 1 is " screen door leading east. You need an exit without a door? You should try going north. You don't like doors? Why not try going south, that entranceway is not blocked by one. You need an exit without a door? You should try going west.".
The description of r_1 is "[corridor part 0][corridor part 1]".

The r_0 is mapped west of r_1.
The r_3 is mapped south of r_1.
The r_2 is mapped north of r_1.
east of r_1 and west of r_6 is a door called d_1.
Understand "bedroom" as r_2.
The internal name of r_2 is "bedroom".
The printed name of r_2 is "-= Bedroom =-".
The bedroom part 0 is some text that varies. The bedroom part 0 is "Guess what, you are in a place we're calling a bedroom.

 Oh wow! Is that what I think it is? It is! It's a bed. The bed is large.[if there is something on the s_3] On the bed you can make out [a list of things on the s_3].[end if]".
The bedroom part 1 is some text that varies. The bedroom part 1 is "[if there is nothing on the s_3] But there isn't a thing on it. Silly bed, silly, empty, good for nothing bed.[end if]".
The bedroom part 2 is some text that varies. The bedroom part 2 is "

There is an exit to the south. There is an exit to the west.".
The description of r_2 is "[bedroom part 0][bedroom part 1][bedroom part 2]".

The r_4 is mapped west of r_2.
The r_1 is mapped south of r_2.
Understand "livingroom" as r_4.
The internal name of r_4 is "livingroom".
The printed name of r_4 is "-= Livingroom =-".
The livingroom part 0 is some text that varies. The livingroom part 0 is "You're now in the livingroom.

 You see a sofa. [if there is something on the s_4]On the sofa you can see [a list of things on the s_4].[end if]".
The livingroom part 1 is some text that varies. The livingroom part 1 is "[if there is nothing on the s_4]Looks like someone's already been here and taken everything off it, though.[end if]".
The livingroom part 2 is some text that varies. The livingroom part 2 is "

There is an exit to the east. You need an exit without a door? You should try going south.".
The description of r_4 is "[livingroom part 0][livingroom part 1][livingroom part 2]".

The r_0 is mapped south of r_4.
The r_2 is mapped east of r_4.
Understand "backyard" as r_6.
The internal name of r_6 is "backyard".
The printed name of r_6 is "-= Backyard =-".
The backyard part 0 is some text that varies. The backyard part 0 is "You find yourself in a backyard. An ordinary kind of place.

 Oh wow! Is that what I think it is? It is! It's a patio table. [if there is something on the s_6]On the patio table you can make out [a list of things on the s_6].[end if]".
The backyard part 1 is some text that varies. The backyard part 1 is "[if there is nothing on the s_6]The patio table appears to be empty.[end if]".
The backyard part 2 is some text that varies. The backyard part 2 is " You see a patio chair. The patio chair is stylish.[if there is something on the s_8] On the patio chair you see [a list of things on the s_8].[end if]".
The backyard part 3 is some text that varies. The backyard part 3 is "[if there is nothing on the s_8] However, the patio chair, like an empty patio chair, has nothing on it.[end if]".
The backyard part 4 is some text that varies. The backyard part 4 is " You see a BBQ.[if toaster_0 is open and there is something in the toaster_0] The BBQ contains [a list of things in the toaster_0].[end if]".
The backyard part 5 is some text that varies. The backyard part 5 is "[if toaster_0 is open and the toaster_0 contains nothing] What a letdown! The BBQ is empty![end if]".
The backyard part 6 is some text that varies. The backyard part 6 is "

 There is [if d_2 is open]an open[otherwise]a closed[end if]".
The backyard part 7 is some text that varies. The backyard part 7 is " wooden door leading east. There is [if d_1 is open]an open[otherwise]a closed[end if]".
The backyard part 8 is some text that varies. The backyard part 8 is " screen door leading west. There is an exit to the north.".
The description of r_6 is "[backyard part 0][backyard part 1][backyard part 2][backyard part 3][backyard part 4][backyard part 5][backyard part 6][backyard part 7][backyard part 8]".

west of r_6 and east of r_1 is a door called d_1.
The r_7 is mapped north of r_6.
east of r_6 and west of r_8 is a door called d_2.
Understand "shed" as r_8.
The internal name of r_8 is "shed".
The printed name of r_8 is "-= Shed =-".
The shed part 0 is some text that varies. The shed part 0 is "You arrive in a shed. An ordinary kind of place.

 You lean against the wall, inadvertently pressing a secret button. The wall opens up to reveal a toolbox.[if c_1 is open and there is something in the c_1] The toolbox contains [a list of things in the c_1]. You shudder, but continue examining the room.[end if]".
The shed part 1 is some text that varies. The shed part 1 is "[if c_1 is open and the c_1 contains nothing] The toolbox is empty! This is the worst thing that could possibly happen, ever![end if]".
The shed part 2 is some text that varies. The shed part 2 is " You can make out a workbench. [if there is something on the s_5]On the workbench you can make out [a list of things on the s_5].[end if]".
The shed part 3 is some text that varies. The shed part 3 is "[if there is nothing on the s_5]However, the workbench, like an empty workbench, has nothing on it.[end if]".
The shed part 4 is some text that varies. The shed part 4 is "

 There is [if d_2 is open]an open[otherwise]a closed[end if]".
The shed part 5 is some text that varies. The shed part 5 is " wooden door leading west.".
The description of r_8 is "[shed part 0][shed part 1][shed part 2][shed part 3][shed part 4][shed part 5]".

west of r_8 and east of r_6 is a door called d_2.
Understand "bathroom" as r_3.
The internal name of r_3 is "bathroom".
The printed name of r_3 is "-= Bathroom =-".
The bathroom part 0 is some text that varies. The bathroom part 0 is "Well, here we are in a bathroom.

 You can make out a toilet. [if there is something on the s_7]On the toilet you make out [a list of things on the s_7].[end if]".
The bathroom part 1 is some text that varies. The bathroom part 1 is "[if there is nothing on the s_7]Unfortunately, there isn't a thing on it.[end if]".
The bathroom part 2 is some text that varies. The bathroom part 2 is "

You don't like doors? Why not try going north, that entranceway is not blocked by one.".
The description of r_3 is "[bathroom part 0][bathroom part 1][bathroom part 2]".

The r_1 is mapped north of r_3.
Understand "pantry" as r_5.
The internal name of r_5 is "pantry".
The printed name of r_5 is "-= Pantry =-".
The pantry part 0 is some text that varies. The pantry part 0 is "You find yourself in a pantry. An usual kind of place.

 You bend down to tie your shoe. When you stand up, you notice a shelf. The shelf is wooden.[if there is something on the s_2] On the shelf you see [a list of things on the s_2].[end if]".
The pantry part 1 is some text that varies. The pantry part 1 is "[if there is nothing on the s_2] Unfortunately, there isn't a thing on it.[end if]".
The pantry part 2 is some text that varies. The pantry part 2 is "

 There is [if d_0 is open]an open[otherwise]a closed[end if]".
The pantry part 3 is some text that varies. The pantry part 3 is " frosted-glass door leading north.".
The description of r_5 is "[pantry part 0][pantry part 1][pantry part 2][pantry part 3]".

north of r_5 and south of r_0 is a door called d_0.
Understand "garden" as r_7.
The internal name of r_7 is "garden".
The printed name of r_7 is "-= Garden =-".
The garden part 0 is some text that varies. The garden part 0 is "You arrive in a garden. A typical one. You start to take note of what's in the room.



There is an exit to the south. Don't worry, there is no door.".
The description of r_7 is "[garden part 0]".

The r_6 is mapped south of r_7.

The RECIPE are recipe-likes.
The RECIPE are privately-named.
The c_0 and the c_1 are containers.
The c_0 and the c_1 are privately-named.
The d_0 and the d_1 and the d_2 are doors.
The d_0 and the d_1 and the d_2 are privately-named.
The f_1 and the f_2 and the f_3 and the f_4 and the f_6 and the f_7 and the f_9 and the f_0 and the f_5 and the f_8 are foods.
The f_1 and the f_2 and the f_3 and the f_4 and the f_6 and the f_7 and the f_9 and the f_0 and the f_5 and the f_8 are privately-named.
The ingredient_0 and the ingredient_1 and the ingredient_2 are ingredient-likes.
The ingredient_0 and the ingredient_1 and the ingredient_2 are privately-named.
The meal_0 are meal-likes.
The meal_0 are privately-named.
The o_0 and the o_1 are object-likes.
The o_0 and the o_1 are privately-named.
The oven_0 are oven-likes.
The oven_0 are privately-named.
The r_0 and the r_1 and the r_2 and the r_4 and the r_6 and the r_8 and the r_3 and the r_5 and the r_7 are rooms.
The r_0 and the r_1 and the r_2 and the r_4 and the r_6 and the r_8 and the r_3 and the r_5 and the r_7 are privately-named.
The s_0 and the s_1 and the s_2 and the s_3 and the s_4 and the s_5 and the s_6 and the s_7 and the s_8 are supporters.
The s_0 and the s_1 and the s_2 and the s_3 and the s_4 and the s_5 and the s_6 and the s_7 and the s_8 are privately-named.
The stove_0 are stove-likes.
The stove_0 are privately-named.
The toaster_0 are toaster-likes.
The toaster_0 are privately-named.

The description of d_0 is "It is what it is, a [noun]. [if open]It is open.[else if locked]It is locked.[otherwise]It is closed.[end if]".
The printed name of d_0 is "frosted-glass door".
Understand "frosted-glass door" as d_0.
Understand "frosted-glass" as d_0.
Understand "door" as d_0.
The d_0 is open.
The description of d_1 is "The [noun] looks manageable. [if open]It is open.[else if locked]It is locked.[otherwise]It is closed.[end if]".
The printed name of d_1 is "screen door".
Understand "screen door" as d_1.
Understand "screen" as d_1.
Understand "door" as d_1.
The d_1 is open.
The description of d_2 is "It is what it is, a [noun]. [if open]You can see inside it.[else if locked]There is a lock on it and seems impossible to crack open.[otherwise]You can't see inside it because the lid's in your way.[end if]".
The printed name of d_2 is "wooden door".
Understand "wooden door" as d_2.
Understand "wooden" as d_2.
Understand "door" as d_2.
The d_2 is open.
The description of c_0 is "The [noun] looks grand. [if open]You can see inside it.[else if locked]There is a lock on it and seems impossible to bash open.[otherwise]You can't see inside it because the lid's in your way.[end if]".
The printed name of c_0 is "fridge".
Understand "fridge" as c_0.
The c_0 is in r_0.
The c_0 is open.
The description of c_1 is "The [noun] looks stuffy. [if open]It is open.[else if locked]It is locked.[otherwise]It is closed.[end if]".
The printed name of c_1 is "toolbox".
Understand "toolbox" as c_1.
The c_1 is in r_8.
The c_1 is open.
The description of f_1 is "That's a [noun]!".
The printed name of f_1 is "yellow potato".
Understand "yellow potato" as f_1.
Understand "yellow" as f_1.
Understand "potato" as f_1.
The f_1 is in r_7.
The base of ingredient_2 is f_1.
The f_1 is cookable.
The f_1 is cuttable.
The f_1 is inedible.
The f_1 is needs cooking.
The f_1 is uncut.
The description of f_2 is "You couldn't pay me to eat that [noun].".
The printed name of f_2 is "green bell pepper".
Understand "green bell pepper" as f_2.
Understand "green" as f_2.
Understand "bell" as f_2.
Understand "pepper" as f_2.
The f_2 is in r_7.
The base of ingredient_0 is f_2.
The f_2 is cookable.
The f_2 is cuttable.
The f_2 is edible.
The f_2 is raw.
The f_2 is uncut.
The description of f_3 is "The [noun] looks tempting.".
The printed name of f_3 is "green hot pepper".
Understand "green hot pepper" as f_3.
Understand "green" as f_3.
Understand "hot" as f_3.
Understand "pepper" as f_3.
The f_3 is in r_7.
The f_3 is cookable.
The f_3 is cuttable.
The f_3 is edible.
The f_3 is raw.
The f_3 is uncut.
The description of f_4 is "That's a [noun]!".
The printed name of f_4 is "red hot pepper".
Understand "red hot pepper" as f_4.
Understand "red" as f_4.
Understand "hot" as f_4.
Understand "pepper" as f_4.
The f_4 is in r_7.
The f_4 is cookable.
The f_4 is cuttable.
The f_4 is edible.
The f_4 is raw.
The f_4 is uncut.
The description of f_6 is "The [noun] looks inviting.".
The printed name of f_6 is "yellow apple".
Understand "yellow apple" as f_6.
Understand "yellow" as f_6.
Understand "apple" as f_6.
The f_6 is in r_7.
The f_6 is cookable.
The f_6 is cuttable.
The f_6 is edible.
The f_6 is raw.
The f_6 is uncut.
The description of f_7 is "That's a [noun]!".
The printed name of f_7 is "purple potato".
Understand "purple potato" as f_7.
Understand "purple" as f_7.
Understand "potato" as f_7.
The f_7 is in r_7.
The f_7 is cookable.
The f_7 is cuttable.
The f_7 is inedible.
The f_7 is needs cooking.
The f_7 is uncut.
The description of f_9 is "That's a [noun]!".
The printed name of f_9 is "red onion".
Understand "red onion" as f_9.
Understand "red" as f_9.
Understand "onion" as f_9.
The f_9 is in r_7.
The f_9 is cookable.
The f_9 is cuttable.
The f_9 is edible.
The f_9 is raw.
The f_9 is uncut.
The description of oven_0 is "Useful for roasting things.".
The printed name of oven_0 is "oven".
Understand "oven" as oven_0.
The oven_0 is in r_0.
The description of s_0 is "The [noun] is durable.".
The printed name of s_0 is "table".
Understand "table" as s_0.
The s_0 is in r_0.
The description of s_1 is "The [noun] is reliable.".
The printed name of s_1 is "counter".
Understand "counter" as s_1.
The s_1 is in r_0.
The description of s_2 is "The [noun] is reliable.".
The printed name of s_2 is "shelf".
Understand "shelf" as s_2.
The s_2 is in r_5.
The description of s_3 is "The [noun] is an unstable piece of junk.".
The printed name of s_3 is "bed".
Understand "bed" as s_3.
The s_3 is in r_2.
The description of s_4 is "The [noun] is stable.".
The printed name of s_4 is "sofa".
Understand "sofa" as s_4.
The s_4 is in r_4.
The description of s_5 is "The [noun] is wobbly.".
The printed name of s_5 is "workbench".
Understand "workbench" as s_5.
The s_5 is in r_8.
The description of s_6 is "The [noun] is balanced.".
The printed name of s_6 is "patio table".
Understand "patio table" as s_6.
Understand "patio" as s_6.
Understand "table" as s_6.
The s_6 is in r_6.
The description of s_7 is "The [noun] is unstable.".
The printed name of s_7 is "toilet".
Understand "toilet" as s_7.
The s_7 is in r_3.
The description of s_8 is "The [noun] is solidly built.".
The printed name of s_8 is "patio chair".
Understand "patio chair" as s_8.
Understand "patio" as s_8.
Understand "chair" as s_8.
The s_8 is in r_6.
The description of stove_0 is "Useful for frying things.".
The printed name of stove_0 is "stove".
Understand "stove" as stove_0.
The stove_0 is in r_0.
The description of toaster_0 is "Useful for grilling things.".
The printed name of toaster_0 is "BBQ".
Understand "BBQ" as toaster_0.
The toaster_0 is in r_6.
The description of f_0 is "You couldn't pay me to eat that [noun].".
The printed name of f_0 is "orange bell pepper".
Understand "orange bell pepper" as f_0.
Understand "orange" as f_0.
Understand "bell" as f_0.
Understand "pepper" as f_0.
The base of ingredient_1 is f_0.
The f_0 is cookable.
The f_0 is cuttable.
The f_0 is edible.
The f_0 is in the c_0.
The f_0 is raw.
The f_0 is uncut.
The description of f_5 is "You couldn't pay me to eat that [noun].".
The printed name of f_5 is "red bell pepper".
Understand "red bell pepper" as f_5.
Understand "red" as f_5.
Understand "bell" as f_5.
Understand "pepper" as f_5.
The f_5 is cookable.
The f_5 is cuttable.
The f_5 is edible.
The f_5 is in the c_0.
The f_5 is raw.
The f_5 is uncut.
The description of f_8 is "You couldn't pay me to eat that [noun].".
The printed name of f_8 is "white tuna".
Understand "white tuna" as f_8.
Understand "white" as f_8.
Understand "tuna" as f_8.
The f_8 is cookable.
The f_8 is cuttable.
The f_8 is in the c_0.
The f_8 is inedible.
The f_8 is needs cooking.
The f_8 is uncut.
The description of ingredient_0 is "".
The printed name of ingredient_0 is "".
The ingredient_0 is diced.
The ingredient_0 is fried.
When play begins, add ingredient_0 to the ingredients of the RECIPE.
The description of ingredient_1 is "".
The printed name of ingredient_1 is "".
The ingredient_1 is diced.
The ingredient_1 is grilled.
When play begins, add ingredient_1 to the ingredients of the RECIPE.
The description of meal_0 is "".
The printed name of meal_0 is "meal".
Understand "meal" as meal_0.
The meal_0 is edible.
The meal of the RECIPE is the meal_0..
The description of ingredient_2 is "".
The printed name of ingredient_2 is "".
The ingredient_2 is grilled.
When play begins, add ingredient_2 to the ingredients of the RECIPE.
The ingredient_2 is sliced.
The description of RECIPE is "".
The printed name of RECIPE is "".
The description of o_0 is "You open the copy of 'Cooking: A Modern Approach (3rd Ed.)' and start reading:[line break][line break]Recipe #1[line break]---------[line break]Gather all following ingredients and follow the directions to prepare this tasty meal.[line break][line break]Ingredients:[line break]green bell pepper[line break]  orange bell pepper[line break]  yellow potato[line break][line break]Directions:[line break]dice the green bell pepper[line break]  fry the green bell pepper[line break]  dice the orange bell pepper[line break]  grill the orange bell pepper[line break]  slice the yellow potato[line break]  grill the yellow potato[line break]  prepare meal[line break]".
The printed name of o_0 is "cookbook".
Understand "recipe" as o_0.
Understand "cookbook" as o_0.
The o_0 is on the s_0.
The description of o_1 is "The [noun] is dirty.".
The printed name of o_1 is "knife".
Understand "knife" as o_1.
The o_1 is on the s_0.
The o_1 is sharp.


The player is in r_4.

The quest0 completed is a truth state that varies.
The quest0 completed is usually false.
Every turn:
	if quest0 completed is true:
		do nothing;
	else if The f_2 is burned:
		end the story; [Lost]

The quest1 completed is a truth state that varies.
The quest1 completed is usually false.

Test quest1_0 with "inventory / go south / examine cookbook / go east / go east / go east / go north / take green bell pepper"

Every turn:
	if quest1 completed is true:
		do nothing;
	else if The player carries the f_2:
		increase the score by 1; [Quest completed]
		if 1 is 1 [always true]:
			Now the quest1 completed is true;

The quest2 completed is a truth state that varies.
The quest2 completed is usually false.

Test quest2_0 with "inventory / go south / examine cookbook / go east / go east / go east / go north / take green bell pepper / go south / go south / go west / go west / take orange bell pepper from fridge / go east / go east / go east / go north / take yellow potato / go south / go south / go west / go west / cook green bell pepper with stove"

Every turn:
	if quest2 completed is true:
		do nothing;
	else if The f_2 is consumed:
		end the story; [Lost]
	else if The f_2 is roasted:
		end the story; [Lost]
	else if The f_2 is grilled:
		end the story; [Lost]
	else if The f_2 is fried:
		increase the score by 1; [Quest completed]
		if 1 is 1 [always true]:
			Now the quest2 completed is true;

The quest3 completed is a truth state that varies.
The quest3 completed is usually false.

Test quest3_0 with "inventory / go south / examine cookbook / go east / go east / go east / go north / take green bell pepper / go south / go south / go west / go west / take orange bell pepper from fridge / go east / go east / go east / go north / take yellow potato / go south / go south / go west / go west / cook green bell pepper with stove / go east / go east / go east / cook orange bell pepper with BBQ / cook orange bell pepper with BBQ / go west / go west / go east / go east / go east / cook yellow potato with BBQ / cook yellow potato with BBQ / go west / go west / take knife from table / dice green bell pepper with knife"

Every turn:
	if quest3 completed is true:
		do nothing;
	else if The f_2 is consumed:
		end the story; [Lost]
	else if The f_2 is chopped:
		end the story; [Lost]
	else if The f_2 is sliced:
		end the story; [Lost]
	else if The f_2 is diced:
		increase the score by 1; [Quest completed]
		if 1 is 1 [always true]:
			Now the quest3 completed is true;

The quest4 completed is a truth state that varies.
The quest4 completed is usually false.
Every turn:
	if quest4 completed is true:
		do nothing;
	else if The f_0 is burned:
		end the story; [Lost]

The quest5 completed is a truth state that varies.
The quest5 completed is usually false.

Test quest5_0 with "inventory / go south / examine cookbook / go east / go east / go east / go north / take green bell pepper / go south / go south / go west / go west / take orange bell pepper from fridge"

Every turn:
	if quest5 completed is true:
		do nothing;
	else if The player carries the f_0:
		increase the score by 1; [Quest completed]
		if 1 is 1 [always true]:
			Now the quest5 completed is true;

The quest6 completed is a truth state that varies.
The quest6 completed is usually false.

Test quest6_0 with "inventory / go south / examine cookbook / go east / go east / go east / go north / take green bell pepper / go south / go south / go west / go west / take orange bell pepper from fridge / go east / go east / go east / go north / take yellow potato / go south / go south / go west / go west / cook green bell pepper with stove / go east / go east / go east / cook orange bell pepper with BBQ"

Every turn:
	if quest6 completed is true:
		do nothing;
	else if The f_0 is consumed:
		end the story; [Lost]
	else if The f_0 is roasted:
		end the story; [Lost]
	else if The f_0 is fried:
		end the story; [Lost]
	else if The f_0 is grilled:
		increase the score by 1; [Quest completed]
		if 1 is 1 [always true]:
			Now the quest6 completed is true;

The quest7 completed is a truth state that varies.
The quest7 completed is usually false.

Test quest7_0 with "inventory / go south / examine cookbook / go east / go east / go east / go north / take green bell pepper / go south / go south / go west / go west / take orange bell pepper from fridge / go east / go east / go east / go north / take yellow potato / go south / go south / go west / go west / cook green bell pepper with stove / go east / go east / go east / cook orange bell pepper with BBQ / cook orange bell pepper with BBQ / go west / go west / go east / go east / go east / cook yellow potato with BBQ / cook yellow potato with BBQ / go west / go west / take knife from table / dice green bell pepper with knife / drop knife / take knife / dice orange bell pepper with knife"

Every turn:
	if quest7 completed is true:
		do nothing;
	else if The f_0 is consumed:
		end the story; [Lost]
	else if The f_0 is chopped:
		end the story; [Lost]
	else if The f_0 is sliced:
		end the story; [Lost]
	else if The f_0 is diced:
		increase the score by 1; [Quest completed]
		if 1 is 1 [always true]:
			Now the quest7 completed is true;

The quest8 completed is a truth state that varies.
The quest8 completed is usually false.
Every turn:
	if quest8 completed is true:
		do nothing;
	else if The f_1 is burned:
		end the story; [Lost]

The quest9 completed is a truth state that varies.
The quest9 completed is usually false.

Test quest9_0 with "inventory / go south / examine cookbook / go east / go east / go east / go north / take green bell pepper / go south / go south / go west / go west / take orange bell pepper from fridge / go east / go east / go east / go north / take yellow potato"

Every turn:
	if quest9 completed is true:
		do nothing;
	else if The player carries the f_1:
		increase the score by 1; [Quest completed]
		if 1 is 1 [always true]:
			Now the quest9 completed is true;

The quest10 completed is a truth state that varies.
The quest10 completed is usually false.

Test quest10_0 with "inventory / go south / examine cookbook / go east / go east / go east / go north / take green bell pepper / go south / go south / go west / go west / take orange bell pepper from fridge / go east / go east / go east / go north / take yellow potato / go south / go south / go west / go west / cook green bell pepper with stove / go east / go east / go east / cook orange bell pepper with BBQ / cook orange bell pepper with BBQ / go west / go west / go east / go east / go east / cook yellow potato with BBQ"

Every turn:
	if quest10 completed is true:
		do nothing;
	else if The f_1 is consumed:
		end the story; [Lost]
	else if The f_1 is roasted:
		end the story; [Lost]
	else if The f_1 is fried:
		end the story; [Lost]
	else if The f_1 is grilled:
		increase the score by 1; [Quest completed]
		if 1 is 1 [always true]:
			Now the quest10 completed is true;

The quest11 completed is a truth state that varies.
The quest11 completed is usually false.

Test quest11_0 with "inventory / go south / examine cookbook / go east / go east / go east / go north / take green bell pepper / go south / go south / go west / go west / take orange bell pepper from fridge / go east / go east / go east / go north / take yellow potato / go south / go south / go west / go west / cook green bell pepper with stove / go east / go east / go east / cook orange bell pepper with BBQ / cook orange bell pepper with BBQ / go west / go west / go east / go east / go east / cook yellow potato with BBQ / cook yellow potato with BBQ / go west / go west / take knife from table / dice green bell pepper with knife / drop knife / take knife / dice orange bell pepper with knife / drop knife / take knife / slice yellow potato with knife"

Every turn:
	if quest11 completed is true:
		do nothing;
	else if The f_1 is consumed:
		end the story; [Lost]
	else if The f_1 is chopped:
		end the story; [Lost]
	else if The f_1 is diced:
		end the story; [Lost]
	else if The f_1 is sliced:
		increase the score by 1; [Quest completed]
		if 1 is 1 [always true]:
			Now the quest11 completed is true;

The quest12 completed is a truth state that varies.
The quest12 completed is usually false.

Test quest12_0 with "inventory / go south / examine cookbook / go east / go east / go east / go north / take green bell pepper / go south / go south / go west / go west / take orange bell pepper from fridge / go east / go east / go east / go north / take yellow potato / go south / go south / go west / go west / cook green bell pepper with stove / go east / go east / go east / cook orange bell pepper with BBQ / cook orange bell pepper with BBQ / go west / go west / go east / go east / go east / cook yellow potato with BBQ / cook yellow potato with BBQ / go west / go west / take knife from table / dice green bell pepper with knife / drop knife / take knife / dice orange bell pepper with knife / drop knife / take knife / slice yellow potato with knife / drop knife / prepare meal"

Every turn:
	if quest12 completed is true:
		do nothing;
	else if The f_2 is consumed:
		end the story; [Lost]
	else if The f_0 is consumed:
		end the story; [Lost]
	else if The f_1 is consumed:
		end the story; [Lost]
	else if The player carries the meal_0:
		increase the score by 1; [Quest completed]
		if 1 is 1 [always true]:
			Now the quest12 completed is true;

The quest13 completed is a truth state that varies.
The quest13 completed is usually false.

Test quest13_0 with "inventory / go south / examine cookbook / go east / go east / go east / go north / take green bell pepper / go south / go south / go west / go west / take orange bell pepper from fridge / go east / go east / go east / go north / take yellow potato / go south / go south / go west / go west / cook green bell pepper with stove / go east / go east / go east / cook orange bell pepper with BBQ / cook orange bell pepper with BBQ / go west / go west / go east / go east / go east / cook yellow potato with BBQ / cook yellow potato with BBQ / go west / go west / take knife from table / dice green bell pepper with knife / drop knife / take knife / dice orange bell pepper with knife / drop knife / take knife / slice yellow potato with knife / drop knife / prepare meal / eat meal"

Every turn:
	if quest13 completed is true:
		do nothing;
	else if The meal_0 is burned:
		end the story; [Lost]
	else if The meal_0 is consumed:
		increase the score by 1; [Quest completed]
		if 1 is 1 [always true]:
			Now the quest13 completed is true;

Use scoring. The maximum score is 11.
This is the simpler notify score changes rule:
	If the score is not the last notified score:
		let V be the score - the last notified score;
		if V > 0:
			say "Your score has just gone up by [V in words] ";
		else:
			say "Your score changed by [V in words] ";
		if V >= -1 and V <= 1:
			say "point.";
		else:
			say "points.";
		Now the last notified score is the score;
	if quest1 completed is true and quest2 completed is true and quest3 completed is true and quest5 completed is true and quest6 completed is true and quest7 completed is true and quest9 completed is true and quest10 completed is true and quest11 completed is true and quest12 completed is true and quest13 completed is true:
		end the story finally; [Win]

The simpler notify score changes rule substitutes for the notify score changes rule.

Rule for listing nondescript items:
	stop.

Rule for printing the banner text:
	say "[fixed letter spacing]";
	say "                    ________  ________  __    __  ________        [line break]";
	say "                   |        \|        \|  \  |  \|        \       [line break]";
	say "                    \$$$$$$$$| $$$$$$$$| $$  | $$ \$$$$$$$$       [line break]";
	say "                      | $$   | $$__     \$$\/  $$   | $$          [line break]";
	say "                      | $$   | $$  \     >$$  $$    | $$          [line break]";
	say "                      | $$   | $$$$$    /  $$$$\    | $$          [line break]";
	say "                      | $$   | $$_____ |  $$ \$$\   | $$          [line break]";
	say "                      | $$   | $$     \| $$  | $$   | $$          [line break]";
	say "                       \$$    \$$$$$$$$ \$$   \$$    \$$          [line break]";
	say "              __       __   ______   _______   __        _______  [line break]";
	say "             |  \  _  |  \ /      \ |       \ |  \      |       \ [line break]";
	say "             | $$ / \ | $$|  $$$$$$\| $$$$$$$\| $$      | $$$$$$$\[line break]";
	say "             | $$/  $\| $$| $$  | $$| $$__| $$| $$      | $$  | $$[line break]";
	say "             | $$  $$$\ $$| $$  | $$| $$    $$| $$      | $$  | $$[line break]";
	say "             | $$ $$\$$\$$| $$  | $$| $$$$$$$\| $$      | $$  | $$[line break]";
	say "             | $$$$  \$$$$| $$__/ $$| $$  | $$| $$_____ | $$__/ $$[line break]";
	say "             | $$$    \$$$ \$$    $$| $$  | $$| $$     \| $$    $$[line break]";
	say "              \$$      \$$  \$$$$$$  \$$   \$$ \$$$$$$$$ \$$$$$$$ [line break]";
	say "[variable letter spacing][line break]";
	say "[objective][line break]".

Include Basic Screen Effects by Emily Short.

Rule for printing the player's obituary:
	if story has ended finally:
		center "*** The End ***";
	else:
		center "*** You lost! ***";
	say paragraph break;
	if maximum score is -32768:
		say "You scored a total of [score] point[s], in [turn count] turn[s].";
	else:
		say "You scored [score] out of a possible [maximum score], in [turn count] turn[s].";
	[wait for any key;
	stop game abruptly;]
	rule succeeds.

Carry out requesting the score:
	if maximum score is -32768:
		say "You have so far scored [score] point[s], in [turn count] turn[s].";
	else:
		say "You have so far scored [score] out of a possible [maximum score], in [turn count] turn[s].";
	rule succeeds.

Rule for implicitly taking something (called target):
	if target is fixed in place:
		say "The [target] is fixed in place.";
	otherwise:
		say "You need to take the [target] first.";
		set pronouns from target;
	stop.

Does the player mean doing something:
	if the noun is not nothing and the second noun is nothing and the player's command matches the text printed name of the noun:
		it is likely;
	if the noun is nothing and the second noun is not nothing and the player's command matches the text printed name of the second noun:
		it is likely;
	if the noun is not nothing and the second noun is not nothing and the player's command matches the text printed name of the noun and the player's command matches the text printed name of the second noun:
		it is very likely.  [Handle action with two arguments.]

Printing the content of the room is an activity.
Rule for printing the content of the room:
	let R be the location of the player;
	say "Room contents:[line break]";
	list the contents of R, with newlines, indented, including all contents, with extra indentation.

Printing the content of the world is an activity.
Rule for printing the content of the world:
	let L be the list of the rooms;
	say "World: [line break]";
	repeat with R running through L:
		say "  [the internal name of R][line break]";
	repeat with R running through L:
		say "[the internal name of R]:[line break]";
		if the list of things in R is empty:
			say "  nothing[line break]";
		otherwise:
			list the contents of R, with newlines, indented, including all contents, with extra indentation.

Printing the content of the inventory is an activity.
Rule for printing the content of the inventory:
	say "You are carrying: ";
	list the contents of the player, as a sentence, giving inventory information, including all contents;
	say ".".

The print standard inventory rule is not listed in any rulebook.
Carry out taking inventory (this is the new print inventory rule):
	say "You are carrying: ";
	list the contents of the player, as a sentence, giving inventory information, including all contents;
	say ".".

Printing the content of nowhere is an activity.
Rule for printing the content of nowhere:
	say "Nowhere:[line break]";
	let L be the list of the off-stage things;
	repeat with thing running through L:
		say "  [thing][line break]";

Printing the things on the floor is an activity.
Rule for printing the things on the floor:
	let R be the location of the player;
	let L be the list of things in R;
	remove yourself from L;
	remove the list of containers from L;
	remove the list of supporters from L;
	remove the list of doors from L;
	if the number of entries in L is greater than 0:
		say "There is [L with indefinite articles] on the floor.";

After printing the name of something (called target) while
printing the content of the room
or printing the content of the world
or printing the content of the inventory
or printing the content of nowhere:
	follow the property-aggregation rules for the target.

The property-aggregation rules are an object-based rulebook.
The property-aggregation rulebook has a list of text called the tagline.

[At the moment, we only support "open/unlocked", "closed/unlocked" and "closed/locked" for doors and containers.]
[A first property-aggregation rule for an openable open thing (this is the mention open openables rule):
	add "open" to the tagline.

A property-aggregation rule for an openable closed thing (this is the mention closed openables rule):
	add "closed" to the tagline.

A property-aggregation rule for an lockable unlocked thing (this is the mention unlocked lockable rule):
	add "unlocked" to the tagline.

A property-aggregation rule for an lockable locked thing (this is the mention locked lockable rule):
	add "locked" to the tagline.]

A first property-aggregation rule for an openable lockable open unlocked thing (this is the mention open openables rule):
	add "open" to the tagline.

A property-aggregation rule for an openable lockable closed unlocked thing (this is the mention closed openables rule):
	add "closed" to the tagline.

A property-aggregation rule for an openable lockable closed locked thing (this is the mention locked openables rule):
	add "locked" to the tagline.

A property-aggregation rule for a lockable thing (called the lockable thing) (this is the mention matching key of lockable rule):
	let X be the matching key of the lockable thing;
	if X is not nothing:
		add "match [X]" to the tagline.

A property-aggregation rule for an edible off-stage thing (this is the mention eaten edible rule):
	add "eaten" to the tagline.

The last property-aggregation rule (this is the print aggregated properties rule):
	if the number of entries in the tagline is greater than 0:
		say " ([tagline])";
		rule succeeds;
	rule fails;

The objective part 0 is some text that varies. The objective part 0 is "You are hungry! Let's cook a delicious meal. Check the cookbook in the kitchen for the recipe. Once done, enjoy your meal!".

An objective is some text that varies. The objective is "[objective part 0]".
Printing the objective is an action applying to nothing.
Carry out printing the objective:
	say "[objective]".

Understand "goal" as printing the objective.

The taking action has an object called previous locale (matched as "from").

Setting action variables for taking:
	now previous locale is the holder of the noun.

Report taking something from the location:
	say "You pick up [the noun] from the ground." instead.

Report taking something:
	say "You take [the noun] from [the previous locale]." instead.

Report dropping something:
	say "You drop [the noun] on the ground." instead.

The print state option is a truth state that varies.
The print state option is usually false.

Turning on the print state option is an action applying to nothing.
Carry out turning on the print state option:
	Now the print state option is true.

Turning off the print state option is an action applying to nothing.
Carry out turning off the print state option:
	Now the print state option is false.

Printing the state is an activity.
Rule for printing the state:
	let R be the location of the player;
	say "Room: [line break] [the internal name of R][line break]";
	[say "[line break]";
	carry out the printing the content of the room activity;]
	say "[line break]";
	carry out the printing the content of the world activity;
	say "[line break]";
	carry out the printing the content of the inventory activity;
	say "[line break]";
	carry out the printing the content of nowhere activity;
	say "[line break]".

Printing the entire state is an action applying to nothing.
Carry out printing the entire state:
	say "-=STATE START=-[line break]";
	carry out the printing the state activity;
	say "[line break]Score:[line break] [score]/[maximum score][line break]";
	say "[line break]Objective:[line break] [objective][line break]";
	say "[line break]Inventory description:[line break]";
	say "  You are carrying: [a list of things carried by the player].[line break]";
	say "[line break]Room description:[line break]";
	try looking;
	say "[line break]-=STATE STOP=-";

Every turn:
	if extra description command option is true:
		say "<description>";
		try looking;
		say "</description>";
	if extra inventory command option is true:
		say "<inventory>";
		try taking inventory;
		say "</inventory>";
	if extra score command option is true:
		say "<score>[line break][score][line break]</score>";
	if extra score command option is true:
		say "<moves>[line break][turn count][line break]</moves>";
	if print state option is true:
		try printing the entire state;

When play ends:
	if print state option is true:
		try printing the entire state;

After looking:
	carry out the printing the things on the floor activity.

Understand "print_state" as printing the entire state.
Understand "enable print state option" as turning on the print state option.
Understand "disable print state option" as turning off the print state option.

Before going through a closed door (called the blocking door):
	say "You have to open the [blocking door] first.";
	stop.

Before opening a locked door (called the locked door):
	let X be the matching key of the locked door;
	if X is nothing:
		say "The [locked door] is welded shut.";
	otherwise:
		say "You have to unlock the [locked door] with the [X] first.";
	stop.

Before opening a locked container (called the locked container):
	let X be the matching key of the locked container;
	if X is nothing:
		say "The [locked container] is welded shut.";
	otherwise:
		say "You have to unlock the [locked container] with the [X] first.";
	stop.

Displaying help message is an action applying to nothing.
Carry out displaying help message:
	say "[fixed letter spacing]Available commands:[line break]";
	say "  look:                describe the current room[line break]";
	say "  goal:                print the goal of this game[line break]";
	say "  inventory:           print player's inventory[line break]";
	say "  go <dir>:            move the player north, east, south or west[line break]";
	say "  examine ...:         examine something more closely[line break]";
	say "  eat ...:             eat edible food[line break]";
	say "  open ...:            open a door or a container[line break]";
	say "  close ...:           close a door or a container[line break]";
	say "  drop ...:            drop an object on the floor[line break]";
	say "  take ...:            take an object that is on the floor[line break]";
	say "  put ... on ...:      place an object on a supporter[line break]";
	say "  take ... from ...:   take an object from a container or a supporter[line break]";
	say "  insert ... into ...: place an object into a container[line break]";
	say "  lock ... with ...:   lock a door or a container with a key[line break]";
	say "  unlock ... with ...: unlock a door or a container with a key[line break]";

Understand "help" as displaying help message.

Taking all is an action applying to nothing.
Check taking all:
	say "You have to be more specific!";
	rule fails.

Understand "take all" as taking all.
Understand "get all" as taking all.
Understand "pick up all" as taking all.

Understand "take each" as taking all.
Understand "get each" as taking all.
Understand "pick up each" as taking all.

Understand "take everything" as taking all.
Understand "get everything" as taking all.
Understand "pick up everything" as taking all.

The extra description command option is a truth state that varies.
The extra description command option is usually false.

Turning on the extra description command option is an action applying to nothing.
Carry out turning on the extra description command option:
	Decrease turn count by 1;  [Internal framework commands shouldn't count as a turn.]
	Now the extra description command option is true.

Understand "tw-extra-infos description" as turning on the extra description command option.

The extra inventory command option is a truth state that varies.
The extra inventory command option is usually false.

Turning on the extra inventory command option is an action applying to nothing.
Carry out turning on the extra inventory command option:
	Decrease turn count by 1;  [Internal framework commands shouldn't count as a turn.]
	Now the extra inventory command option is true.

Understand "tw-extra-infos inventory" as turning on the extra inventory command option.

The extra score command option is a truth state that varies.
The extra score command option is usually false.

Turning on the extra score command option is an action applying to nothing.
Carry out turning on the extra score command option:
	Decrease turn count by 1;  [Internal framework commands shouldn't count as a turn.]
	Now the extra score command option is true.

Understand "tw-extra-infos score" as turning on the extra score command option.

The extra moves command option is a truth state that varies.
The extra moves command option is usually false.

Turning on the extra moves command option is an action applying to nothing.
Carry out turning on the extra moves command option:
	Decrease turn count by 1;  [Internal framework commands shouldn't count as a turn.]
	Now the extra moves command option is true.

Understand "tw-extra-infos moves" as turning on the extra moves command option.

To trace the actions:
	(- trace_actions = 1; -).

Tracing the actions is an action applying to nothing.
Carry out tracing the actions:
	Decrease turn count by 1;  [Internal framework commands shouldn't count as a turn.]
	trace the actions;

Understand "tw-trace-actions" as tracing the actions.

The restrict commands option is a truth state that varies.
The restrict commands option is usually false.

Turning on the restrict commands option is an action applying to nothing.
Carry out turning on the restrict commands option:
	Decrease turn count by 1;  [Internal framework commands shouldn't count as a turn.]
	Now the restrict commands option is true.

Understand "restrict commands" as turning on the restrict commands option.

The taking allowed flag is a truth state that varies.
The taking allowed flag is usually false.

Before removing something from something:
	now the taking allowed flag is true.

After removing something from something:
	now the taking allowed flag is false.

Before taking a thing (called the object) when the object is on a supporter (called the supporter):
	if the restrict commands option is true and taking allowed flag is false:
		say "Can't see any [object] on the floor! Try taking the [object] from the [supporter] instead.";
		rule fails.

Before of taking a thing (called the object) when the object is in a container (called the container):
	if the restrict commands option is true and taking allowed flag is false:
		say "Can't see any [object] on the floor! Try taking the [object] from the [container] instead.";
		rule fails.

Understand "take [something]" as removing it from.

Rule for supplying a missing second noun while removing:
	if restrict commands option is false and noun is on a supporter (called the supporter):
		now the second noun is the supporter;
	else if restrict commands option is false and noun is in a container (called the container):
		now the second noun is the container;
	else:
		try taking the noun;
		say ""; [Needed to avoid printing a default message.]

The version number is always 1.

Reporting the version number is an action applying to nothing.
Carry out reporting the version number:
	Decrease turn count by 1;  [Internal framework commands shouldn't count as a turn.]
	say "[version number]".

Understand "tw-print version" as reporting the version number.

Reporting max score is an action applying to nothing.
Carry out reporting max score:
	Decrease turn count by 1;  [Internal framework commands shouldn't count as a turn.]
	if maximum score is -32768:
		say "infinity";
	else:
		say "[maximum score]".

Understand "tw-print max_score" as reporting max score.

To print id of (something - thing):
	(- print {something}, "^"; -).

Printing the id of player is an action applying to nothing.
Carry out printing the id of player:
	Decrease turn count by 1;  [Internal framework commands shouldn't count as a turn.]
	print id of player.

Printing the id of EndOfObject is an action applying to nothing.
Carry out printing the id of EndOfObject:
	Decrease turn count by 1;  [Internal framework commands shouldn't count as a turn.]
	print id of EndOfObject.

Understand "tw-print player id" as printing the id of player.
Understand "tw-print EndOfObject id" as printing the id of EndOfObject.

There is a EndOfObject.

