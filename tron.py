import pygame
# Author: Alex Gomes
# Date: Oct 13/2019
# Notes: Just a quick game, no real graphics, just polygons, supports up to 4 players, min 2 players 

# The dimensions for the window
W = 500
H = 500

# Player objects
# Instantiation takes x, y, coords of where to spawn the player
# It also takes c, the colour of the player
# Also takes in a keymap, which is a dictionary that maps UP, DOWN, LEFT, RIGHT to pygame keys
# Also takes in a name, for the player
# Keeps track of a constant velocity in which the player will move at
# The size of the player is proportional to the velocity, so we don't have gaps in the grid
# Keeps track of whether or not it is alive
# Also keeps track of the name of the player
class Player:
    def __init__(self, x, y, c, keymap, name):
        self.x = x
        self.y = y
        self.c = c
        self.keys = keymap
        self.r = 4
        self.v = self.r
        self.alive = True
        self.traversed = [(self.x, self.y)]
        self.name = name
        self.reset_move()
        
        # determine which way we will start, depending on how far we are from the top, start moving towards the directon
        if y > W//2:
            self.up = True
        else:
            self.down = True

    # gritty function to reset all movement vars
    def reset_move(self):
        self.up = False
        self.down = False
        self.left = False
        self.right = False

    # basic checks for collision with following logic:
    #   check if player's current position is inside coords of our player's traversed path
    #   check if player's current position is inside coords of the grid's traversed paths, the paths from all players
    #   check if player is outside the bounds of the window
    # if any of these fail, then the player is dead
    def check_collision(self, grid_traversed):
        if (self.x, self.y) in self.traversed \
            or (self.x, self.y) in grid_traversed \
            or self.x > W or self.x < 0 \
            or self.y > H or self.y < 0:
            self.alive = False

    # takes in the key list of the states of all keys, and the grid state of all the traversed paths
    # checking if the inputted key corresponds to the player's designated key as per mapping logic
    # before moving, we check if we were not moving in the opposite direction of the input key, because we cannot do a flip, we'd be inside our path
    # reset all the other direciton, then set the direction 
    # depending on the bool that's true, move our player's x or y in the correct direction by the constant velocity
    # perform a collision check for this player
    # add this iteration of movement to our player's traversed path and to the grid's traversed path
    # return the updated grid for future collision checks
    def move(self, key_buffer, grid_traversed):
        if key_buffer[self.keys["UP"]]:
            if not self.down:
                self.reset_move()
                self.up = True

        elif key_buffer[self.keys["DOWN"]]:
            if not self.up:
                self.reset_move()
                self.down = True

        elif key_buffer[self.keys["LEFT"]]:
            if not self.right:
                self.reset_move()
                self.left = True

        elif key_buffer[self.keys["RIGHT"]]:
            if not self.left:
                self.reset_move()
                self.right = True

        if self.up:
            self.y -= self.v
        elif self.down:
            self.y += self.v
        elif self.left: 
            self.x -= self.v
        elif self.right: 
            self.x += self.v

        self.check_collision(grid_traversed)
        self.traversed.append((self.x, self.y))
        grid_traversed.append((self.x, self.y))

        return grid_traversed
        
    # the draw logic for the player, takes in the window context to draw into
    # draws the trail based on the players traversed path
    # draws the head of the player as well on top
    def draw(self, gfx):
        for point in self.traversed:
            pygame.draw.rect(gfx, self.c, (point[0], point[1], self.r, self.r))
        pygame.draw.rect(gfx, (255, 255, 255), (self.x, self.y, self.r, self.r))

    # basic logic of player death makes it so the trail of the player is recoloured as the same colour as the bg
    # this would be a problem if trails overlapped, but they don't, so no worries
    def death(self, gfx, bg):
        for point in self.traversed:
            pygame.draw.rect(gfx, bg, (point[0], point[1], self.r, self.r))

# the game object, responsible for the environment and resource management
# instantiation takes in the width and height of the window
# keeps track of all the resources that are dependant on the environment, in this case just the players, could just keep track of players, this will
#   be useful if we ever decide to have more game objects
# keeps track of the spawned players, eventually used to see which player is left alive
# keeps track of how much of the grid has been traversed
# sets up the clock and other necessary graphics objects
class Game:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.resources = []
        self.bg = (0, 0, 0)
        self.spawned_players = []
        self.traversed = []

        pygame.init()
        self.window = pygame.display.set_mode((w, h))
        pygame.display.set_caption("PyTron")
        self.clock = pygame.time.Clock()

        self.font = pygame.font.Font('freesansbold.ttf', 32) 

    # append game object to resources list, a bit redundent but good practice
    def add(self, obj):
        self.resources.append(obj)

    # create a player if we have room for one, track this player into the players list and add the player's spawn location to the grid traversed
    def spawn_player(self, x, y, c, keymap, name):
        if len(self.spawned_players) < 4:
            self.traversed.append((x, y))
            self.spawned_players.append(name)
            return Player(x, y, c, keymap, name)

    # redraw the background, which will clear everything
    # also draw the borders of the window
    def reset(self):
        self.window.fill((self.bg))
        pygame.draw.rect(self.window, (255, 255, 255), (0, 0, W, H), 2)

    # update the window after all calculations
    # responsible for calling the update and draw for all resources in the game environment
    # starts by resetting the window for a new iteration
    # loops through all the resources, if the resource is a player, and we have more than 1 player alive, draw them, else
    #   call the death function to take them off the board and remove them from the list of players we are tracking
    #  while we have players, draw them, else clear screen, and write the winner's name
    def update(self):
        self.reset()
        for resource in self.resources:
            type = resource.__class__.__name__
            if type == "Player" and len(self.spawned_players) > 1:
                if resource.alive:
                    resource.draw(self.window)
                else:
                    resource.death(self.window, self.bg)
                    self.spawned_players.pop(self.spawned_players.index(resource.name))

        if len(self.spawned_players) > 1:
            pygame.display.update()
        else:
            self.reset()
            text = self.font.render(f'{self.spawned_players[0]} wins!', True, (0, 0, 0), (255, 255, 255)) 
            textRect = text.get_rect()
            textRect.center = (W // 2, H // 2)
            self.window.blit(text, textRect)
            pygame.display.update()

    # main loop for the game environment
    # has an internal running bool, which is always True unless we hit the quit button
    # we loop through all the game resources, if it's a player and they are alive, delegate movement for them by passing the keys state and grid traversed
    # return the state of whether or not the quit button was hit
    def run(self):
        running = True
        self.clock.tick(60)

        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        for resource in self.resources:
            type = resource.__class__.__name__
            if type == "Player":
                if resource.alive:
                    resource.move(keys, self.traversed)

        return running

# MAIN LOGIC AND SETUP

# Creating the game object
game = Game(W, H)

# Possible colours for our 4 players
colors = {
        "red": (255, 64, 64),
        "green": (64, 255, 64),
        "blue": (64, 64, 255),
        "yellow": (255, 255, 128)
    }

# Player keymap with arrow keys
red_player_keys = {
    "UP": pygame.K_UP,
    "LEFT": pygame.K_LEFT,
    "RIGHT": pygame.K_RIGHT,
    "DOWN": pygame.K_DOWN
}

# Player kepmap with WASD keys
blue_player_keys = {
    "UP": pygame.K_w,
    "LEFT": pygame.K_a,
    "RIGHT": pygame.K_d,
    "DOWN": pygame.K_s
}

# spawn the players 
red_player = game.spawn_player(400, 400, colors['red'], red_player_keys, "Player 1")
blue_player = game.spawn_player(100, 100, colors['blue'], blue_player_keys, "Player 2")

# add the players as resources to the game environment
game.add(red_player)
game.add(blue_player)

# run the main loop logic of the game
while game.run():
    game.update()