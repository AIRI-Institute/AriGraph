import textworld
from textworld import GameMaker
from textworld.generator.game import GameOptions, Quest, Event
# Make the generation process reproducible.
from textworld import g_rng  # Global random generator.
g_rng.set_seed(20180916)

# GameMaker object for handcrafting text-based games.
M = GameMaker()

#Level 1
roomA = M.new_room("Room A")
roomB = M.new_room("Room B")
roomC = M.new_room("Room C")
roomD = M.new_room("Room D")
roomE = M.new_room("Room E")


corridor1 = M.connect(roomA.west, roomB.east)
corridor2 = M.connect(roomB.south, roomC.north)
corridor3 = M.connect(roomC.east, roomD.west)
corridor4 = M.connect(roomC.south, roomE.north)


lockerA = M.new(type='c', name='Golden locker')     
M.add_fact("locked", lockerA)  
roomA.add(lockerA)
lockerB = M.new(type='c', name='Blue locker')     
M.add_fact("locked", lockerB)  
roomB.add(lockerB)
lockerC = M.new(type='c', name='Red locker')     
M.add_fact("locked", lockerC)  
roomC.add(lockerC)
lockerD = M.new(type='c', name='Yellow locker')     
M.add_fact("locked", lockerD)  
roomD.add(lockerD)
lockerE = M.new(type='c', name='Grey locker')     
M.add_fact("locked", lockerE)  
roomE.add(lockerE)




task_note = M.new(type="o", name="Task note")
task_note.infos.desc = "Your task is to get a treasure. Treasure is hidden in the golden locker. You need a golden key to unlock it. The key is hidden in one of the other lockers located in the environment. All lockers are locked and require a specific key to unlock. The key 1 you found in room A unlocks grey locker. Other notes you will find will guide you further."
roomA.add(task_note)

key1 = M.new(type="k", name="Key 1")   
M.add_fact("match", key1, lockerE)
roomA.add(key1)

key2 = M.new(type="k", name="Golden key")   
M.add_fact("match", key2, lockerA)
lockerE.add(key2)



M.set_player(roomA)

treasure = M.new(type='o', name="treasure")
lockerA.add(treasure)

quest = Quest(win_events=[
        Event(conditions={M.new_fact("in", treasure, M.inventory)})
    ])

M.quests = [quest]
M.render(interactive=True)
#M.test()
M.compile(path='tw_games/benchmark/navigation1/navigation1.z8')