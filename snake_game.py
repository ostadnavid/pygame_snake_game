import pygame, sys, time
import numpy as np

w, h = 720, 420
fps = 10
step = 30 # this makes the objects bigger
initial_snake_length = 3

if w % step != 0 or h % step != 0:
  print(f'increase/decrease the width by {w % step} and height by {h % step}')
  sys.exit()

score, high_score = 0,0
ranking_text = ' High Score : {} | Score : {} '

pygame.init()

screen = pygame.display.set_mode((w, h))
pygame.display.set_caption('snake game by @ostadnavid')
fps_controller = pygame.time.Clock()
font = pygame.font.Font('./JetBrainsMono-Medium.ttf', round(step*.8))
# black, white, red
colors = ['#030712', '#f8fafc', '#ef4444']

rank_surface = font.render(ranking_text.format(0, 0), True, colors[0], colors[1]).convert_alpha()
rank_surface_position = ((w - rank_surface.get_size()[0])/2, 0)

x_range = np.arange(0, w, step).tolist()
y_range = np.arange(0, h, step).tolist()
print(len(x_range), len(y_range))
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
  time.sleep(1)

def check_food_pos():
  global snake_body, food_pos

  return any([(cord[0] == food_pos[0] and cord[1] == food_pos[1])
              for cord in snake_body])

while True:
  # print(np.random.randint(0, len(y_range)-1))
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