""" asteroids.py

A simple Asteroids-type game, made using pygame. """

import sys
import math
import random
import pygame
from pygame.locals import *
from pgu import gui

# Some useful color constants.
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

class Ship(pygame.sprite.Sprite):
    """ Represents the player ship. """
    
    def __init__(self, centerx, centery):
        """ Constructor. """
        
        pygame.sprite.Sprite.__init__(self)
        
        # Set up the image.
        width = 30
        height = 40
        image = pygame.Surface((width, height))
        triangle = ((0, height - 1), (width // 2 - 1, 0), (width - 1, height - 1))
        pygame.draw.lines(image, WHITE, True, triangle, 1)
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
        """ Start turning the ship left on updates. """
        
        self.spin = 5
        
    def start_turning_right(self):
        """ Start turning the ship right on updates. """
        
        self.spin = -5
    
    def stop_turning(self):
        """ Stop turning the ship on updates. """
        
        self.spin = 0
    
    def start_accelerating(self):
        """ Start accelerating the ship on updates. """
        
        radians = math.radians(self.angle)
        magnitude = 0.4
        self.ax = magnitude * -math.sin(radians)
        self.ay = magnitude * -math.cos(radians)
    
    def stop_accelerating(self):
        """ Stop accelerating the ship on updates. """
        
        self.ax = self.ay = 0
    
    def update(self):
        """ Update the ship's state. """
        
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
        
        if not self.screen_rect.contains(self.rect):
            # Check if ship went off horizontal screen margins.
            if self.rect.bottom < self.screen_rect.top:
                self.rect.top = self.screen_rect.bottom
            elif self.rect.top > self.screen_rect.bottom:
                self.rect.bottom = self.screen_rect.top
            
            # Check if ship went off vertical screen margins.
            if self.rect.right < self.screen_rect.left:
                self.rect.left = self.screen_rect.right
            elif self.rect.left > self.screen_rect.right:
                self.rect.right = self.screen_rect.left
            
            self.x = self.rect.x
            self.y = self.rect.y

    def shoot(self):
        """ Return a bullet fired by the ship. """
        
        bullet = Bullet(self.rect.centerx, self.rect.centery, self.angle)
        return bullet

class Bullet(pygame.sprite.Sprite):
    """ Represents a bullet fired by the player ship. """
    
    def __init__(self, centerx, centery, angle):
        """ Constructor. """
        
        pygame.sprite.Sprite.__init__(self)
        
        # Set up the image.
        image = pygame.Surface((8, 8))
        rect = image.get_rect()
        pygame.draw.rect(image, YELLOW, rect.inflate(-2, -2), 1)
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
        """ Update the bullet's state. """
        
        self.x += self.vx
        self.y += self.vy
        self.rect.x = self.x
        self.rect.y = self.y

    def is_offscreen(self):
        """ Is the bullet offscreen? """
        
        return not self.screen_rect.contains(self.rect)

class Asteroid(pygame.sprite.Sprite):
    """ Represents an asteroid. """
    
    def __init__(self, x, y, width, height):
        """ Constructor. """
        
        pygame.sprite.Sprite.__init__(self)
        
        # Set up the image.
        image = pygame.Surface((width, height))
        rect = image.get_rect()
        pygame.draw.rect(image, WHITE, rect.inflate(-2, -2), 1)
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
        """ Update the asteroid's state. """
        
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
        """ Return the new asteroids that result from this asteroid exploding. """
        
        width = self.rect.w // 4
        height = self.rect.h // 4
        
        # Don't allow really small asteroids.
        min_width = min_height = 10
        if width < min_width or height < min_height:
            return ()
        
        x = self.rect.x
        y = self.rect.y
        
        # Create the component asteroids.
        ast1 = Asteroid(x, y, width, height)
        ast2 = Asteroid(x + width, y, width, height)
        ast3 = Asteroid(x, y + height, width, height)
        ast4 = Asteroid(x + width, y + height, width, height)
        
        return (ast1, ast2, ast3, ast4)

class GameOverScreen(gui.Table):
    """ Represents the game over screen, to be shown when the player ship is killed. """
    
    def __init__(self):
        """ Constructor. """
        
        gui.Table.__init__(self)
        
        self.input = gui.Input()
        self.submit = gui.Button('Submit')
        
        self.tr()
        self.td(self.input)
        self.td(self.submit)

class Game:
    """ Represents a game instance. """
    
    pass

def main():
    if not pygame.font:
        print('Error: pygame font module unavailable.', file=sys.stderr)
        sys.exit(1)
    
    pygame.init()
    
    # Initialize the display surface.
    screen = pygame.display.set_mode((600, 480))
    pygame.display.set_caption('Asteroids')
    
    clock = pygame.time.Clock()
    
    # Put the player ship at the center of the screen.
    screen_rect = screen.get_rect()
    ship = Ship(screen_rect.centerx, screen_rect.centery)
    
    font = pygame.font.Font(None, 36)   # Font for score display.
    score = 0                           # Player score.
    
    # Sprite groups.
    ships = pygame.sprite.RenderPlain((ship))
    bullets = pygame.sprite.RenderPlain()
    asteroids = pygame.sprite.RenderPlain()
    
    # Set up the stuff for managing the game over screen.
    gui_app = gui.App()
    game_over_screen = GameOverScreen()
    gui_app.init(game_over_screen)
    
    def game_over():
        """ Is the game over? """
        
        return len(ships) == 0 and len(bullets) == 0
    
    def add_random_asteroid():
        """ Add a randomly generated asteroid to the arena. The asteroid will enter from the edge of
        the screen. """
        
        screen = pygame.display.get_surface()
        screen_rect = screen.get_rect()
        
        # Set up the asteroid dimensions.
        width = height = random.randint(10, 80)
        
        # Set up the asteroid's initial position (just off the screen).
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

    def remove_offscreen_bullets():
        """ Remove any bullets that have drifted offscreen. """
        
        offscreen = []
        for bullet in iter(bullets):
            if bullet.is_offscreen():
                offscreen.append(bullet)
        
        bullets.remove(offscreen)
    
    count = 0
    while True:
        clock.tick(60)
        
        # Process event queue.
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            
            elif game_over():
                gui_app.event(event)
            
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return
                elif event.key == K_LEFT:
                    ship.start_turning_left()
                elif event.key == K_RIGHT:
                    ship.start_turning_right()
                elif event.key == K_UP:
                    ship.start_accelerating()
                elif event.key == K_LCTRL or event.key == K_RCTRL:
                    # Fire a bullet if the ship is still alive.
                    if len(ships) > 0:
                        bullets.add(ship.shoot())
            
            elif event.type == KEYUP:
                if event.key == K_LEFT or event.key == K_RIGHT:
                    ship.stop_turning()
                elif event.key == K_UP:
                    ship.stop_accelerating()
        
        remove_offscreen_bullets()
        
        # If the ship isn't dead, add a new asteroid every few frames.
        if len(ships) > 0:
            count += 1
            if count == 60*5:
                add_random_asteroid()
                count = 0
        
        # Explode the asteroids hit by any bullets and update the player score.
        dead_asteroids = pygame.sprite.groupcollide(asteroids, bullets, True, True)
        
        # Update the score and score display.
        score += len(dead_asteroids)
        score_display = font.render('Score: ' + str(score), True, WHITE)
        
        for ast in dead_asteroids:
            asteroids.add(ast.explode())
        
        # If any asteroids hit the ship, explode them and destroy the ship.
        dead_asteroids = pygame.sprite.groupcollide(asteroids, ships, True, True)
        
        # Any asteroids hitting the ship?
        if len(dead_asteroids) > 0:
            # Kill the ship.
            ships.remove(ship)
            
        for ast in dead_asteroids:
            asteroids.add(ast.explode())
        
        # Update the sprites.
        ships.update()
        bullets.update()
        asteroids.update()
        
        # Redraw the screen.
        
        screen.fill(BLACK)
        
        bullets.draw(screen)    # Want bullets below ship.
        ships.draw(screen)
        asteroids.draw(screen)
        
        # Show the score display.
        screen.blit(score_display, (0, 0))
        
        if len(ships) == 0 and len(bullets) == 0:
            gui_app.paint()
        
        # Display the changes.
        pygame.display.flip()
        
if __name__ == '__main__':
    main()
