import textworld
from textworld import GameMaker
from textworld.generator.game import GameOptions, Quest, Event
# Make the generation process reproducible.
from textworld import g_rng  # Global random generator.
g_rng.set_seed(20180916)

# GameMaker object for handcrafting text-based games.
M = GameMaker()


roomA = M.new_room("Room A")
roomB = M.new_room("Room B")
roomC = M.new_room("Room C")
roomD = M.new_room("Room D")
roomE = M.new_room("Room E")
roomF = M.new_room("Room F")
roomG = M.new_room("Room G")
roomH = M.new_room("Room H")
roomJ = M.new_room("Room J")

corridor1 = M.connect(roomA.east, roomB.west)
corridor2 = M.connect(roomB.south, roomC.north)
corridor3 = M.connect(roomC.west, roomD.east)
corridor4 = M.connect(roomD.north, roomA.south)
corridor5 = M.connect(roomB.east, roomE.west)
corridor6 = M.connect(roomE.south, roomF.north)
corridor7 = M.connect(roomC.east, roomF.west)

corridor8 = M.connect(roomD.south, roomG.north)
corridor9 = M.connect(roomG.east, roomH.west)
corridor10 = M.connect(roomH.east, roomJ.west)
corridor11 = M.connect(roomC.south, roomH.north)
corridor12 = M.connect(roomF.south, roomJ.north)


M.generate_distractors(20)
M.set_player(roomA)

M.render(interactive=True)

M.test()
#M.compile(path='benchmark/graph_test_3x3/graph_test_3x3.z8')
