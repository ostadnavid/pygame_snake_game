import time
from snake_game_ai import SnakeGame
import random

env = SnakeGame()
env.build()

# env.reset and env.play_step both has a same parameter `render`. 
obs = env.reset(True)

for i in range(100):
    obs, reward, done = env.play_step(random.choice([0, 1, 2]), True)

    print('obs[0]: ')
    print(obs[0])
    print('obs[1]: ')
    print(obs[1])
    print('obs[2]: ')
    print(obs[2])
    print('reward: ', reward)
    print('done: ', done)
    print('__'*9)

    if done:
        obs = env.reset(True)
    time.sleep(.1)