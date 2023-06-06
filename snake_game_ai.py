import pygame, sys, time
import numpy as np

class SnakeGame(object):
  def __init__(self, w:int=780, h:int=510, fps:int=30, step:int=15, init_snake_length:int=3,
               vision_size:int=6, delay:float=.01):
    self.w = w
    self.h = h
    self.fps = fps
    self.step=step
    self.initial_snake_length = init_snake_length
    self.vision_size= vision_size
    self.delay = delay

  def build(self):
    if self.w % self.step != 0 or self.h % self.step != 0:
      print(f'increase/decrease the width by {self.w % self.step} and height by {self.h % self.step}')
      sys.exit()
    
    self.score, self.high_score = 0,0
    self.ranking_text = ' High Score: {}  |  Score: {} '

    self.x_range = np.arange(0, self.w, self.step).tolist()
    self.y_range = np.arange(0, self.h, self.step).tolist()
    self.base_image = np.zeros((len(self.y_range), len(self.x_range)), dtype='float32')

    for n in range(self.vision_size//2):
      self.base_image = np.append(self.base_image, [[-1] * len(self.x_range)], axis=0)
      self.base_image = np.insert(self.base_image, 0, [[-1] * len(self.x_range)], axis=0)

    for n in range(self.vision_size//2):
      self.base_image = np.insert(self.base_image, 0, [-1] * len(self.base_image[:,-1]), axis=1)
      self.base_image = np.append(self.base_image,np.array([[-1] * len(self.base_image[:,-1])]).T, axis=1)

    pygame.init()

    self.screen = pygame.display.set_mode((self.w, self.h))
    pygame.display.set_caption('snake game by @ostadnavid')
    self.fps_controller = pygame.time.Clock()
    self.font = pygame.font.Font('./arial.ttf', round(self.step*1.25) if len(self.x_range) > 50 else round(self.step*.75) if len(self.x_range) < 20 else self.step)
    # black, white, red
    self.colors = ['#030712', '#f8fafc', '#ef4444']
    self.rank_surface = self.font.render(self.ranking_text.format(0, 0), True, self.colors[0], self.colors[1]).convert_alpha()
    self.rank_surface_position = ((self.w - self.rank_surface.get_size()[0])/2, 0)

    # snake starts from center
    self.snake_pos = [self.x_range[len(self.x_range)//2], self.y_range[len(self.y_range)//2]]
    self.snake_body = [(self.snake_pos[0]-(n*self.step), self.snake_pos[1]) for n in range(self.initial_snake_length)]

    self.food_pos = [self.x_range[np.random.randint(0, len(self.x_range) - 1)], self.y_range[np.random.randint(0, len(self.y_range)-1)]]
    self.food_spawn = True

    self.direction = 'RIGHT'
    self.change_to = self.direction

    self.done = False
    self.reward = 0
    self.n_steps = 0
  
  def reset(self, render=False):
    self.snake_pos = [self.x_range[len(self.x_range)//2], self.y_range[len(self.y_range)//2]]
    self.snake_body = [(self.snake_pos[0]-(n*self.step), self.snake_pos[1]) for n in range(self.initial_snake_length)]
    self.food_pos = [self.x_range[np.random.randint(0, len(self.x_range) - 1)], self.y_range[np.random.randint(0, len(self.y_range)-1)]]
    self.food_spawn = True
    self.direction = 'RIGHT'
    self.change_to = self.direction
    self.n_steps = 0

    if self.score > self.high_score:
      self.high_score = self.score
    self.score = 0

    if render:
      red_surface = self.font.render(self.ranking_text.format(self.high_score, self.score), True, self.colors[1], self.colors[2])

      self.screen.blit(red_surface, self.rank_surface_position)
      pygame.display.update()
      time.sleep(self.delay)
    
    # return corrent obs
    return self.get_state()
  
  def get_image(self):
    image = self.base_image.copy()

    for snake_body_cord in self.snake_body:
      image[self.x_range.index(self.x_range[snake_body_cord[1]//self.step])+self.vision_size//2, self.x_range.index(self.x_range[snake_body_cord[0]//self.step])+self.vision_size//2] = 2

    snake_head_x = self.x_range.index(self.x_range[self.snake_pos[0]//self.step]) + self.vision_size//2
    snake_head_y = self.y_range.index(self.x_range[self.snake_pos[1]//self.step]) + self.vision_size//2
    image[snake_head_y, snake_head_x] = 1

    food_x = self.x_range.index(self.x_range[self.food_pos[0]//self.step]) + self.vision_size//2
    food_y = self.x_range.index(self.x_range[self.food_pos[1]//self.step]) + self.vision_size//2

    image[food_y, food_x] = 3

    n = self.vision_size

    for i in range(n//2, image.shape[0] - n//2):
      for j in range(n//2, image.shape[1] - n//2):
        if image[i, j] == 1:
          window = image[i-n//2:i+n//2+1, j-n//2:j+n//2+1]
  
    return window, snake_head_x, snake_head_y, food_x, food_y
  
  def get_state(self):
    vision, snake_head_x, snake_head_y, food_x, food_y = self.get_image()
    snake_length = len(self.snake_body)

    food_head_direction = np.zeros((3,3), dtype='float32')

    if snake_head_y < food_y: # snake is on top of food
      if snake_head_x < food_x: # snake is on left of the food
        food_head_direction[2, 2] = 1 # topleft
      elif snake_head_x > food_x: # right of food
        food_head_direction[2, 0] = 1 # topright
      else:
        food_head_direction[2, 1] = 1 # on the same x position
    elif snake_head_y > food_y:# down of the food
      if snake_head_x < food_x: # snake is on left of the food
        food_head_direction[0, 2] = 1 # topleft
      elif snake_head_x > food_x: # right of food
        food_head_direction[0, 0] = 1 # topright
      else:
        food_head_direction[0, 1] = 1 # on the same x position
    else:
      if snake_head_x < food_x: # snake is on left of the food
        food_head_direction[1, 2] = 1 # topleft
      else: # right of food
        food_head_direction[1, 0] = 1 # topright


    return vision, food_head_direction, snake_length

  def check_food_pos(self):
    return any([(cord[0] == self.food_pos[0] and cord[1] == self.food_pos[1])
                for cord in self.snake_body])

  def play_step(self, action:int, render=False):
    assert action in [0, 1, 2], 'action must be 0(right) 1(left) 2(straight)' # right, left, straight
    self.reward = 0
    self.done = False
    self.n_steps += 1
    self.change_to = action


    if self.change_to == 0 and self.direction == 'LEFT':
      self.direction = 'UP'
    elif self.change_to == 0 and self.direction == 'UP':
      self.direction = 'RIGHT'
    elif self.change_to == 0 and self.direction == 'RIGHT':
      self.direction = 'DOWN'
    elif self.change_to == 0 and self.direction == 'DOWN':
      self.direction = 'LEFT'
    elif self.change_to == 1 and self.direction == 'LEFT':
      self.direction = 'DOWN'
    elif self.change_to == 1 and self.direction == 'DOWN':
      self.direction = 'RIGHT'
    elif self.change_to == 1 and self.direction == 'RIGHT':
      self.direction = 'UP'
    elif self.change_to == 1 and self.direction == 'UP':
      self.direction = 'LEFT'

    # Moving the snake
    if self.direction == 'UP':
      self.snake_pos[1] -= self.step
    if self.direction == 'DOWN':
      self.snake_pos[1] += self.step
    if self.direction == 'LEFT':
      self.snake_pos[0] -= self.step
    if self.direction == 'RIGHT':
      self.snake_pos[0] += self.step
    
    if self.n_steps > (len(self.snake_body)+1)*10:
      self.reward = -10
    
    # Snake body growing mechanism
    self.snake_body.insert(0, list(self.snake_pos))
    if self.snake_pos[0] == self.food_pos[0] and self.snake_pos[1] == self.food_pos[1]:
      self.score += 1
      self.food_spawn = False

      self.reward = 10
    else:
      self.snake_body.pop()
    
    # Spawning food on the screen
    if not self.food_spawn:
      self.food_pos = [self.x_range[np.random.randint(0, len(self.x_range) - 1)], self.y_range[np.random.randint(0, len(self.y_range)-1)]]
      self.food_spawn = True
    
    # GFX
    self.screen.fill(self.colors[0])
  
    while self.check_food_pos():
      self.food_pos = [self.x_range[np.random.randint(0, len(self.x_range) - 1)], self.y_range[np.random.randint(0, len(self.y_range)-1)]]
    # Snake food
    pygame.draw.rect(self.screen, self.colors[2], pygame.Rect(self.food_pos[0], self.food_pos[1], self.step, self.step))

    for pos in self.snake_body:
      # Snake body
      # .draw.rect(play_surface, color, xy-coordinate)
      # xy-coordinate -> .Rect(x, y, size_x, size_y)
      pygame.draw.rect(self.screen, self.colors[1], pygame.Rect(pos[0], pos[1], self.step, self.step))
    
    # Game Over conditions
    # Getting out of bounds
    if self.snake_pos[0] < np.min(self.x_range) or self.snake_pos[0] > np.max(self.x_range):
      self.done = True
      self.reward = -10
      self.reset()
    if self.snake_pos[1] < np.min(self.y_range) or self.snake_pos[1] > np.max(self.y_range):
      self.done = True
      self.reward = -10
      self.reset()

    # Touching the snake body
    for block in self.snake_body[1:]:
      if self.snake_pos[0] == block[0] and self.snake_pos[1] == block[1]:
        self.done = True
        self.reward = -10
        self.reset()
    
    if self.food_pos[1] <= self.step:
      self.rank_surface_position = ((self.w - self.rank_surface.get_size()[0])/2, self.h-self.rank_surface.get_size()[1])
    elif self.food_pos[1] >= np.max(self.y_range)-self.step:
      self.rank_surface_position = ((self.w - self.rank_surface.get_size()[0])/2, 0)
    elif self.snake_pos[1] <= self.step or any([body_y <= self.step 
                                    for body_y in map(lambda cord: cord[1] ,self.snake_body)]):
      self.rank_surface_position = ((self.w - self.rank_surface.get_size()[0])/2, self.h-self.rank_surface.get_size()[1])
    elif self.snake_pos[1] >= np.max(self.y_range)-self.step or any([body_y >= np.max(self.y_range)-self.step
                                    for body_y in map(lambda cord: cord[1] ,self.snake_body)]):
      self.rank_surface_position = ((self.w - self.rank_surface.get_size()[0])/2, 0)
    
    self.rank_surface = self.font.render(self.ranking_text.format(self.high_score, self.score), True, self.colors[0], self.colors[1])
    self.screen.blit(self.rank_surface, self.rank_surface_position)

    if render:
      pygame.display.update()
    self.fps_controller.tick(self.fps)

    return self.get_state(), self.reward, self.done