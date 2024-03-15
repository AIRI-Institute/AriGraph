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


The r_1 and the r_0 and the r_2 and the r_3 are rooms.

Understand "Room B" as r_1.
The internal name of r_1 is "Room B".
The printed name of r_1 is "-= Room B =-".
The Room B part 0 is some text that varies. The Room B part 0 is "You are in a Room B. A standard one. The room seems oddly familiar, as though it were only superficially different from the other rooms in the building.

 You can see a chest.[if c_1 is open and there is something in the c_1] The chest contains [a list of things in the c_1]. Wow, isn't TextWorld just the best?[end if]".
The Room B part 1 is some text that varies. The Room B part 1 is "[if c_1 is open and the c_1 contains nothing] Empty! What kind of nightmare TextWorld is this?[end if]".
The Room B part 2 is some text that varies. The Room B part 2 is " You make out a box.[if c_2 is open and there is something in the c_2] The box contains [a list of things in the c_2].[end if]".
The Room B part 3 is some text that varies. The Room B part 3 is "[if c_2 is open and the c_2 contains nothing] The box is empty, what a horrible day![end if]".
The Room B part 4 is some text that varies. The Room B part 4 is " If you haven't noticed it already, there seems to be something there by the wall, it's a display. You look at the price tag on the display. Sixty dollars?! Where'd they buy this display, some kind of expensive place?[if c_3 is open and there is something in the c_3] The display contains [a list of things in the c_3].[end if]".
The Room B part 5 is some text that varies. The Room B part 5 is "[if c_3 is open and the c_3 contains nothing] Empty! What kind of nightmare TextWorld is this?[end if]".
The Room B part 6 is some text that varies. The Room B part 6 is " You see a shelf. [if there is something on the s_1]On the shelf you make out [a list of things on the s_1].[end if]".
The Room B part 7 is some text that varies. The Room B part 7 is "[if there is nothing on the s_1]But oh no! there's nothing on this piece of trash.[end if]".
The Room B part 8 is some text that varies. The Room B part 8 is "

 There is [if d_1 is open]an open[otherwise]a closed[end if]".
The Room B part 9 is some text that varies. The Room B part 9 is " red door leading south. There is [if d_0 is open]an open[otherwise]a closed[end if]".
The Room B part 10 is some text that varies. The Room B part 10 is " blue door leading west.".
The description of r_1 is "[Room B part 0][Room B part 1][Room B part 2][Room B part 3][Room B part 4][Room B part 5][Room B part 6][Room B part 7][Room B part 8][Room B part 9][Room B part 10]".

west of r_1 and east of r_0 is a door called d_0.
south of r_1 and north of r_2 is a door called d_1.
Understand "Room A" as r_0.
The internal name of r_0 is "Room A".
The printed name of r_0 is "-= Room A =-".
The Room A part 0 is some text that varies. The Room A part 0 is "You find yourself in a Room A. A normal one.

 You make out a Microsoft style locker.[if c_4 is open and there is something in the c_4] The Microsoft style locker contains [a list of things in the c_4].[end if]".
The Room A part 1 is some text that varies. The Room A part 1 is "[if c_4 is open and the c_4 contains nothing] The Microsoft style locker is empty! What a waste of a day![end if]".
The Room A part 2 is some text that varies. The Room A part 2 is " You can make out a Microsoft box.[if c_5 is open and there is something in the c_5] The Microsoft box contains [a list of things in the c_5]. You look around you, at all the containers and supporters, doors and objects, and you think to yourself. Why? Why Textworld?[end if]".
The Room A part 3 is some text that varies. The Room A part 3 is "[if c_5 is open and the c_5 contains nothing] What a letdown! The Microsoft box is empty![end if]".
The Room A part 4 is some text that varies. The Room A part 4 is " You smell an intriguing smell, and follow it to a locker.[if c_6 is open and there is something in the c_6] The locker contains [a list of things in the c_6].[end if]".
The Room A part 5 is some text that varies. The Room A part 5 is "[if c_6 is open and the c_6 contains nothing] The locker is empty! What a waste of a day![end if]".
The Room A part 6 is some text that varies. The Room A part 6 is " Hey, want to see a table? Look over there, a table. The table is standard.[if there is something on the s_0] On the table you make out [a list of things on the s_0].[end if]".
The Room A part 7 is some text that varies. The Room A part 7 is "[if there is nothing on the s_0] However, the table, like an empty table, has nothing on it. Hm. Oh well[end if]".
The Room A part 8 is some text that varies. The Room A part 8 is " You can make out a stand. What a coincidence, weren't you just thinking about a stand? [if there is something on the s_2]You see [a list of things on the s_2] on the stand.[end if]".
The Room A part 9 is some text that varies. The Room A part 9 is "[if there is nothing on the s_2]But oh no! there's nothing on this piece of trash. Hm. Oh well[end if]".
The Room A part 10 is some text that varies. The Room A part 10 is " Look over there! an armchair. You shudder, but continue examining the armchair. [if there is something on the s_3]You see [a list of things on the s_3] on the armchair.[end if]".
The Room A part 11 is some text that varies. The Room A part 11 is "[if there is nothing on the s_3]But the thing is empty.[end if]".
The Room A part 12 is some text that varies. The Room A part 12 is "

 There is [if d_0 is open]an open[otherwise]a closed[end if]".
The Room A part 13 is some text that varies. The Room A part 13 is " blue door leading east. There is [if d_3 is open]an open[otherwise]a closed[end if]".
The Room A part 14 is some text that varies. The Room A part 14 is " white door leading south.".
The description of r_0 is "[Room A part 0][Room A part 1][Room A part 2][Room A part 3][Room A part 4][Room A part 5][Room A part 6][Room A part 7][Room A part 8][Room A part 9][Room A part 10][Room A part 11][Room A part 12][Room A part 13][Room A part 14]".

south of r_0 and north of r_3 is a door called d_3.
east of r_0 and west of r_1 is a door called d_0.
Understand "Room C" as r_2.
The internal name of r_2 is "Room C".
The printed name of r_2 is "-= Room C =-".
The Room C part 0 is some text that varies. The Room C part 0 is "You find yourself in a Room C. A typical kind of place. The room is well lit.

 You can make out a Microsoft locker.[if c_7 is open and there is something in the c_7] The Microsoft locker contains [a list of things in the c_7].[end if]".
The Room C part 1 is some text that varies. The Room C part 1 is "[if c_7 is open and the c_7 contains nothing] Empty! What kind of nightmare TextWorld is this?[end if]".
The Room C part 2 is some text that varies. The Room C part 2 is " You can see a case. Make a note of this, you might have to put stuff on or in it later on.[if c_8 is open and there is something in the c_8] The case contains [a list of things in the c_8].[end if]".
The Room C part 3 is some text that varies. The Room C part 3 is "[if c_8 is open and the c_8 contains nothing] Empty! What kind of nightmare TextWorld is this?[end if]".
The Room C part 4 is some text that varies. The Room C part 4 is " You make out a saucepan. The saucepan is standard.[if there is something on the s_4] On the saucepan you make out [a list of things on the s_4].[end if]".
The Room C part 5 is some text that varies. The Room C part 5 is "[if there is nothing on the s_4] But the thing hasn't got anything on it. You move on, clearly upset by your TextWorld experience.[end if]".
The Room C part 6 is some text that varies. The Room C part 6 is " Oh wow! Is that what I think it is? It is! It's a platter. Why don't you take a picture of it, it'll last longer! [if there is something on the s_5]You see [a list of things on the s_5] on the platter. Huh, weird.[end if]".
The Room C part 7 is some text that varies. The Room C part 7 is "[if there is nothing on the s_5]However, the platter, like an empty platter, has nothing on it.[end if]".
The Room C part 8 is some text that varies. The Room C part 8 is "

 There is [if d_1 is open]an open[otherwise]a closed[end if]".
The Room C part 9 is some text that varies. The Room C part 9 is " red door leading north. There is [if d_2 is open]an open[otherwise]a closed[end if]".
The Room C part 10 is some text that varies. The Room C part 10 is " green door leading west.".
The description of r_2 is "[Room C part 0][Room C part 1][Room C part 2][Room C part 3][Room C part 4][Room C part 5][Room C part 6][Room C part 7][Room C part 8][Room C part 9][Room C part 10]".

west of r_2 and east of r_3 is a door called d_2.
north of r_2 and south of r_1 is a door called d_1.
Understand "Room D" as r_3.
The internal name of r_3 is "Room D".
The printed name of r_3 is "-= Room D =-".
The Room D part 0 is some text that varies. The Room D part 0 is "Welcome to the Room D. You begin to take stock of what's here.

 You make out a refrigerator.[if c_0 is open and there is something in the c_0] The refrigerator contains [a list of things in the c_0]. You can't wait to tell the folks at home about this![end if]".
The Room D part 1 is some text that varies. The Room D part 1 is "[if c_0 is open and the c_0 contains nothing] The refrigerator is empty! What a waste of a day![end if]".
The Room D part 2 is some text that varies. The Room D part 2 is " [if c_10 is locked]A locked[else if c_10 is open]An open[otherwise]A closed[end if]".
The Room D part 3 is some text that varies. The Room D part 3 is " rectangular safe is close by.[if c_10 is open and there is something in the c_10] The rectangular safe contains [a list of things in the c_10].[end if]".
The Room D part 4 is some text that varies. The Room D part 4 is "[if c_10 is open and the c_10 contains nothing] The rectangular safe is empty! This is the worst thing that could possibly happen, ever![end if]".
The Room D part 5 is some text that varies. The Room D part 5 is " You see [if c_9 is locked]a locked[else if c_9 is open]an opened[otherwise]a closed[end if]".
The Room D part 6 is some text that varies. The Room D part 6 is " type B safe, which looks usual, here.[if c_9 is open and there is something in the c_9] The type B safe contains [a list of things in the c_9].[end if]".
The Room D part 7 is some text that varies. The Room D part 7 is "[if c_9 is open and the c_9 contains nothing] What a letdown! The type B safe is empty![end if]".
The Room D part 8 is some text that varies. The Room D part 8 is "

 There is [if d_2 is open]an open[otherwise]a closed[end if]".
The Room D part 9 is some text that varies. The Room D part 9 is " green door leading east. There is [if d_3 is open]an open[otherwise]a closed[end if]".
The Room D part 10 is some text that varies. The Room D part 10 is " white door leading north.".
The description of r_3 is "[Room D part 0][Room D part 1][Room D part 2][Room D part 3][Room D part 4][Room D part 5][Room D part 6][Room D part 7][Room D part 8][Room D part 9][Room D part 10]".

north of r_3 and south of r_0 is a door called d_3.
east of r_3 and west of r_2 is a door called d_2.

The c_0 and the c_1 and the c_10 and the c_2 and the c_3 and the c_4 and the c_5 and the c_6 and the c_7 and the c_8 and the c_9 are containers.
The c_0 and the c_1 and the c_10 and the c_2 and the c_3 and the c_4 and the c_5 and the c_6 and the c_7 and the c_8 and the c_9 are privately-named.
The d_0 and the d_3 and the d_1 and the d_2 are doors.
The d_0 and the d_3 and the d_1 and the d_2 are privately-named.
The f_3 and the f_2 and the f_4 and the f_1 and the f_0 are foods.
The f_3 and the f_2 and the f_4 and the f_1 and the f_0 are privately-named.
The k_0 and the k_10 and the k_2 and the k_5 and the k_8 and the k_9 and the k_4 and the k_6 and the k_7 are keys.
The k_0 and the k_10 and the k_2 and the k_5 and the k_8 and the k_9 and the k_4 and the k_6 and the k_7 are privately-named.
The o_4 and the o_1 and the o_2 and the o_3 and the o_0 are object-likes.
The o_4 and the o_1 and the o_2 and the o_3 and the o_0 are privately-named.
The r_1 and the r_0 and the r_2 and the r_3 are rooms.
The r_1 and the r_0 and the r_2 and the r_3 are privately-named.
The s_0 and the s_1 and the s_2 and the s_3 and the s_4 and the s_5 are supporters.
The s_0 and the s_1 and the s_2 and the s_3 and the s_4 and the s_5 are privately-named.

The description of d_0 is "it's a durable blue door [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of d_0 is "blue door".
Understand "blue door" as d_0.
Understand "blue" as d_0.
Understand "door" as d_0.
The d_0 is open.
The description of d_3 is "it's a well-built white door [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of d_3 is "white door".
Understand "white door" as d_3.
Understand "white" as d_3.
Understand "door" as d_3.
The d_3 is open.
The description of d_1 is "The red door looks rugged. [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of d_1 is "red door".
Understand "red door" as d_1.
Understand "red" as d_1.
Understand "door" as d_1.
The d_1 is open.
The description of d_2 is "The green door looks rugged. [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of d_2 is "green door".
Understand "green door" as d_2.
Understand "green" as d_2.
Understand "door" as d_2.
The d_2 is open.
The description of c_0 is "The refrigerator looks strong, and impossible to break. [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of c_0 is "refrigerator".
Understand "refrigerator" as c_0.
The c_0 is in r_3.
The c_0 is closed.
The description of c_1 is "The Microsoft limited edition box looks strong, and impossible to destroy. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_1 is "Microsoft limited edition box".
Understand "Microsoft limited edition box" as c_1.
Understand "Microsoft" as c_1.
Understand "limited" as c_1.
Understand "edition" as c_1.
Understand "box" as c_1.
The c_1 is in r_1.
The c_1 is closed.
The description of c_10 is "The fudge scented chest looks strong, and impossible to break. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_10 is "fudge scented chest".
Understand "fudge scented chest" as c_10.
Understand "fudge" as c_10.
Understand "scented" as c_10.
Understand "chest" as c_10.
The c_10 is in r_3.
The c_10 is locked.
The description of c_2 is "The non-euclidean box looks strong, and impossible to crack. [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of c_2 is "non-euclidean box".
Understand "non-euclidean box" as c_2.
Understand "non-euclidean" as c_2.
Understand "box" as c_2.
The c_2 is in r_1.
The c_2 is closed.
The description of c_3 is "The cabinet looks strong, and impossible to crack. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_3 is "cabinet".
Understand "cabinet" as c_3.
The c_3 is in r_1.
The c_3 is open.
The description of c_4 is "The formless chest looks strong, and impossible to destroy. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_4 is "formless chest".
Understand "formless chest" as c_4.
Understand "formless" as c_4.
Understand "chest" as c_4.
The c_4 is in r_0.
The c_4 is closed.
The description of c_5 is "The Microsoft style locker looks strong, and impossible to crack. [if open]It is open.[else if closed]It is closed.[otherwise]It is locked.[end if]".
The printed name of c_5 is "Microsoft style locker".
Understand "Microsoft style locker" as c_5.
Understand "Microsoft" as c_5.
Understand "style" as c_5.
Understand "locker" as c_5.
The c_5 is in r_0.
The c_5 is locked.
The description of c_6 is "The Microsoft box looks strong, and impossible to crack. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_6 is "Microsoft box".
Understand "Microsoft box" as c_6.
Understand "Microsoft" as c_6.
Understand "box" as c_6.
The c_6 is in r_0.
The c_6 is closed.
The description of c_7 is "The locker looks strong, and impossible to crack. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_7 is "locker".
Understand "locker" as c_7.
The c_7 is in r_2.
The c_7 is closed.
The description of c_8 is "The chest looks strong, and impossible to break. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_8 is "chest".
Understand "chest" as c_8.
The c_8 is in r_2.
The c_8 is locked.
The description of c_9 is "The Microsoft locker looks strong, and impossible to crack. [if open]You can see inside it.[else if closed]You can't see inside it because the lid's in your way.[otherwise]There is a lock on it.[end if]".
The printed name of c_9 is "Microsoft locker".
Understand "Microsoft locker" as c_9.
Understand "Microsoft" as c_9.
Understand "locker" as c_9.
The c_9 is in r_3.
The c_9 is closed.
The description of f_3 is "You couldn't pay me to eat that typical thing.".
The printed name of f_3 is "cookie".
Understand "cookie" as f_3.
The f_3 is in r_1.
The f_3 is edible.
The description of o_4 is "The mop would seem to be to fit in here".
The printed name of o_4 is "mop".
Understand "mop" as o_4.
The o_4 is in r_3.
The description of s_0 is "The table is undependable.".
The printed name of s_0 is "table".
Understand "table" as s_0.
The s_0 is in r_0.
The description of s_1 is "The shelf is wobbly.".
The printed name of s_1 is "shelf".
Understand "shelf" as s_1.
The s_1 is in r_1.
The description of s_2 is "The stand is unstable.".
The printed name of s_2 is "stand".
Understand "stand" as s_2.
The s_2 is in r_0.
The description of s_3 is "The bookshelf is durable.".
The printed name of s_3 is "bookshelf".
Understand "bookshelf" as s_3.
The s_3 is in r_0.
The description of s_4 is "The bowl is wobbly.".
The printed name of s_4 is "bowl".
Understand "bowl" as s_4.
The s_4 is in r_2.
The description of s_5 is "The pan is unstable.".
The printed name of s_5 is "pan".
Understand "pan" as s_5.
The s_5 is in r_2.
The description of f_2 is "The pizza looks tempting.".
The printed name of f_2 is "pizza".
Understand "pizza" as f_2.
The f_2 is edible.
The f_2 is in the c_1.
The description of f_4 is "The gummy bear looks delicious.".
The printed name of f_4 is "gummy bear".
Understand "gummy bear" as f_4.
Understand "gummy" as f_4.
Understand "bear" as f_4.
The f_4 is edible.
The player carries the f_4.
The description of f_1 is "that's an ordinary icecream!".
The printed name of f_1 is "icecream".
Understand "icecream" as f_1.
The f_1 is in the c_0.
The description of k_0 is "The metal of the Microsoft limited edition passkey is hammered.".
The printed name of k_0 is "Microsoft limited edition passkey".
Understand "Microsoft limited edition passkey" as k_0.
Understand "Microsoft" as k_0.
Understand "limited" as k_0.
Understand "edition" as k_0.
Understand "passkey" as k_0.
The player carries the k_0.
The matching key of the c_1 is the k_0.
The description of k_10 is "The metal of the fudge scented key is polished.".
The printed name of k_10 is "fudge scented key".
Understand "fudge scented key" as k_10.
Understand "fudge" as k_10.
Understand "scented" as k_10.
Understand "key" as k_10.
The k_10 is in the c_0.
The matching key of the c_10 is the k_10.
The description of k_2 is "The metal of the non-euclidean passkey is antiqued.".
The printed name of k_2 is "non-euclidean passkey".
Understand "non-euclidean passkey" as k_2.
Understand "non-euclidean" as k_2.
Understand "passkey" as k_2.
The player carries the k_2.
The matching key of the c_2 is the k_2.
The description of k_5 is "The Microsoft style keycard is cold to the touch".
The printed name of k_5 is "Microsoft style keycard".
Understand "Microsoft style keycard" as k_5.
Understand "Microsoft" as k_5.
Understand "style" as k_5.
Understand "keycard" as k_5.
The k_5 is in the c_4.
The matching key of the c_5 is the k_5.
The description of k_8 is "The passkey looks useful".
The printed name of k_8 is "passkey".
Understand "passkey" as k_8.
The player carries the k_8.
The matching key of the c_0 is the k_8.
The description of k_9 is "The metal of the Microsoft key is rusty.".
The printed name of k_9 is "Microsoft key".
Understand "Microsoft key" as k_9.
Understand "Microsoft" as k_9.
Understand "key" as k_9.
The player carries the k_9.
The matching key of the c_9 is the k_9.
The description of o_1 is "The printer seems well matched to everything else here".
The printed name of o_1 is "printer".
Understand "printer" as o_1.
The o_1 is in the c_1.
The description of o_2 is "The backup calendar is expensive looking.".
The printed name of o_2 is "backup calendar".
Understand "backup calendar" as o_2.
Understand "backup" as o_2.
Understand "calendar" as o_2.
The o_2 is in the c_1.
The description of o_3 is "The bug is clean.".
The printed name of o_3 is "bug".
Understand "bug" as o_3.
The player carries the o_3.
The description of k_4 is "The formless key is cold to the touch".
The printed name of k_4 is "formless key".
Understand "formless key" as k_4.
Understand "formless" as k_4.
Understand "key" as k_4.
The matching key of the c_4 is the k_4.
The k_4 is on the s_2.
The description of k_6 is "The Microsoft latchkey looks useful".
The printed name of k_6 is "Microsoft latchkey".
Understand "Microsoft latchkey" as k_6.
Understand "Microsoft" as k_6.
Understand "latchkey" as k_6.
The matching key of the c_6 is the k_6.
The k_6 is on the s_0.
The description of k_7 is "The keycard looks useful".
The printed name of k_7 is "keycard".
Understand "keycard" as k_7.
The matching key of the c_7 is the k_7.
The k_7 is on the s_4.
The description of f_0 is "You couldn't pay me to eat that normal thing.".
The printed name of f_0 is "apple".
Understand "apple" as f_0.
The f_0 is on the s_0.
The description of o_0 is "The book appears well matched to everything else here".
The printed name of o_0 is "book".
Understand "book" as o_0.
The o_0 is on the s_0.


The player is in r_0.

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

