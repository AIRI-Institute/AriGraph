Use MAX_STATIC_DATA of 500000.
When play begins, seed the random-number generator with 1234.

container is a kind of thing.
door is a kind of thing.
object-like is a kind of thing.
supporter is a kind of thing.
food is a kind of object-like.
key is a kind of object-like.
containers are openable, lockable and fixed in place. containers are usually closed.
door is openable and lockable.
object-like is portable.
supporters are fixed in place.
food is edible.
A room has a text called internal name.


The r_1 and the r_6 and the r_2 and the r_3 and the r_4 and the r_5 and the r_7 and the r_0 and the r_8 are rooms.

Understand "Kids Room" as r_1.
The internal name of r_1 is "Kids Room".
The printed name of r_1 is "-= Kids Room =-".
The Kids Room part 0 is some text that varies. The Kids Room part 0 is "Well, here we are in a Kids Room. Let's see what's in here.

 You make out [if c_3 is locked]a locked[else if c_3 is open]an opened[otherwise]a closed[end if]".
The Kids Room part 1 is some text that varies. The Kids Room part 1 is " toy storage cabinet nearby.[if c_3 is open and there is something in the c_3] The toy storage cabinet contains [a list of things in the c_3].[end if]".
The Kids Room part 2 is some text that varies. The Kids Room part 2 is "[if c_3 is open and the c_3 contains nothing] The toy storage cabinet is empty! This is the worst thing that could possibly happen, ever![end if]".
The Kids Room part 3 is some text that varies. The Kids Room part 3 is " Were you looking for a study table? Because look over there, it's a study table. [if there is something on the s_10]On the study table you can see [a list of things on the s_10].[end if]".
The Kids Room part 4 is some text that varies. The Kids Room part 4 is "[if there is nothing on the s_10]But the thing hasn't got anything on it. You make a mental note to not get your hopes up the next time you see a study table in a room.[end if]".
The Kids Room part 5 is some text that varies. The Kids Room part 5 is " If you haven't noticed it already, there seems to be something there by the wall, it's a kids bed. The kids bed is normal.[if there is something on the s_9] On the kids bed you can make out [a list of things on the s_9].[end if]".
The Kids Room part 6 is some text that varies. The Kids Room part 6 is "[if there is nothing on the s_9] But oh no! there's nothing on this piece of garbage.[end if]".
The Kids Room part 7 is some text that varies. The Kids Room part 7 is "

There is an exit to the east. Don't worry, it is unguarded. You don't like doors? Why not try going south, that entranceway is unguarded. You don't like doors? Why not try going west, that entranceway is unguarded.".
The description of r_1 is "[Kids Room part 0][Kids Room part 1][Kids Room part 2][Kids Room part 3][Kids Room part 4][Kids Room part 5][Kids Room part 6][Kids Room part 7]".

The r_6 is mapped west of r_1.
The r_2 is mapped south of r_1.
The r_4 is mapped east of r_1.
Understand "Bathroom" as r_6.
The internal name of r_6 is "Bathroom".
The printed name of r_6 is "-= Bathroom =-".
The Bathroom part 0 is some text that varies. The Bathroom part 0 is "You arrive in a Bathroom. A typical one. Let's see what's in here.

 What's that over there? It looks like it's a toilet. The toilet is typical.[if there is something on the s_11] On the toilet you can see [a list of things on the s_11].[end if]".
The Bathroom part 1 is some text that varies. The Bathroom part 1 is "[if there is nothing on the s_11] But there isn't a thing on it.[end if]".
The Bathroom part 2 is some text that varies. The Bathroom part 2 is " You can see a bathroom sink. [if there is something on the s_12]On the bathroom sink you can see [a list of things on the s_12].[end if]".
The Bathroom part 3 is some text that varies. The Bathroom part 3 is "[if there is nothing on the s_12]But the thing is empty.[end if]".
The Bathroom part 4 is some text that varies. The Bathroom part 4 is " What's that over there? It looks like it's a towel rack. The towel rack is typical.[if there is something on the s_13] On the towel rack you can make out [a list of things on the s_13].[end if]".
The Bathroom part 5 is some text that varies. The Bathroom part 5 is "[if there is nothing on the s_13] But oh no! there's nothing on this piece of trash.[end if]".
The Bathroom part 6 is some text that varies. The Bathroom part 6 is "

There is an exit to the east. Don't worry, it is unblocked. There is an unblocked exit to the south.".
The description of r_6 is "[Bathroom part 0][Bathroom part 1][Bathroom part 2][Bathroom part 3][Bathroom part 4][Bathroom part 5][Bathroom part 6]".

The r_3 is mapped south of r_6.
The r_1 is mapped east of r_6.
Understand "Dining Room" as r_2.
The internal name of r_2 is "Dining Room".
The printed name of r_2 is "-= Dining Room =-".
The Dining Room part 0 is some text that varies. The Dining Room part 0 is "You're now in a Dining Room. You try to gain information on your surroundings by using a technique you call 'looking.'

 You can see a dining table. The dining table is typical.[if there is something on the s_6] On the dining table you see [a list of things on the s_6].[end if]".
The Dining Room part 1 is some text that varies. The Dining Room part 1 is "[if there is nothing on the s_6] But the thing is empty. Oh! Why couldn't there just be stuff on it?[end if]".
The Dining Room part 2 is some text that varies. The Dining Room part 2 is "

You need an unblocked exit? You should try going east. There is an exit to the north. Don't worry, it is unguarded. You need an unblocked exit? You should try going south. You don't like doors? Why not try going west, that entranceway is unguarded.".
The description of r_2 is "[Dining Room part 0][Dining Room part 1][Dining Room part 2]".

The r_3 is mapped west of r_2.
The r_7 is mapped south of r_2.
The r_1 is mapped north of r_2.
The r_5 is mapped east of r_2.
Understand "Kitchen" as r_3.
The internal name of r_3 is "Kitchen".
The printed name of r_3 is "-= Kitchen =-".
The Kitchen part 0 is some text that varies. The Kitchen part 0 is "You find yourself in a Kitchen. An ordinary kind of place. You can barely contain your excitement.

 You can make out [if c_0 is locked]a locked[else if c_0 is open]an opened[otherwise]a closed[end if]".
The Kitchen part 1 is some text that varies. The Kitchen part 1 is " dishwasher in the corner.[if c_0 is open and there is something in the c_0] The dishwasher contains [a list of things in the c_0], so there's that.[end if]".
The Kitchen part 2 is some text that varies. The Kitchen part 2 is "[if c_0 is open and the c_0 contains nothing] The dishwasher is empty! This is the worst thing that could possibly happen, ever![end if]".
The Kitchen part 3 is some text that varies. The Kitchen part 3 is " You see a refrigerator. You wonder idly who left that here.[if c_1 is open and there is something in the c_1] The refrigerator contains [a list of things in the c_1].[end if]".
The Kitchen part 4 is some text that varies. The Kitchen part 4 is "[if c_1 is open and the c_1 contains nothing] The refrigerator is empty, what a horrible day![end if]".
The Kitchen part 5 is some text that varies. The Kitchen part 5 is " You scan the room for a cook table, and you find a cook table. [if there is something on the s_3]On the cook table you make out [a list of things on the s_3].[end if]".
The Kitchen part 6 is some text that varies. The Kitchen part 6 is "[if there is nothing on the s_3]But there isn't a thing on it. What, you think everything in TextWorld should have stuff on it?[end if]".
The Kitchen part 7 is some text that varies. The Kitchen part 7 is "

You don't like doors? Why not try going east, that entranceway is unblocked. There is an exit to the north. Don't worry, it is unblocked. You don't like doors? Why not try going south, that entranceway is unguarded.".
The description of r_3 is "[Kitchen part 0][Kitchen part 1][Kitchen part 2][Kitchen part 3][Kitchen part 4][Kitchen part 5][Kitchen part 6][Kitchen part 7]".

The r_0 is mapped south of r_3.
The r_6 is mapped north of r_3.
The r_2 is mapped east of r_3.
Understand "Living Room" as r_4.
The internal name of r_4 is "Living Room".
The printed name of r_4 is "-= Living Room =-".
The Living Room part 0 is some text that varies. The Living Room part 0 is "Well, here we are in a Living Room.

 You can see a TV table. The TV table is normal.[if there is something on the s_0] On the TV table you can see [a list of things on the s_0].[end if]".
The Living Room part 1 is some text that varies. The Living Room part 1 is "[if there is nothing on the s_0] However, the TV table, like an empty TV table, has nothing on it.[end if]".
The Living Room part 2 is some text that varies. The Living Room part 2 is " You can see a sofa. The sofa is ordinary.[if there is something on the s_1] On the sofa you see [a list of things on the s_1].[end if]".
The Living Room part 3 is some text that varies. The Living Room part 3 is "[if there is nothing on the s_1] The sofa appears to be empty. It would have been so cool if there was stuff on the sofa! oh well.[end if]".
The Living Room part 4 is some text that varies. The Living Room part 4 is " You make out a game consol cabinet. The game consol cabinet is standard.[if there is something on the s_2] On the game consol cabinet you can make out [a list of things on the s_2]. Huh, weird.[end if]".
The Living Room part 5 is some text that varies. The Living Room part 5 is "[if there is nothing on the s_2] But there isn't a thing on it.[end if]".
The Living Room part 6 is some text that varies. The Living Room part 6 is "

You need an unblocked exit? You should try going south. You need an unguarded exit? You should try going west.".
The description of r_4 is "[Living Room part 0][Living Room part 1][Living Room part 2][Living Room part 3][Living Room part 4][Living Room part 5][Living Room part 6]".

The r_1 is mapped west of r_4.
The r_5 is mapped south of r_4.
Understand "Master Bedroom" as r_5.
The internal name of r_5 is "Master Bedroom".
The printed name of r_5 is "-= Master Bedroom =-".
The Master Bedroom part 0 is some text that varies. The Master Bedroom part 0 is "You are in a Master Bedroom. A typical kind of place.

 You can see [if c_2 is locked]a locked[else if c_2 is open]an opened[otherwise]a closed[end if]".
The Master Bedroom part 1 is some text that varies. The Master Bedroom part 1 is " ordinary looking wardrobe in the corner.[if c_2 is open and there is something in the c_2] The wardrobe contains [a list of things in the c_2].[end if]".
The Master Bedroom part 2 is some text that varies. The Master Bedroom part 2 is "[if c_2 is open and the c_2 contains nothing] The wardrobe is empty! What a waste of a day![end if]".
The Master Bedroom part 3 is some text that varies. The Master Bedroom part 3 is " You can see a king size bed. The king size bed is standard.[if there is something on the s_7] On the king size bed you can see [a list of things on the s_7].[end if]".
The Master Bedroom part 4 is some text that varies. The Master Bedroom part 4 is "[if there is nothing on the s_7] Unfortunately, there isn't a thing on it. Aw, here you were, all excited for there to be things on it![end if]".
The Master Bedroom part 5 is some text that varies. The Master Bedroom part 5 is " You can make out a bedside table. Make a note of this, you might have to put stuff on or in it later on. The bedside table is typical.[if there is something on the s_8] On the bedside table you see [a list of things on the s_8]. Huh, weird.[end if]".
The Master Bedroom part 6 is some text that varies. The Master Bedroom part 6 is "[if there is nothing on the s_8] But the thing is empty. Hm. Oh well[end if]".
The Master Bedroom part 7 is some text that varies. The Master Bedroom part 7 is "

There is an exit to the north. Don't worry, it is unguarded. You need an unguarded exit? You should try going south. There is an unblocked exit to the west.".
The description of r_5 is "[Master Bedroom part 0][Master Bedroom part 1][Master Bedroom part 2][Master Bedroom part 3][Master Bedroom part 4][Master Bedroom part 5][Master Bedroom part 6][Master Bedroom part 7]".

The r_2 is mapped west of r_5.
The r_8 is mapped south of r_5.
The r_4 is mapped north of r_5.
Understand "Swimming Pool Area" as r_7.
The internal name of r_7 is "Swimming Pool Area".
The printed name of r_7 is "-= Swimming Pool Area =-".
The Swimming Pool Area part 0 is some text that varies. The Swimming Pool Area part 0 is "You are in a Swimming Pool Area. It seems to be pretty usual here. You start to take note of what's in the room.

 You hear a noise behind you and spin around, but you can't see anything other than a pool equipment rack. [if there is something on the s_16]You see [a list of things on the s_16] on the pool equipment rack.[end if]".
The Swimming Pool Area part 1 is some text that varies. The Swimming Pool Area part 1 is "[if there is nothing on the s_16]But the thing is empty, unfortunately.[end if]".
The Swimming Pool Area part 2 is some text that varies. The Swimming Pool Area part 2 is " You make out a table for pool chemicals. [if there is something on the s_17]On the table for pool chemicals you can make out [a list of things on the s_17].[end if]".
The Swimming Pool Area part 3 is some text that varies. The Swimming Pool Area part 3 is "[if there is nothing on the s_17]But there isn't a thing on it. It would have been so cool if there was stuff on the table for pool chemicals.[end if]".
The Swimming Pool Area part 4 is some text that varies. The Swimming Pool Area part 4 is "

You need an unguarded exit? You should try going east. There is an unguarded exit to the north. There is an exit to the west. Don't worry, it is unblocked.".
The description of r_7 is "[Swimming Pool Area part 0][Swimming Pool Area part 1][Swimming Pool Area part 2][Swimming Pool Area part 3][Swimming Pool Area part 4]".

The r_0 is mapped west of r_7.
The r_2 is mapped north of r_7.
The r_8 is mapped east of r_7.
Understand "Gym" as r_0.
The internal name of r_0 is "Gym".
The printed name of r_0 is "-= Gym =-".
The Gym part 0 is some text that varies. The Gym part 0 is "Guess what, you are in a place we're calling a Gym.

 You see a dumbbell stand. [if there is something on the s_14]You see [a list of things on the s_14] on the dumbbell stand.[end if]".
The Gym part 1 is some text that varies. The Gym part 1 is "[if there is nothing on the s_14]But there isn't a thing on it.[end if]".
The Gym part 2 is some text that varies. The Gym part 2 is " You make out a treadmill. [if there is something on the s_15]On the treadmill you can see [a list of things on the s_15].[end if]".
The Gym part 3 is some text that varies. The Gym part 3 is "[if there is nothing on the s_15]However, the treadmill, like an empty treadmill, has nothing on it.[end if]".
The Gym part 4 is some text that varies. The Gym part 4 is "

You need an unblocked exit? You should try going east. There is an unblocked exit to the north.".
The description of r_0 is "[Gym part 0][Gym part 1][Gym part 2][Gym part 3][Gym part 4]".

The r_3 is mapped north of r_0.
The r_7 is mapped east of r_0.
Understand "Library" as r_8.
The internal name of r_8 is "Library".
The printed name of r_8 is "-= Library =-".
The Library part 0 is some text that varies. The Library part 0 is "You've entered a Library.

 You can see a bookcase. [if there is something on the s_4]On the bookcase you see [a list of things on the s_4].[end if]".
The Library part 1 is some text that varies. The Library part 1 is "[if there is nothing on the s_4]Looks like someone's already been here and taken everything off it, though.[end if]".
The Library part 2 is some text that varies. The Library part 2 is " You make out a reading table. [if there is something on the s_5]On the reading table you make out [a list of things on the s_5].[end if]".
The Library part 3 is some text that varies. The Library part 3 is "[if there is nothing on the s_5]But the thing is empty. Oh! Why couldn't there just be stuff on it?[end if]".
The Library part 4 is some text that varies. The Library part 4 is "

There is an unguarded exit to the north. There is an unblocked exit to the west.".
The description of r_8 is "[Library part 0][Library part 1][Library part 2][Library part 3][Library part 4]".

The r_7 is mapped west of r_8.
The r_5 is mapped north of r_8.

The c_0 and the c_1 and the c_2 and the c_3 are containers.
The c_0 and the c_1 and the c_2 and the c_3 are privately-named.
The f_0 and the f_1 and the f_2 are foods.
The f_0 and the f_1 and the f_2 are privately-named.
The o_15 and the o_16 and the o_21 and the o_22 and the o_25 and the o_11 and the o_9 and the o_0 and the o_1 and the o_10 and the o_12 and the o_13 and the o_14 and the o_17 and the o_18 and the o_19 and the o_2 and the o_20 and the o_23 and the o_24 and the o_26 and the o_27 and the o_28 and the o_29 and the o_3 and the o_4 and the o_5 and the o_6 and the o_7 and the o_8 are object-likes.
The o_15 and the o_16 and the o_21 and the o_22 and the o_25 and the o_11 and the o_9 and the o_0 and the o_1 and the o_10 and the o_12 and the o_13 and the o_14 and the o_17 and the o_18 and the o_19 and the o_2 and the o_20 and the o_23 and the o_24 and the o_26 and the o_27 and the o_28 and the o_29 and the o_3 and the o_4 and the o_5 and the o_6 and the o_7 and the o_8 are privately-named.
The r_1 and the r_6 and the r_2 and the r_3 and the r_4 and the r_5 and the r_7 and the r_0 and the r_8 are rooms.
The r_1 and the r_6 and the r_2 and the r_3 and the r_4 and the r_5 and the r_7 and the r_0 and the r_8 are privately-named.
The s_0 and the s_1 and the s_10 and the s_11 and the s_12 and the s_13 and the s_14 and the s_15 and the s_16 and the s_17 and the s_2 and the s_3 and the s_4 and the s_5 and the s_6 and the s_7 and the s_8 and the s_9 are supporters.
The s_0 and the s_1 and the s_10 and the s_11 and the s_12 and the s_13 and the s_14 and the s_15 and the s_16 and the s_17 and the s_2 and the s_3 and the s_4 and the s_5 and the s_6 and the s_7 and the s_8 and the s_9 are privately-named.

The description of c_0 is "dishwasher".
The printed name of c_0 is "dishwasher".
Understand "dishwasher" as c_0.
The c_0 is in r_3.
The c_0 is closed.
The description of c_1 is "refrigerator".
The printed name of c_1 is "refrigerator".
Understand "refrigerator" as c_1.
The c_1 is in r_3.
The c_1 is closed.
The description of c_2 is "normal wardrobe".
The printed name of c_2 is "wardrobe".
Understand "wardrobe" as c_2.
The c_2 is in r_5.
The c_2 is closed.
The description of c_3 is "toy storage cabinet".
The printed name of c_3 is "toy storage cabinet".
Understand "toy storage cabinet" as c_3.
Understand "toy" as c_3.
Understand "storage" as c_3.
Understand "cabinet" as c_3.
The c_3 is in r_1.
The c_3 is closed.
The description of o_15 is "yoga mat".
The printed name of o_15 is "yoga mat".
Understand "yoga mat" as o_15.
Understand "yoga" as o_15.
Understand "mat" as o_15.
The o_15 is in r_0.
The description of o_16 is "jump rope".
The printed name of o_16 is "jump rope".
Understand "jump rope" as o_16.
Understand "jump" as o_16.
Understand "rope" as o_16.
The o_16 is in r_0.
The description of o_21 is "a tale about elf wizard".
The printed name of o_21 is "fantasy book".
Understand "fantasy book" as o_21.
Understand "fantasy" as o_21.
Understand "book" as o_21.
The o_21 is in r_0.
The description of o_22 is "ornamented dining table runner".
The printed name of o_22 is "elegant table runner".
Understand "elegant table runner" as o_22.
Understand "elegant" as o_22.
Understand "table" as o_22.
Understand "runner" as o_22.
The o_22 is in r_6.
The description of o_25 is "small toy racing car".
The printed name of o_25 is "toy car".
Understand "toy car" as o_25.
Understand "toy" as o_25.
Understand "car" as o_25.
The o_25 is in r_7.
The description of s_0 is "TV table".
The printed name of s_0 is "TV table".
Understand "TV table" as s_0.
Understand "TV" as s_0.
Understand "table" as s_0.
The s_0 is in r_4.
The description of s_1 is "sofa".
The printed name of s_1 is "sofa".
Understand "sofa" as s_1.
The s_1 is in r_4.
The description of s_10 is "study table".
The printed name of s_10 is "study table".
Understand "study table" as s_10.
Understand "study" as s_10.
Understand "table" as s_10.
The s_10 is in r_1.
The description of s_11 is "toilet".
The printed name of s_11 is "toilet".
Understand "toilet" as s_11.
The s_11 is in r_6.
The description of s_12 is "bathroom sink".
The printed name of s_12 is "bathroom sink".
Understand "bathroom sink" as s_12.
Understand "bathroom" as s_12.
Understand "sink" as s_12.
The s_12 is in r_6.
The description of s_13 is "towel rack".
The printed name of s_13 is "towel rack".
Understand "towel rack" as s_13.
Understand "towel" as s_13.
Understand "rack" as s_13.
The s_13 is in r_6.
The description of s_14 is "dumbbell stand".
The printed name of s_14 is "dumbbell stand".
Understand "dumbbell stand" as s_14.
Understand "dumbbell" as s_14.
Understand "stand" as s_14.
The s_14 is in r_0.
The description of s_15 is "treadmill".
The printed name of s_15 is "treadmill".
Understand "treadmill" as s_15.
The s_15 is in r_0.
The description of s_16 is "pool equipment rack".
The printed name of s_16 is "pool equipment rack".
Understand "pool equipment rack" as s_16.
Understand "pool" as s_16.
Understand "equipment" as s_16.
Understand "rack" as s_16.
The s_16 is in r_7.
The description of s_17 is "table for pool chemicals".
The printed name of s_17 is "table for pool chemicals".
Understand "table for pool chemicals" as s_17.
Understand "table" as s_17.
Understand "for" as s_17.
Understand "pool" as s_17.
Understand "chemicals" as s_17.
The s_17 is in r_7.
The description of s_2 is "game consol cabinet".
The printed name of s_2 is "game consol cabinet".
Understand "game consol cabinet" as s_2.
Understand "game" as s_2.
Understand "consol" as s_2.
Understand "cabinet" as s_2.
The s_2 is in r_4.
The description of s_3 is "cook table".
The printed name of s_3 is "cook table".
Understand "cook table" as s_3.
Understand "cook" as s_3.
Understand "table" as s_3.
The s_3 is in r_3.
The description of s_4 is "bookcase".
The printed name of s_4 is "bookcase".
Understand "bookcase" as s_4.
The s_4 is in r_8.
The description of s_5 is "reading glasses".
The printed name of s_5 is "reading table".
Understand "reading table" as s_5.
Understand "reading" as s_5.
Understand "table" as s_5.
The s_5 is in r_8.
The description of s_6 is "dining table".
The printed name of s_6 is "dining table".
Understand "dining table" as s_6.
Understand "dining" as s_6.
Understand "table" as s_6.
The s_6 is in r_2.
The description of s_7 is "king size bed".
The printed name of s_7 is "king size bed".
Understand "king size bed" as s_7.
Understand "king" as s_7.
Understand "size" as s_7.
Understand "bed" as s_7.
The s_7 is in r_5.
The description of s_8 is "normal bedside table".
The printed name of s_8 is "bedside table".
Understand "bedside table" as s_8.
Understand "bedside" as s_8.
Understand "table" as s_8.
The s_8 is in r_5.
The description of s_9 is "kids bed".
The printed name of s_9 is "kids bed".
Understand "kids bed" as s_9.
Understand "kids" as s_9.
Understand "bed" as s_9.
The s_9 is in r_1.
The description of f_0 is "milk".
The printed name of f_0 is "milk".
Understand "milk" as f_0.
The f_0 is in the c_1.
The description of f_1 is "cheese".
The printed name of f_1 is "cheese".
Understand "cheese" as f_1.
The f_1 is in the c_1.
The description of o_11 is "toy sword".
The printed name of o_11 is "toy sword".
Understand "toy sword" as o_11.
Understand "toy" as o_11.
Understand "sword" as o_11.
The o_11 is in the c_3.
The description of o_9 is "beautifull evening dress".
The printed name of o_9 is "evening dress".
Understand "evening dress" as o_9.
Understand "evening" as o_9.
Understand "dress" as o_9.
The o_9 is in the c_2.
The description of f_2 is "peace of raw meat".
The printed name of f_2 is "raw meat".
Understand "raw meat" as f_2.
Understand "raw" as f_2.
Understand "meat" as f_2.
The f_2 is on the s_1.
The description of o_0 is "TV".
The printed name of o_0 is "TV".
Understand "TV" as o_0.
The o_0 is on the s_0.
The description of o_1 is "decorative pillow".
The printed name of o_1 is "decorative pillow".
Understand "decorative pillow" as o_1.
Understand "decorative" as o_1.
Understand "pillow" as o_1.
The o_1 is on the s_1.
The description of o_10 is "school notebooks".
The printed name of o_10 is "school notebooks".
Understand "school notebooks" as o_10.
Understand "school" as o_10.
Understand "notebooks" as o_10.
The o_10 is on the s_10.
The description of o_12 is "felt tip pens".
The printed name of o_12 is "felt tip pens".
Understand "felt tip pens" as o_12.
Understand "felt" as o_12.
Understand "tip" as o_12.
Understand "pens" as o_12.
The o_12 is on the s_10.
The description of o_13 is "deodorant".
The printed name of o_13 is "deodorant".
Understand "deodorant" as o_13.
The o_13 is on the s_12.
The description of o_14 is "toilet paper".
The printed name of o_14 is "toilet paper".
Understand "toilet paper" as o_14.
Understand "toilet" as o_14.
Understand "paper" as o_14.
The o_14 is on the s_11.
The description of o_17 is "swimming goggles".
The printed name of o_17 is "swimming goggles".
Understand "swimming goggles" as o_17.
Understand "swimming" as o_17.
Understand "goggles" as o_17.
The o_17 is on the s_16.
The description of o_18 is "life ring".
The printed name of o_18 is "life ring".
Understand "life ring" as o_18.
Understand "life" as o_18.
Understand "ring" as o_18.
The o_18 is on the s_16.
The description of o_19 is "chlorine".
The printed name of o_19 is "chlorine".
Understand "chlorine" as o_19.
The o_19 is on the s_17.
The description of o_2 is "gaming consol".
The printed name of o_2 is "gaming consol".
Understand "gaming consol" as o_2.
Understand "gaming" as o_2.
Understand "consol" as o_2.
The o_2 is on the s_2.
The description of o_20 is "dirty dining plate".
The printed name of o_20 is "dirty plate".
Understand "dirty plate" as o_20.
Understand "dirty" as o_20.
Understand "plate" as o_20.
The o_20 is on the s_9.
The description of o_23 is "expensive grey business suit".
The printed name of o_23 is "business suit".
Understand "business suit" as o_23.
Understand "business" as o_23.
Understand "suit" as o_23.
The o_23 is on the s_3.
The description of o_24 is "soft light sleeping lamp".
The printed name of o_24 is "sleeping lamp".
Understand "sleeping lamp" as o_24.
Understand "sleeping" as o_24.
Understand "lamp" as o_24.
The o_24 is on the s_11.
The description of o_26 is "ordinary toothbrush".
The printed name of o_26 is "toothbrush".
Understand "toothbrush" as o_26.
The o_26 is on the s_6.
The description of o_27 is "heavy dumbbell".
The printed name of o_27 is "dumbbell".
Understand "dumbbell" as o_27.
The o_27 is on the s_10.
The description of o_28 is "blue swimming fins that are used for swimming".
The printed name of o_28 is "swimming fins".
Understand "swimming fins" as o_28.
Understand "swimming" as o_28.
Understand "fins" as o_28.
The o_28 is on the s_5.
The description of o_29 is "red wet bathroom towel".
The printed name of o_29 is "wet towel".
Understand "wet towel" as o_29.
Understand "wet" as o_29.
Understand "towel" as o_29.
The o_29 is on the s_7.
The description of o_3 is "reading glasses".
The printed name of o_3 is "reading glasses".
Understand "reading glasses" as o_3.
Understand "reading" as o_3.
Understand "glasses" as o_3.
The o_3 is on the s_5.
The description of o_4 is "detective book".
The printed name of o_4 is "detective book".
Understand "detective book" as o_4.
Understand "detective" as o_4.
Understand "book" as o_4.
The o_4 is on the s_4.
The description of o_5 is "centerpiece".
The printed name of o_5 is "centerpiece".
Understand "centerpiece" as o_5.
The o_5 is on the s_6.
The description of o_6 is "candles".
The printed name of o_6 is "candles".
Understand "candles" as o_6.
The o_6 is on the s_6.
The description of o_7 is "salt and papper shakers".
The printed name of o_7 is "salt and papper shakers".
Understand "salt and papper shakers" as o_7.
Understand "salt" as o_7.
Understand "and" as o_7.
Understand "papper" as o_7.
Understand "shakers" as o_7.
The o_7 is on the s_6.
The description of o_8 is "normal alarm clock".
The printed name of o_8 is "alarm clock".
Understand "alarm clock" as o_8.
Understand "alarm" as o_8.
Understand "clock" as o_8.
The o_8 is on the s_8.


The player is in r_2.

Use scoring. The maximum score is 0.
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
	if 1 is 0 [always false]:
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


An objective is some text that varies. The objective is "".
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

