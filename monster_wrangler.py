import pygame, random

pygame.init()

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700

display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Monster Wrangler!")

#set FPS and clock
FPS = 60
clock = pygame.time.Clock()

#define classes
class Game():
    """A class to control game play"""
    def __init__(self, player, monster_group):
        #set game values
        self.score = 0
        #there are rounds, like in boxing
        self.round_number =  0

        #how long player has been playing in an individual round
        self.round_time = 0
        self.frame_count = 0

        #attach player and monster_class
        self.player = player
        self.monster_group = monster_group

        #set sounds and music
        self.next_level_sound = pygame.mixer.Sound("next_level.wav")

        #set font
        self.font = pygame.font.Font("Abrushow.ttf", 24)

        #set images (in HUD) for target monster
        blue_image = pygame.image.load("blue_monster.png")
        green_image = pygame.image.load("green_monster.png")
        purple_image = pygame.image.load("purple_monster.png")
        yellow_image = pygame.image.load("yellow_monster.png")
        #make a list of all images
        #this list corresponds to the monster_type attribute
        #0 -> blue at index 0, 1 -> green at index 1, 2 -> purple at index 2, 3 -> yellow at index 3
        self.target_monster_images = [blue_image, green_image, purple_image, yellow_image]

        #choose a target monster
        self.target_monster_type = random.randint(1,3)
        self.target_monster_image = self.target_monster_images[self.target_monster_type]

        self.target_monster_rect = self.target_monster_image.get_rect()
        self.target_monster_rect.centerx = WINDOW_WIDTH//2
        self.target_monster_rect.top = 30

    def update(self):
        """Update our game object"""
        self.frame_count += 1
        if self.frame_count == FPS:
            self.round_time += 1
            self.frame_count = 0

        #check for collisions
        self.check_collisions()

    def draw(self):
        """Draw the HUD and other to the display"""
        #set colors
        WHITE = (255, 255, 255)
        BLUE = (20, 176, 235)
        GREEN = (87, 201, 47)
        PURPLE = (226, 73, 243)
        YELLOW = (243, 157, 20)

        #add the monster colors to a list where the index of the color matches target_monster_images
        colors = [BLUE, GREEN, PURPLE, YELLOW]

        #set text
        catch_text = self.font.render("Current Catch", True, WHITE)
        catch_rect = catch_text.get_rect()
        catch_rect.centerx = WINDOW_WIDTH//2
        catch_rect.top = 5

        score_text = self.font.render("Score: " + str(self.score), True, WHITE )
        score_rect = score_text.get_rect()
        score_rect.topleft = (5, 5)

        lives_text = self.font.render("Lives " + str(self.player.lives), True, WHITE)
        lives_rect = lives_text.get_rect()
        lives_rect.topleft = (5, 35)

        round_text = self.font.render("Curent Round " + str(self.round_number), True, WHITE)
        round_rect = round_text.get_rect()
        round_rect.topright = (5, 65)

        time_text = self.font.render("Round Time " + str(self.round_time), True, WHITE)
        time_rect = time_text.get_rect()
        time_rect.topright = (WINDOW_WIDTH - 10, 5)

        warp_text = self.font.render("Warps " + str(self.player.warps), True, WHITE)
        warp_rect = warp_text.get_rect()
        warp_rect.topright = (WINDOW_WIDTH - 10, 35)

        #blit the HUD
        display_surface.blit(catch_text, catch_rect)
        display_surface.blit(score_text, score_rect)
        display_surface.blit(lives_text, lives_rect)
        display_surface.blit(round_text, round_rect)
        display_surface.blit(time_text, time_rect)
        display_surface.blit(warp_text, warp_rect)
        #blit monster image
        display_surface.blit(self.target_monster_image, self.target_monster_rect)
        #drae rectangle on the screen whatever target monster color is
        #monster is 64 pixels and so center him within rectangle
        # 2 is for the thickness
        pygame.draw.rect(display_surface, colors[self.target_monster_type], (WINDOW_WIDTH//2 - 32, 30, 64, 64), 2)
        #want to draw same color around entire game area
        pygame.draw.rect(display_surface, colors[self.target_monster_type], (0, 100, WINDOW_WIDTH, WINDOW_HEIGHT - 200), 4)


    def check_collisions(self):
        """Check for collisions between players and monsters"""
        #we need to collide with the right color monster
        #does the type of the monster match up with 0,1,2,or 3
        #check for collisions between player and an individual monster
        #we must check if type of monster matches with type of our target monster
        #checking for collisions between player and monster group
        #spritecollideany() will return the monster collided with
        #the variable collided_monster will either have a monster or be null
        collided_monster = pygame.sprite.spritecollideany(self.player, self.monster_group)
        #we collided with a monster
        if collided_monster:
            #collided with correct monster
            if collided_monster.type == self.target_monster_type:
                #increase score and remove the monster we collided with
                self.score += 100*self.round_number
                collided_monster.remove(self.monster_group)
                #check if there are any monsters left
                if self.monster_group:
                    #there are more monsters to catch
                    self.player.catch_sound.play()
                    self.choose_new_target()
                else:
                    #round is complete
                    self.player.reset()
                    self.start_new_round()

            #if we caught wrong monster
            else:
                #play die sound
                self.player.die_sounds.play()
                #decrease number of lives
                self.player.lives -= 1
                #check for game over
                if self.player.lives == 0:
                    self.pause_game()
                    self.reset_game()
                #if we caught wrong monster then return to original position 
                #on screen
                self.player.warp()
                self.pause_game()
                self.reset_game()

    def start_new_round(self):
        """Populate board with new monsters"""
        #the quicker the round is completed the bigger the score
        #provide a score bonus on how quickly the round was finished
        #adding 1 to round time because if round_time is zero will throw an error
        self.score += int(10000*self.round_number/1 + self.round_time)

        #reset round values
        self.round_time = 0
        self.frame_count = 0
        self.round_number += 1
        #give player extra warp
        self.player.warps += 1

        #if player dies with remaining monsters then reset game
        #loop through monster group and clear out all monsters
        for monster in self.monster_group:
            self.monster_group.remove(monster)

        #populate board with new monsters
        #for each round add four monsters
        #when round number is 1 for loop will run one time
        for i in range(self.round_number):
            #add four monsters, one for each color
            self.monster_group.add(Monster(random.randint(0, WINDOW_WIDTH - 64), random.randint(100, WINDOW_HEIGHT - 164), self.target_monster_images[0], 0))
            self.monster_group.add(Monster(random.randint(0, WINDOW_WIDTH - 64), random.randint(100, WINDOW_HEIGHT - 164), self.target_monster_images[1], 1))
            self.monster_group.add(Monster(random.randint(0, WINDOW_WIDTH - 64), random.randint(100, WINDOW_HEIGHT - 164), self.target_monster_images[2], 2))
            self.monster_group.add(Monster(random.randint(0, WINDOW_WIDTH - 64), random.randint(100, WINDOW_HEIGHT - 164), self.target_monster_images[3], 3))
        
            #choose a new target monster
            self.choose_new_target()

            #play next level sound
            self.next_level_sound.play()

    def choose_new_target(self):
        """CHoose a new target monster for the player"""
        pass

    def pause_game(self):
        """Pause the game"""
        pass

    def reset_game(self):
        """Reset the game"""
        pass
    

class Player(pygame.sprite.Sprite):
    """Player class that the user can control"""
    def __init__(self):
        """Initialize the player"""
        #initialize super class that is our sprite class
        #so we have access to all methods that are inside of sprite class
        super().__init__()
        #use self to link player to object
        self.image = pygame.image.load("knight.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = WINDOW_WIDTH//2
        self.rect.bottom = WINDOW_HEIGHT

        self.lives = 5
        self.warps = 5
        self.velocity = 8

        self.catch_sound = pygame.mixer.Sound("catch.wav")
        self.die_sounds = pygame.mixer.Sound("die.wav")
        self.warp_sound = pygame.mixer.Sound("warp.wav")

    #every sprite should have an update method
    def update(self):
        """Update the player"""
        keys = pygame.key.get_pressed()

        #move the player within the bounds of the screen
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.velocity
        if keys[pygame.K_RIGHT] and self.rect.right < WINDOW_WIDTH:
            self.rect.x += self.velocity
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.velocity
        if keys[pygame.K_DOWN] and self.rect.bottom < WINDOW_HEIGHT:
            self.rect.y += self.velocity


    def warp(self):
        """Warp the player to the bottom of the screen or safe zone away from monsters"""
        if self.warps > 0:
            self.warps -= 1
            self.warp_sound.play()
            #move player to the bottom, out of harms way
            self.rect.bottom = WINDOW_HEIGHT


    def reset(self):
        """Resets the player position"""
        #call this method anytime the player dies
        self.rect.centerx = WINDOW_WIDTH//2
        self.rect.bottom = WINDOW_HEIGHT


class Monster(pygame.sprite.Sprite):
    """A class to create monster enemy objects"""
    def __init__(self, x, y, image, monster_type):
        """Initialize the monster"""
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        #want position of each monster to be random and so use what we 
        #pass in
        self.rect.topleft = (x, y)

        #monster type is an int
        #0 -> blue, 1 -> green, 2 -> purple, 3 -> yellow
        self.type = monster_type

        #set random motion
        self.dx = random.choice([-1, 1])
        self.dy = random.choice([-1, 1])
        #speed at which monsters will move
        self.velocity = random.randint(1, 5)

    def update(self):
        """Update the monster"""
        #move the monster
        self.rect.x += self.dx*self.velocity
        self.rect.y += self.dy*self.velocity

        #bounce the monster of edges of display
        #change dx and dy values
        if self.rect.left <=0 or self.rect.right >= WINDOW_WIDTH:
            #change the direction of monster
            self.dx = -1*self.dx
        if self.rect.top <=0 or self.rect.bottom >= WINDOW_HEIGHT:
            #change the direction of monster 
            self.dy = -1*self.dy
    
#create a player group and player object
my_player_group = pygame.sprite.Group()
my_player = Player()
my_player_group.add(my_player)

#create a monster group
my_monster_group = pygame.sprite.Group()

#create a test monster - will delete this later
#monster = Monster(500, 500, pygame.image.load("green_monster.png"), 1)
#my_monster_group.add(monster)
#monster = Monster(100, 500, pygame.image.load("blue_monster.png"), 0)
#my_monster_group.add(monster)

#create a game object
my_game = Game(my_player, my_monster_group)
my_game.start_new_round()


#main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #fill display
    display_surface.fill((0, 0, 0))

    #update and draw sprite groups
    my_player_group.update()
    my_player_group.draw(display_surface)

    my_monster_group.update()
    my_monster_group.draw(display_surface)

    #we are writing our own draw method for my_game. we are not inheriting from the sprite class
    #that is why we don't have to pass in display_surface
    my_game.update()
    my_game.draw()

    #update display and tick the clock
    pygame.display.update()
    clock.tick(FPS)


#quit game
pygame.quit()