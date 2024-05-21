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



#Level 2
roomF = M.new_room("Room F")
roomG = M.new_room("Room G")
roomH = M.new_room("Room H")

corridor5 = M.connect(roomB.north, roomF.south)
corridor6 = M.connect(roomD.east, roomG.west)
corridor7 = M.connect(roomG.north, roomH.south)

lockerF = M.new(type='c', name='Green locker')     
M.add_fact("locked", lockerF)  
roomF.add(lockerF)
lockerG = M.new(type='c', name='White locker')     
M.add_fact("locked", lockerG)  
roomG.add(lockerG)
lockerH = M.new(type='c', name='Orange locker')     
M.add_fact("locked", lockerH)  
roomH.add(lockerH)



#Level 3
roomI = M.new_room("Room I")
roomJ = M.new_room("Room J")
roomK = M.new_room("Room K")
roomL = M.new_room("Room L")

corridor8 = M.connect(roomH.north, roomI.south)
corridor9 = M.connect(roomI.east, roomJ.west)
corridor10 = M.connect(roomI.west, roomK.east)
corridor11 = M.connect(roomG.south, roomL.north)

lockerI = M.new(type='c', name='Brown locker')     
M.add_fact("locked", lockerI)  
roomI.add(lockerI)
lockerJ = M.new(type='c', name='Cyan locker')     
M.add_fact("locked", lockerJ)  
roomJ.add(lockerJ)
lockerK = M.new(type='c', name='Crimson locker')     
M.add_fact("locked", lockerK)  
roomK.add(lockerK)
lockerL = M.new(type='c', name='Silver locker')     
M.add_fact("locked", lockerL)  
roomL.add(lockerL)

#Level 4
roomM = M.new_room("Room M")
roomN = M.new_room("Room N")
roomO = M.new_room("Room O")
roomP = M.new_room("Room P")

corridor11 = M.connect(roomG.east, roomM.west)
corridor12 = M.connect(roomM.south, roomN.north)
corridor13 = M.connect(roomL.east, roomN.west)
corridor14 = M.connect(roomN.east, roomO.west)
corridor15 = M.connect(roomM.north, roomP.south)

lockerM = M.new(type='c', name='Azure locker')     
M.add_fact("locked", lockerM)  
roomM.add(lockerM)
lockerN = M.new(type='c', name='Emerald locker')     
M.add_fact("locked", lockerN)  
roomN.add(lockerN)
lockerO = M.new(type='c', name='Bronze locker')     
M.add_fact("locked", lockerO)  
roomO.add(lockerO)
lockerP = M.new(type='c', name='Black locker')     
M.add_fact("locked", lockerP)  
roomP.add(lockerP)


task_note = M.new(type="o", name="Task note")
task_note.infos.desc = "Your task is to get a treasure. Treasure is hidden in the golden locker. You need a golden key to unlock it. The key is hidden in one of the other lockers located in the environment. All lockers are locked and require a specific key to unlock. The key 1 you found in room A unlocks bronze locker. Other notes you will find will guide you further."
roomA.add(task_note)

key1 = M.new(type="k", name="Key 1")   
M.add_fact("match", key1, lockerO)
roomA.add(key1)

note2 = M.new(type="o", name="Note 2")
note2.infos.desc = "The key 2 unlocks Red locker."
lockerO.add(note2)

key2 = M.new(type="k", name="Key 2")   
M.add_fact("match", key2, lockerC)
lockerO.add(key2)

note3 = M.new(type="o", name="Note 3")
note3.infos.desc = "The key 3 unlocks Cyan locker."
lockerC.add(note3)

key3 = M.new(type="k", name="Key 3")   
M.add_fact("match", key3, lockerJ)
lockerC.add(key3)

note4 = M.new(type="o", name="Note 4")
note4.infos.desc = "The key 4 unlocks black locker."
lockerJ.add(note4)

key4 = M.new(type="k", name="Key 4")   
M.add_fact("match", key4, lockerP)
lockerJ.add(key4)

key5 = M.new(type="k", name="Golden Key")   
M.add_fact("match", key5, lockerA)
lockerP.add(key5)

M.set_player(roomA)

treasure = M.new(type='o', name="treasure")
lockerA.add(treasure)

quest = Quest(win_events=[
        Event(conditions={M.new_fact("in", treasure, M.inventory)})
    ])

M.quests = [quest]
M.render(interactive=True)
#M.test()
M.compile(path='tw_games/benchmark/navigation4/navigation4.z8')