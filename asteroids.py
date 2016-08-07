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
RED = (255, 0, 0)

class Ship(pygame.sprite.Sprite):
    """ Represents the player ship. """
    
    def __init__(self, centerx, centery):
        """ Constructor. """
        
        pygame.sprite.Sprite.__init__(self)
        
        ship_width, ship_height = 30, 40
        flame_width, flame_height = 10, 5
        
        # Set up the non-accelerating ship image.
        
        self.non_accel_image = pygame.Surface((ship_width, ship_height + flame_height))
        ship = ((0, ship_height - 1), (ship_width // 2 - 1, 0), (ship_width - 1, ship_height - 1))
        pygame.draw.lines(self.non_accel_image, WHITE, True, ship, 1)
        self.non_accel_image = self.non_accel_image.convert()
        
        # Set up the accelerating ship image (the non-accelerating image plus a booster flame).
        
        flame = (((ship_width - flame_width) // 2 - 1, ship_height - 1),
                  (ship_width // 2 - 1, ship_height + flame_height - 1),
                  (ship_width - (ship_width - flame_width) // 2 - 1, ship_height - 1))
        
        self.accel_image = pygame.Surface((ship_width, ship_height + flame_height))
        self.accel_image.blit(self.non_accel_image, (0, 0))
        pygame.draw.lines(self.accel_image, RED, False, flame, 1)
        self.accel_image = self.accel_image.convert()
        
        # The ship isn't accelerating to begin with.
        self.image = self.non_accel_image
        self.rect = self.image.get_rect(centerx=centerx, centery=centery)
        
        self.orig_image = self.image
        
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
        
        self.orig_image = self.accel_image
        
    def stop_accelerating(self):
        """ Stop accelerating the ship on updates. """
        
        self.ax = self.ay = 0
        
        self.orig_image = self.non_accel_image
        
    def update(self):
        """ Update the ship's state. """
        
        # Handle turning.
        self.angle += self.spin
        if self.angle >= 360:
            self.angle -= 360
        
        center = self.rect.center
        self.image = pygame.transform.rotate(self.orig_image, self.angle)
        self.rect = self.image.get_rect(center=center)
        
        if self.spin != 0:
            # The ship actually turned, so update its coordinates.
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
        
        self.orig_image = self.image
        
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
        
        self.angle += self.spin
        if self.angle >= 360:
            self.angle -= 360
        
        center = self.rect.center
        self.image = pygame.transform.rotate(self.orig_image, self.angle)
        self.rect = self.image.get_rect(center=center)
        
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
    
    def __init__(self, game):
        """ Constructor. """
        
        gui.Table.__init__(self)
        
        self.game = game
        
        self.input = gui.Input()
        self.submit = gui.Button('Submit')
        
        self.input.connect('activate', self._submit_score)
        self.submit.connect(gui.CLICK, self._submit_score)
        
        self.tr()
        self.td(gui.Label('Name: ', color=WHITE))
        self.td(self.input)
        self.td(self.submit)
        
        self.input.focus()
        
    def _submit_score(self):
        self.game.start_new()
        
        # Ensure that the input box is focused for next time.
        self.input.focus()
    
class Game:
    """ Class to manage game functionality. """
    
    def __init__(self):
        """ Constructor. """
        
        self.screen = pygame.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        
        # Set up font for score display.
        self.font = pygame.font.Font(None, 36)
    
    def start_new(self):
        """ Starts a new game. """
        
        # Put the player ship at the center of the screen.
        self.ship = Ship(self.screen_rect.centerx, self.screen_rect.centery)
        
        # Set up the sprite groups.
        self.ships = pygame.sprite.RenderPlain((self.ship))
        self.bullets = pygame.sprite.RenderPlain()
        self.asteroids = pygame.sprite.RenderPlain()
        
        # Set up player score.
        self.score = 0
        
        # Used to keep track of updates.
        # TODO: Attributes can be added to functions in Python. Should this become an attribute
        # of update()?
        self.update_count = 0
        
    def is_over(self):
        """ Is the game over? """
        
        return len(self.ships) == 0 and len(self.bullets) == 0
    
    def get_score(self):
        """ Returns the current player score. """
        
        return self.score
    
    def _add_random_asteroid(self):
        """ Add a randomly generated asteroid to the screen. The asteroid will enter from the edge
        of the screen. """
        
        # Set up the asteroid dimensions.
        width = height = random.randint(10, 80)
        
        # Set up the asteroid's initial position (just off the screen).
        side = random.randint(0, 3)
        if side == 0:   # Left side.
            x = -width
            y = random.randint(0, self.screen_rect.height)
        elif side == 1: # Bottom side.
            x = random.randint(0, self.screen_rect.width)
            y = self.screen_rect.height
        elif side == 2: # Right side.
            x = self.screen_rect.width
            y = random.randint(0, self.screen_rect.height)
        elif side == 3: # Top side.
            x = random.randint(0, self.screen_rect.width)
            y = -height
        
        # Create the new asteroid and add it to the sprite set.
        ast = Asteroid(x, y, width, height)
        self.asteroids.add(ast)

    def _remove_offscreen_bullets(self):
        """ Remove any bullets that have drifted offscreen. """
        
        offscreen = []
        for bullet in iter(self.bullets):
            if bullet.is_offscreen():
                offscreen.append(bullet)
        
        self.bullets.remove(offscreen)
    
    def event(self, ev):
        """ Process an event. """
        
        if ev.type == KEYDOWN:
            if ev.key == K_LEFT:
                self.ship.start_turning_left()
            elif ev.key == K_RIGHT:
                self.ship.start_turning_right()
            elif ev.key == K_UP:
                self.ship.start_accelerating()
            elif ev.key == K_LCTRL or ev.key == K_RCTRL:
                # Fire a bullet if the ship is still alive.
                if len(self.ships) > 0:
                    self.bullets.add(self.ship.shoot())
        
        elif ev.type == KEYUP:
            if ev.key == K_LEFT or ev.key == K_RIGHT:
                self.ship.stop_turning()
            elif ev.key == K_UP:
                self.ship.stop_accelerating()
    
    def update(self):
        """ Update the game state. """
        
        self._remove_offscreen_bullets()
        
        # If the ship isn't dead, add a new asteroid every few updates.
        if len(self.ships) > 0:
            self.update_count += 1
            if self.update_count == 60*5:
                self._add_random_asteroid()
                self.update_count = 0
        
        # Handle collisions between bullets and asteroids.
        dead_asteroids = pygame.sprite.groupcollide(self.asteroids, self.bullets, True, True)
        
        # Update the score and score display.
        self.score += len(dead_asteroids)
        self.score_display = self.font.render('Score: ' + str(self.score), True, WHITE)
        
        for ast in dead_asteroids:
            self.asteroids.add(ast.explode())
        
        # Handle collisions between asteroids and the ship.
        dead_asteroids = pygame.sprite.groupcollide(self.asteroids, self.ships, True, True)
        
        # Any asteroids hitting the ship?
        if len(dead_asteroids) > 0:
            # Kill the ship.
            self.ships.remove(self.ship)
            
        for ast in dead_asteroids:
            self.asteroids.add(ast.explode())
        
        # Update the sprites.
        self.ships.update()
        self.bullets.update()
        self.asteroids.update()
    
    def draw(self):
        """ Draw the sprites, etc., to the screen. """
        
        # Clear the screen.
        self.screen.fill(BLACK)
        
        # Draw the sprites.
        self.bullets.draw(self.screen)  # Want bullets below ship.
        self.ships.draw(self.screen)
        self.asteroids.draw(self.screen)
        
        # Show the score display.
        self.screen.blit(self.score_display, (0, 0))
    
def main():
    # Give a warning if the pygame font module is unavailable.
    if not pygame.font:
        print('Error: pygame font module unavailable.', file=sys.stderr)
        sys.exit(1)
    
    pygame.init()
    
    # Initialize the display surface.
    screen = pygame.display.set_mode((600, 480))
    pygame.display.set_caption('Asteroids')
    
    clock = pygame.time.Clock()
    
    # Set up a new game.
    game = Game()
    game.start_new()
    
    # Set up the stuff for managing the game over screen.
    gui_app = gui.App()
    game_over_screen = GameOverScreen(game)
    gui_app.init(game_over_screen)
    
    while True:
        clock.tick(60)
        
        # Process the event queue.
        for ev in pygame.event.get():
            if ev.type == QUIT:
                return
            elif ev.type == KEYDOWN and ev.key == K_ESCAPE:
                return
            elif ev.type == KEYDOWN and ev.key == K_F1:
                game.start_new()
            elif game.is_over():
                gui_app.event(ev)
            else:
                game.event(ev)
        
        game.update()
        game.draw()
        
        if game.is_over():
            gui_app.paint()
        
        # Display the changes to the screen.
        pygame.display.flip()
    
if __name__ == '__main__':
    main()
