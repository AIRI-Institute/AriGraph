import textworld.gym
import textworld
import textworld.render
# Register a text-based game as a new environment.


request_infos = textworld.EnvInfos(
    admissible_commands=True,  # All commands relevant to the current state.
    entities=True,              # List of all interactable entities found in the game.
    facts=True,
    inventory=True
)

env_id = textworld.gym.register_game("tw_games/benchmark/navigation1/game.z8", request_infos,
                                     max_episode_steps=50)
#jericho-game-suite/zork1.z5
env = textworld.gym.make(env_id)


obs, infos = env.reset()  # Start new episode.
env.render()

score, moves, done = 0, 0, False
while not done:
    #print("Entities: {}\n".format(infos["entities"]))
    #print("-= Facts =-")
    #print("\n".join(map(str, infos["facts"])))
    print("Admissible commands:\n  {}".format("\n  ".join(infos["admissible_commands"])))
    print('inventory:', infos["inventory"])
    command = input("> ")
    
    obs, score, done, infos = env.step(command)
    env.render()
    moves += 1
    #textworld.render.show_graph(infos["facts"], renderer="browser")
    #print("graph", gpaph_show)
env.close()
print("moves: {}; score: {}".format(moves, score))

