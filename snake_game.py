import pygame, sys, time
import numpy as np

w, h = 720, 480
fps = 120
step = 30 # this makes the objects bigger
initial_snake_length = 3
vision_size = 5
delay = .1

if w % step != 0 or h % step != 0:
  print(f'increase/decrease the width by {w % step} and height by {h % step}')
  sys.exit()

score, high_score = 0,0
ranking_text = ' High Score: {}  |  Score: {} '

x_range = np.arange(0, w, step).tolist()
y_range = np.arange(0, h, step).tolist()
base_image = np.zeros((len(y_range), len(x_range)))

for n in range(vision_size//2):
  base_image = np.append(base_image, [[-1] * len(x_range)], axis=0)
  base_image = np.insert(base_image, 0, [[-1] * len(x_range)], axis=0)

for n in range(vision_size//2):
  base_image = np.insert(base_image, 0, [-1] * len(base_image[:,-1]), axis=1)
  base_image = np.append(base_image,np.array([[-1] * len(base_image[:,-1])]).T, axis=1)

pygame.init()

screen = pygame.display.set_mode((w, h))
pygame.display.set_caption('snake game by @ostadnavid')
fps_controller = pygame.time.Clock()
font = pygame.font.Font('./arial.ttf', round(step*1.25) if len(x_range) > 50 else round(step*.75) if len(x_range) < 20 else step)
# black, white, red
colors = ['#030712', '#f8fafc', '#ef4444']
rank_surface = font.render(ranking_text.format(0, 0), True, colors[0], colors[1]).convert_alpha()
rank_surface_position = ((w - rank_surface.get_size()[0])/2, 0)

# snake starts from center
snake_pos = [x_range[len(x_range)//2], y_range[len(y_range)//2]]
snake_body = [(snake_pos[0]-(n*step), snake_pos[1]) for n in range(initial_snake_length)]

food_pos = [x_range[np.random.randint(0, len(x_range) - 1)], y_range[np.random.randint(0, len(y_range)-1)]]
food_spawn = True

direction = 'RIGHT'
change_to = direction

def game_over():
  global snake_pos, snake_body, food_pos, food_spawn, direction, change_to, score, high_score
  snake_pos = [x_range[len(x_range)//2], y_range[len(y_range)//2]]
  snake_body = [(snake_pos[0]-(n*step), snake_pos[1]) for n in range(initial_snake_length)]
  food_pos = [x_range[np.random.randint(0, len(x_range) - 1)], y_range[np.random.randint(0, len(y_range)-1)]]
  food_spawn = True
  direction = 'RIGHT'
  change_to = direction

  if score > high_score:
    high_score = score
  score = 0

  red_surface = font.render(ranking_text.format(high_score, score), True, colors[1], colors[2])

  screen.blit(red_surface, rank_surface_position)
  pygame.display.update()
  time.sleep(delay)

def get_image():
  global vision_size
  image = base_image.copy()

  for snake_body_cord in snake_body:
    image[x_range.index(x_range[snake_body_cord[1]//step])+vision_size//2, x_range.index(x_range[snake_body_cord[0]//step])+vision_size//2] = 2

  snake_head_x = x_range.index(x_range[snake_pos[0]//step]) + vision_size//2
  snake_head_y = y_range.index(x_range[snake_pos[1]//step]) + vision_size//2
  image[snake_head_y, snake_head_x] = 1

  food_x = x_range.index(x_range[food_pos[0]//step]) + vision_size//2
  food_y = x_range.index(x_range[food_pos[1]//step]) + vision_size//2

  image[food_y, food_x] = 3

  n = vision_size

  for i in range(n//2, image.shape[0] - n//2):
    for j in range(n//2, image.shape[1] - n//2):
      if image[i, j] == 1:
        window = image[i-n//2:i+n//2+1, j-n//2:j+n//2+1]
  return window, snake_head_x, snake_head_y, food_x, food_y

def get_state():
  vision, snake_head_x, snake_head_y, food_x, food_y = get_image()
  snake_length = len(snake_body) + 1

  return vision, snake_head_x, snake_head_y, food_x, food_y, snake_length

def check_food_pos():
  global snake_body, food_pos

  return any([(cord[0] == food_pos[0] and cord[1] == food_pos[1])
              for cord in snake_body])

while True:
  # image, *_ = get_state()
  # print(image) 
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
      sys.exit()
    elif event.type == pygame.KEYDOWN:
      # W -> Up; S -> Down; A -> Left; D -> Right
      if event.key == pygame.K_UP or event.key == ord('w'):
        change_to = 'UP'
      if event.key == pygame.K_DOWN or event.key == ord('s'):
        change_to = 'DOWN'
      if event.key == pygame.K_LEFT or event.key == ord('a'):
        change_to = 'LEFT'
      if event.key == pygame.K_RIGHT or event.key == ord('d'):
        change_to = 'RIGHT'
      # Esc -> Create event to quit the game
      if event.key == pygame.K_ESCAPE:
        pygame.event.post(pygame.event.Event(pygame.QUIT))
    
  # change_to = np.random.choice(['UP','DOWN','LEFT',"RIGHT"])

  # Making sure the snake cannot move in the opposite direction instantaneously
  if change_to == 'UP' and direction != 'DOWN':
    direction = 'UP'
  if change_to == 'DOWN' and direction != 'UP':
    direction = 'DOWN'
  if change_to == 'LEFT' and direction != 'RIGHT':
    direction = 'LEFT'
  if change_to == 'RIGHT' and direction != 'LEFT':
    direction = 'RIGHT'
  
  # Moving the snake
  if direction == 'UP':
    snake_pos[1] -= step
  if direction == 'DOWN':
    snake_pos[1] += step
  if direction == 'LEFT':
    snake_pos[0] -= step
  if direction == 'RIGHT':
    snake_pos[0] += step

  # Snake body growing mechanism
  snake_body.insert(0, list(snake_pos))
  if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
    score += 1
    food_spawn = False
  else:
    snake_body.pop()
  
  
  # Spawning food on the screen
  if not food_spawn:
    food_pos = [x_range[np.random.randint(0, len(x_range) - 1)], y_range[np.random.randint(0, len(y_range)-1)]]
    food_spawn = True

  # GFX
  screen.fill(colors[0])
  
  while check_food_pos():
    food_pos = [x_range[np.random.randint(0, len(x_range) - 1)], y_range[np.random.randint(0, len(y_range)-1)]]
  # Snake food
  pygame.draw.rect(screen, colors[2], pygame.Rect(food_pos[0], food_pos[1], step, step))

  for pos in snake_body:
    # Snake body
    # .draw.rect(play_surface, color, xy-coordinate)
    # xy-coordinate -> .Rect(x, y, size_x, size_y)
    pygame.draw.rect(screen, colors[1], pygame.Rect(pos[0], pos[1], step, step))

  # Game Over conditions
  # Getting out of bounds
  if snake_pos[0] < np.min(x_range) or snake_pos[0] > np.max(x_range):
    game_over()
    continue
  if snake_pos[1] < np.min(y_range) or snake_pos[1] > np.max(y_range):
    game_over()
    continue
  # Touching the snake body
  for block in snake_body[1:]:
    if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
      game_over()
      continue
  
  if food_pos[1] <= step:
    rank_surface_position = ((w - rank_surface.get_size()[0])/2, h-rank_surface.get_size()[1])
  elif food_pos[1] >= np.max(y_range)-step:
    rank_surface_position = ((w - rank_surface.get_size()[0])/2, 0)
  elif snake_pos[1] <= step or any([body_y <= step 
                                  for body_y in map(lambda cord: cord[1] ,snake_body)]):
    rank_surface_position = ((w - rank_surface.get_size()[0])/2, h-rank_surface.get_size()[1])
  elif snake_pos[1] >= np.max(y_range)-step or any([body_y >= np.max(y_range)-step
                                  for body_y in map(lambda cord: cord[1] ,snake_body)]):
    rank_surface_position = ((w - rank_surface.get_size()[0])/2, 0)
  rank_surface = font.render(ranking_text.format(high_score, score), True, colors[0], colors[1])
  screen.blit(rank_surface, rank_surface_position)

  pygame.display.update()
  fps_controller.tick(fps)