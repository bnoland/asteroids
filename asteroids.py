import math
import random
import pygame
from pygame.locals import *

class Ship(pygame.sprite.Sprite):
  def __init__(self, centerx, centery):
    pygame.sprite.Sprite.__init__(self)
    
    # Set up the image.
    image = pygame.Surface((30, 30))
    triangle = ((0, 29), (14, 0), (29, 29))
    pygame.draw.lines(image, (255, 255, 255), True, triangle, 1)
    image = image.convert()
    
    self.image = image
    self.rect = self.image.get_rect(centerx=centerx, centery=centery)
    
    self.original = self.image
    
    # Used for determining if the ship is off the screen.
    screen = pygame.display.get_surface()
    self.screen_rect = screen.get_rect()
    
    # Used to provide smooth movement.
    self.x = self.rect.x
    self.y = self.rect.y
    
    self.vx = self.vy = 0
    self.ax = self.ay = 0
    
    self.angle = 0
    self.spin = 0
    
  def start_turning_left(self):
    self.spin = 5
    
  def start_turning_right(self):
    self.spin = -5
  
  def stop_turning(self):
    self.spin = 0
  
  def start_accelerating(self):
    radians = math.radians(self.angle)
    magnitude = 0.4
    self.ax = magnitude * -math.sin(radians)
    self.ay = magnitude * -math.cos(radians)
  
  def stop_accelerating(self):
    self.ax = self.ay = 0
  
  def update(self):
    # Handle turning.
    if self.spin != 0:
      self.angle += self.spin
      if self.angle >= 360:
        self.angle -= 360
      
      center = self.rect.center
      self.image = pygame.transform.rotate(self.original, self.angle)
      self.rect = self.image.get_rect(center=center)
      
      self.x = self.rect.x
      self.y = self.rect.y
    
    # Handle linear movement.
    
    self.vx += self.ax
    self.vy += self.ay
    
    # Drag force.
    magnitude = 0.005
    self.vx -= magnitude * self.vx
    self.vy -= magnitude * self.vy
    
    self.x += self.vx
    self.y += self.vy
    self.rect.x = self.x
    self.rect.y = self.y
    
    # Check if ship went off horizontal screen margins.
    if self.rect.bottom < self.screen_rect.top:
      self.rect.top = self.screen_rect.bottom
      self.x = self.rect.x
      self.y = self.rect.y
    elif self.rect.top > self.screen_rect.bottom:
      self.rect.bottom = self.screen_rect.top
      self.x = self.rect.x
      self.y = self.rect.y
    
    # Check if ship went off vertical screen margins.
    if self.rect.right < self.screen_rect.left:
      self.rect.left = self.screen_rect.right
      self.x = self.rect.x
      self.y = self.rect.y
    elif self.rect.left > self.screen_rect.right:
      self.rect.right = self.screen_rect.left
      self.x = self.rect.x
      self.y = self.rect.y

  def shoot(self):
    centerx = self.rect.centerx
    centery = self.rect.centery
    bullet = Bullet(centerx, centery, self.angle)
    return bullet

class Bullet(pygame.sprite.Sprite):
  def __init__(self, centerx, centery, angle):
    pygame.sprite.Sprite.__init__(self)
    
    # Set up the image.
    image = pygame.Surface((8, 8))
    rect = image.get_rect()
    pygame.draw.rect(image, (255, 255, 255), rect.inflate(-2, -2), 1)
    image = pygame.transform.rotate(image, angle)
    image = image.convert()
    
    self.image = image
    self.rect = image.get_rect(centerx=centerx, centery=centery)
    
    # Used for determining if the bullet is off the screen.
    screen = pygame.display.get_surface()
    self.screen_rect = screen.get_rect()
    
    # Used to provide smooth movement.
    self.x = self.rect.x
    self.y = self.rect.y
    
    # Set up the bullet's velocity.
    radians = math.radians(angle)
    magnitude = 5
    self.vx = magnitude * -math.sin(radians)
    self.vy = magnitude * -math.cos(radians)
    
  def update(self):
    self.x += self.vx
    self.y += self.vy
    self.rect.x = self.x
    self.rect.y = self.y

  def is_offscreen(self):
    return not self.screen_rect.contains(self.rect)

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
    if self.angle >= 360:
      self.angle -= 360
    
    # Handle linear movement.
    self.rect.move_ip(self.vx, self.vy)
    
    # Check if asteroid went off horizontal screen margins.
    if self.rect.bottom < self.screen_rect.top:
      self.rect.top = self.screen_rect.bottom
    elif self.rect.top > self.screen_rect.bottom:
      self.rect.bottom = self.screen_rect.top
    
    # Check if asteroid went off vertical screen margins.
    if self.rect.right < self.screen_rect.left:
      self.rect.left = self.screen_rect.right
    elif self.rect.left > self.screen_rect.right:
      self.rect.right = self.screen_rect.left  
    
  def explode(self):
    width = self.rect.w // 4
    height = self.rect.h // 4
    
    # Don't allow really small asteroids.
    if width < 10 or height < 10:
      return ()
    
    x = self.rect.x
    y = self.rect.y
    
    # Create the component asteroids.
    ast1 = Asteroid(x, y, width, height)
    ast2 = Asteroid(x + width, y, width, height)
    ast3 = Asteroid(x, y + height, width, height)
    ast4 = Asteroid(x + width, y + height, width, height)
    
    return (ast1, ast2, ast3, ast4)

def add_random_asteroid(asteroids, screen):
  # Set up the asteroid dimensions.
  width = height = random.randint(10, 80)
  
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
  asteroids.add(ast)

def remove_offscreen_bullets(bullets):
  offscreen = []
  for bullet in iter(bullets):
    if bullet.is_offscreen():
      offscreen.append(bullet)
  
  bullets.remove(offscreen)
  
def main():
  pygame.init()
  
  # Initialize the display surface.
  screen = pygame.display.set_mode((600, 480))
  pygame.display.set_caption('Asteroids')
  
  clock = pygame.time.Clock()
  
  # Player ship.
  ship = Ship(299, 239)
  
  # Sprite groups.
  # TODO: Handle player ship outside of a sprite group?
  ships = pygame.sprite.RenderPlain((ship))
  bullets = pygame.sprite.RenderPlain()
  asteroids = pygame.sprite.RenderPlain()
  
  count = 0
  while True:
    clock.tick(60)
    
    # Process event queue.
    for event in pygame.event.get():
      if event.type == QUIT:
        return
      elif event.type == KEYDOWN:
        if event.key == K_LEFT:
          ship.start_turning_left()
        elif event.key == K_RIGHT:
          ship.start_turning_right()
        elif event.key == K_UP:
          ship.start_accelerating()
        elif event.key == K_LCTRL or event.key == K_RCTRL:
          if len(ships) > 0:  # Only fire if the ship is still alive.
            bullets.add(ship.shoot())
      elif event.type == KEYUP:
        if event.key == K_LEFT or event.key == K_RIGHT:
          ship.stop_turning()
        elif event.key == K_UP:
          ship.stop_accelerating()
    
    remove_offscreen_bullets(bullets)
    
    # Add a new asteroid every few frames.
    count += 1
    if count == 60*5:
      add_random_asteroid(asteroids, screen)
      count = 0
    
    # Explode the asteroids hit by any bullets.
    dead_asteroids = pygame.sprite.groupcollide(asteroids, bullets, True, True)
    for ast in dead_asteroids:
      asteroids.add(ast.explode())
    
    # If any asteroids hit the ship, explode them and destroy the ship.
    dead_asteroids = pygame.sprite.groupcollide(asteroids, ships, True, True)
    if len(dead_asteroids) > 0:
      ships.remove(ship)
    for ast in dead_asteroids:
      asteroids.add(ast.explode())
    
    ships.update()
    bullets.update()
    asteroids.update()
    
    screen.fill((0, 0, 0))
    
    bullets.draw(screen)  # Want bullets below ship.
    ships.draw(screen)
    asteroids.draw(screen)
    
    pygame.display.flip()
    
if __name__ == '__main__':
  main()
