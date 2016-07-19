import random
import pygame
from pygame.locals import *

class Ship(pygame.sprite.Sprite):
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)
    
  def update(self):
    pass

class Bullet(pygame.sprite.Sprite):
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)
    
  def update(self):
    pass

class Asteroid(pygame.sprite.Sprite):
  def __init__(self, x, y, width, height):
    pygame.sprite.Sprite.__init__(self)
    
    # Set up the image.
    image = pygame.Surface((width, height))
    rect = image.get_rect()
    pygame.draw.rect(image, (255, 255, 255), rect.inflate(-2, -2), 1)
    image = image.convert()
    
    self.image = image
    self.rect = self.image.get_rect(x=x, y=y)
    
    self.original = self.image
    
    # Used for determining if the asteroid is off the screen.
    screen = pygame.display.get_surface()
    self.screen_rect = screen.get_rect()
    
    # Set up the velocity. I do it like this in order to avoid the possibility
    # of a zero velocity along any axis.
    velocities = list(range(1, 3)) + list(range(-3, -1))
    self.vx = random.choice(velocities)
    self.vy = random.choice(velocities)
    
    # Set up the angle and angular velocity (spin).
    self.angle = random.random() * 360
    self.spin = random.random() * 5
    
  def update(self):
    # Handle rotation.
    center = self.rect.center
    self.image = pygame.transform.rotate(self.original, self.angle)
    self.rect = self.image.get_rect(center=center)
    
    self.angle += self.spin
    if self.angle > 360:
      self.angle -= 360
    
    # Handle linear movement.
    self.rect.move_ip(self.vx, self.vy)
    
    # Check if asteroid went off horizontal screen margins.
    if self.rect.bottom < self.screen_rect.top:
      #self.rect.move_ip(0, self.screen_rect.height)
      self.rect.top = self.screen_rect.bottom
    elif self.rect.top > self.screen_rect.bottom:
      #self.rect.move_ip(0, -self.screen_rect.height)
      self.rect.bottom = self.screen_rect.top
    
    # Check if asteroid went off vertical screen margins.
    if self.rect.right < self.screen_rect.left:
      #self.rect.move_ip(self.screen_rect.width, 0)
      self.rect.left = self.screen_rect.right
    elif self.rect.left > self.screen_rect.right:
      #self.rect.move_ip(-self.screen_rect.width, 0)
      self.rect.right = self.screen_rect.left

    def explode():
      pass

def add_asteroid(sprites, screen):
  # Set up the asteroid dimensions.
  width = height = random.randint(10, 30)
  
  # Set up the asteroid's initial position (just off the screen).
  screen_rect = screen.get_rect()
  side = random.randint(0, 3)
  if side == 0:   # Left side.
    x = -width
    y = random.randint(0, screen_rect.height)
  elif side == 1: # Bottom side.
    x = random.randint(0, screen_rect.width)
    y = screen_rect.height
  elif side == 2: # Right side.
    x = screen_rect.width
    y = random.randint(0, screen_rect.height)
  elif side == 3: # Top side.
    x = random.randint(0, screen_rect.width)
    y = -height
  
  # Create the new asteroid and add it to the sprite set.
  ast = Asteroid(x, y, width, height)
  sprites.add(ast)
  
def main():
  pygame.init()
  
  # Initialize the display surface.
  screen = pygame.display.set_mode((600, 480))
  pygame.display.set_caption('Asteroids')
  
  clock = pygame.time.Clock()
  sprites = pygame.sprite.RenderPlain()
  count = 0
  
  while True:
    clock.tick(60)
    
    # Process event queue.
    for event in pygame.event.get():
      if event.type == QUIT:
        return
    
    # Add a new asteroid every few frames.
    count += 1
    if count == 60*5:
      add_asteroid(sprites, screen)
      count = 0
    
    sprites.update()
    
    screen.fill((0, 0, 0))
    sprites.draw(screen)
    pygame.display.flip()
    
if __name__ == '__main__':
  main()
