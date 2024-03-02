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

corridor1 = M.connect(roomA.east, roomB.west)
corridor2 = M.connect(roomB.south, roomC.north)
corridor3 = M.connect(roomC.west, roomD.east)
corridor4 = M.connect(roomD.north, roomA.south)


M.generate_distractors(20)
M.set_player(roomA)

M.render(interactive=True)

M.test()
#M.compile(path='benchmark/graph_test_2x2/graph_test_2x2.z8')
