import pygame
import sys
import random
import asyncio

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)
PURPLE = (128, 0, 128)
DARK_GREEN = (0, 100, 0)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
DARK_RED = (139, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
SILVER = (192, 192, 192)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sacrifice Must Be Made - Dangerous Coins")
clock = pygame.time.Clock()


font_large = pygame.font.SysFont('Arial', 36)
font_medium = pygame.font.SysFont('Arial', 24)
font_small = pygame.font.SysFont('Arial', 18)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 50))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = SCREEN_HEIGHT - 150
        
        
        self.velocity_x = 0
        self.velocity_y = 0
        self.max_speed = 8
        self.acceleration = 0.5
        self.deceleration = 0.8
        self.jump_power = -15
        self.gravity = 0.8
        self.max_fall_speed = 15
        
        
        self.jumping = False
        self.can_jump = False
        self.jump_cut = False
        self.coyote_time = 0
        self.max_coyote_time = 7  
        self.jump_buffer = 0
        self.max_jump_buffer = 5  
    
        self.health = 100
        self.max_health = 100
        self.sacrifice_points = 0
        self.sacrifice_cost = 10
        self.invincible = False
        self.invincible_timer = 0
        self.level = 1
        self.lives = 3
        self.on_ground = False
        self.ground_damage_timer = 0
        
        
        self.coins_collected = 0
        self.total_coins_collected = 0
        self.coin_damage = 5  
        
    
        self.facing_right = True
        
    def update(self, platforms, spikes, moving_platforms, coins):
        keys = pygame.key.get_pressed()
        
       
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x = max(self.velocity_x - self.acceleration, -self.max_speed)
            self.facing_right = False
          
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = min(self.velocity_x + self.acceleration, self.max_speed)
            self.facing_right = True
       
        else:
            if self.velocity_x > 0:
                self.velocity_x = max(0, self.velocity_x - self.deceleration)
            elif self.velocity_x < 0:
                self.velocity_x = min(0, self.velocity_x + self.deceleration)
        
        
        self.velocity_y = min(self.velocity_y + self.gravity, self.max_fall_speed)
        
        
        old_x, old_y = self.rect.x, self.rect.y
        
        self.rect.x += self.velocity_x
        
       
        platform_hit_x = pygame.sprite.spritecollide(self, platforms, False)
        for p in platform_hit_x:
            if self.velocity_x > 0:
                self.rect.right = p.rect.left
                self.velocity_x = 0
            elif self.velocity_x < 0:
                self.rect.left = p.rect.right
                self.velocity_x = 0
        
        
        self.rect.y += self.velocity_y
        
        
        self.on_ground = False
        
        
        platform_hit_y = pygame.sprite.spritecollide(self, platforms, False)
        for p in platform_hit_y:
            if self.velocity_y > 0:
                self.rect.bottom = p.rect.top
                self.velocity_y = 0
                self.on_ground = True
                self.jumping = False
                self.can_jump = True
                self.coyote_time = self.max_coyote_time
            elif self.velocity_y < 0:
                self.rect.top = p.rect.bottom
                self.velocity_y = 0
        
        moving_platform_hit = pygame.sprite.spritecollide(self, moving_platforms, False)
        for mp in moving_platform_hit:
            if self.velocity_y > 0 and self.rect.bottom > mp.rect.top and self.rect.top < mp.rect.top:
                self.rect.bottom = mp.rect.top
                self.velocity_y = 0
                self.on_ground = True
                self.jumping = False
                self.can_jump = True
                self.coyote_time = self.max_coyote_time
                self.rect.x += mp.direction * mp.speed
        
        if self.rect.bottom >= SCREEN_HEIGHT - 50:
            self.rect.bottom = SCREEN_HEIGHT - 50
            self.velocity_y = 0
            self.on_ground = True
            self.jumping = False
            self.can_jump = True
            self.coyote_time = self.max_coyote_time
            
            if not self.invincible:
                self.ground_damage_timer += 1
                if self.ground_damage_timer >= 120:
                    self.health -= 1
                    self.ground_damage_timer = 0
                    self.invincible = True
                    self.invincible_timer = 30
        else:
            self.ground_damage_timer = 0
            
            if self.coyote_time > 0:
                self.coyote_time -= 1
                if self.coyote_time == 0:
                    self.can_jump = False
        
        if self.jump_buffer > 0:
            self.jump_buffer -= 1
            if self.can_jump and self.jump_buffer > 0:
                self.jump()
                self.jump_buffer = 0
        
        if self.jumping and self.velocity_y < 0:
            if not (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]):
                self.velocity_y = max(self.velocity_y, self.jump_power * 0.5)  # Reduce jump height
        
        if not self.invincible:
            spike_hit = pygame.sprite.spritecollide(self, spikes, False)
            if spike_hit:
                self.health -= 10
                self.invincible = True
                self.invincible_timer = 60
        
        coin_hit = pygame.sprite.spritecollide(self, coins, True)
        for coin in coin_hit:
            if not self.invincible:
                self.health -= self.coin_damage
                self.invincible = True
                self.invincible_timer = 30
            self.coins_collected += 1
            self.total_coins_collected += 1
        
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
            if self.invincible_timer % 10 < 5:
                self.image.fill(BLUE)
            else:
                self.image.fill(WHITE)
        else:
            self.image.fill(BLUE)
        
        if self.rect.left < 0:
            self.rect.left = 0
            self.velocity_x = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.velocity_x = 0
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity_y = 0
            
    def jump(self):
        if self.can_jump:
            self.velocity_y = self.jump_power
            self.jumping = True
            self.can_jump = False
            self.coyote_time = 0
            return True
        return False
    
    def queue_jump(self):
        self.jump_buffer = self.max_jump_buffer
        
    def make_sacrifice(self, platforms, spikes, moving_platforms, coins):
        if self.sacrifice_points >= self.sacrifice_cost:
            self.sacrifice_points -= self.sacrifice_cost
            self.health += 20
            if self.health > self.max_health:
                self.health = self.max_health
                
            temp_platform = Platform(self.rect.centerx, self.rect.top - 20, 100, 20, True)
            platforms.add(temp_platform)
            
            for spike in spikes:
                if random.random() < 0.3:
                    spike.kill()
                    
            for coin in coins:
                if random.random() < 0.2:
                    coin.kill()
                    
            self.sacrifice_cost += 5
                    
            return True
        return False
        
    def reset_position(self):
        self.rect.x = 100
        self.rect.y = SCREEN_HEIGHT - 150
        self.velocity_x = 0
        self.velocity_y = 0
        self.jumping = False
        self.can_jump = False
        self.health = self.max_health
        self.invincible = True
        self.invincible_timer = 120
        self.on_ground = False
        self.ground_damage_timer = 0
        self.coyote_time = 0
        self.jump_buffer = 0
        
    def lose_all_coins(self):
        """Lose all collected coins when game over"""
        coins_lost = self.coins_collected
        self.coins_collected = 0
        return coins_lost

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, temporary=False):
        super().__init__()
        self.image = pygame.Surface((width, height))
        if temporary:
            self.image.fill(PURPLE)
        else:
            self.image.fill(BROWN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.temporary = temporary
        self.timer = 300 if temporary else 0
        
    def update(self):
        if self.temporary:
            self.timer -= 1
            if self.timer <= 0:
                self.kill()

class MovingPlatform(Platform):
    def __init__(self, x, y, width, height, move_range, speed=2):
        super().__init__(x, y, width, height)
        self.image.fill(ORANGE)
        self.start_x = x
        self.move_range = move_range
        self.speed = speed
        self.direction = 1
        
    def update(self):
        self.rect.x += self.direction * self.speed
        if self.rect.x <= self.start_x or self.rect.x >= self.start_x + self.move_range:
            self.direction *= -1

class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        pygame.draw.polygon(self.image, WHITE, [(15, 0), (0, 30), (30, 30)])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((25, 25), pygame.SRCALPHA)      #for coin
        pygame.draw.circle(self.image, GOLD, (12, 12), 10)
        pygame.draw.circle(self.image, YELLOW, (12, 12), 8)
       
        font = pygame.font.SysFont('Arial', 14, bold=True)      #for symbiols
        dollar_text = font.render("$", True, BLACK)
        text_rect = dollar_text.get_rect(center=(12, 12))
        self.image.blit(dollar_text, text_rect)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.float_timer = 0
        self.float_direction = 1
        
    def update(self):
        self.float_timer += 1
        if self.float_timer >= 30:
            self.float_timer = 0
            self.float_direction *= -1
        
        self.rect.y += self.float_direction * 0.5

class Goal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 60))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, patrol_range=100, speed=2):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.start_x = x
        self.patrol_range = patrol_range
        self.speed = speed
        self.direction = 1
        
    def update(self):
        self.rect.x += self.direction * self.speed
        if self.rect.x <= self.start_x or self.rect.x >= self.start_x + self.patrol_range:
            self.direction *= -1

class CursedGround(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((SCREEN_WIDTH, 50))
        self.image.fill(DARK_RED)
        for i in range(0, SCREEN_WIDTH, 40):
            pygame.draw.rect(self.image, (80, 0, 0), (i, 0, 20, 50))
            pygame.draw.rect(self.image, (100, 0, 0), (i + 20, 10, 20, 40))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = SCREEN_HEIGHT - 50
        self.pulse_timer = 0
        
    def update(self):
        self.pulse_timer += 1
        if self.pulse_timer >= 30:
            self.pulse_timer = 0
            self.image.fill(DARK_RED)
            for i in range(0, SCREEN_WIDTH, 40):
                pygame.draw.rect(self.image, (80, 0, 0), (i, 0, 20, 50))
                pygame.draw.rect(self.image, (100, 0, 0), (i + 20, 10, 20, 40))

def create_level(level_num):
    platforms = pygame.sprite.Group()
    spikes = pygame.sprite.Group()
    moving_platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    cursed_ground = pygame.sprite.GroupSingle(CursedGround())
    goal = pygame.sprite.GroupSingle()
    
    



    platforms.add(Platform(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
    
    if level_num == 1:
        platforms.add(Platform(100, SCREEN_HEIGHT - 150, 200, 20))
        platforms.add(Platform(400, SCREEN_HEIGHT - 250, 200, 20))
        platforms.add(Platform(200, SCREEN_HEIGHT - 350, 150, 20))
        platforms.add(Platform(500, SCREEN_HEIGHT - 450, 200, 20))
        
        spikes.add(Spike(300, SCREEN_HEIGHT - 80))
        spikes.add(Spike(450, SCREEN_HEIGHT - 280))
        1
        coins.add(Coin(150, SCREEN_HEIGHT - 170))
        coins.add(Coin(450, SCREEN_HEIGHT - 270))
        coins.add(Coin(250, SCREEN_HEIGHT - 370))
        coins.add(Coin(550, SCREEN_HEIGHT - 470))
        
        goal.add(Goal(650, SCREEN_HEIGHT - 510))
        
    elif level_num == 2:
        platforms.add(Platform(100, SCREEN_HEIGHT - 150, 150, 20))
        platforms.add(Platform(400, SCREEN_HEIGHT - 250, 150, 20))
        
        moving_platforms.add(MovingPlatform(200, SCREEN_HEIGHT - 200, 100, 20, 200, 2))
        moving_platforms.add(MovingPlatform(500, SCREEN_HEIGHT - 350, 100, 20, 150, 3))
        
        spikes.add(Spike(350, SCREEN_HEIGHT - 80))
        spikes.add(Spike(250, SCREEN_HEIGHT - 230))
        spikes.add(Spike(550, SCREEN_HEIGHT - 380))
        
        coins.add(Coin(150, SCREEN_HEIGHT - 170))
        coins.add(Coin(450, SCREEN_HEIGHT - 270))
        coins.add(Coin(550, SCREEN_HEIGHT - 370))
        coins.add(Coin(220, SCREEN_HEIGHT - 220))
        coins.add(Coin(520, SCREEN_HEIGHT - 380))
        
        goal.add(Goal(700, SCREEN_HEIGHT - 400))
        
    elif level_num == 3:
        platforms.add(Platform(100, SCREEN_HEIGHT - 150, 150, 20))
        platforms.add(Platform(350, SCREEN_HEIGHT - 250, 150, 20))
        platforms.add(Platform(200, SCREEN_HEIGHT - 350, 100, 20))
        platforms.add(Platform(500, SCREEN_HEIGHT - 450, 150, 20))
        
        moving_platforms.add(MovingPlatform(600, SCREEN_HEIGHT - 300, 100, 20, 100, 2))
        
        spikes.add(Spike(300, SCREEN_HEIGHT - 80))
        spikes.add(Spike(450, SCREEN_HEIGHT - 280))
        spikes.add(Spike(250, SCREEN_HEIGHT - 380))
        
        enemies.add(Enemy(150, SCREEN_HEIGHT - 180, 100, 2))
        enemies.add(Enemy(400, SCREEN_HEIGHT - 280, 150, 3))
        
        coins.add(Coin(180, SCREEN_HEIGHT - 170))
        coins.add(Coin(400, SCREEN_HEIGHT - 270))
        coins.add(Coin(250, SCREEN_HEIGHT - 370))
        coins.add(Coin(550, SCREEN_HEIGHT - 470))
        coins.add(Coin(320, SCREEN_HEIGHT - 290))
        coins.add(Coin(580, SCREEN_HEIGHT - 320))
        
        goal.add(Goal(700, SCREEN_HEIGHT - 510))
        
    elif level_num == 4:
        platforms.add(Platform(100, SCREEN_HEIGHT - 150, 100, 20))
        platforms.add(Platform(300, SCREEN_HEIGHT - 250, 100, 20))
        platforms.add(Platform(500, SCREEN_HEIGHT - 350, 100, 20))
        platforms.add(Platform(200, SCREEN_HEIGHT - 450, 100, 20))
        
        moving_platforms.add(MovingPlatform(150, SCREEN_HEIGHT - 300, 80, 20, 200, 3))
        moving_platforms.add(MovingPlatform(400, SCREEN_HEIGHT - 400, 80, 20, 150, 4))
        
        spikes.add(Spike(250, SCREEN_HEIGHT - 80))
        spikes.add(Spike(450, SCREEN_HEIGHT - 180))
        spikes.add(Spike(350, SCREEN_HEIGHT - 280))
        spikes.add(Spike(550, SCREEN_HEIGHT - 380))
        spikes.add(Spike(250, SCREEN_HEIGHT - 480))
        
        enemies.add(Enemy(120, SCREEN_HEIGHT - 170, 80, 3))
        enemies.add(Enemy(320, SCREEN_HEIGHT - 270, 100, 2))
        enemies.add(Enemy(520, SCREEN_HEIGHT - 370, 120, 4))
        
        coins.add(Coin(130, SCREEN_HEIGHT - 170))
        coins.add(Coin(330, SCREEN_HEIGHT - 270))
        coins.add(Coin(530, SCREEN_HEIGHT - 370))
        coins.add(Coin(230, SCREEN_HEIGHT - 470))
        coins.add(Coin(380, SCREEN_HEIGHT - 290))
        coins.add(Coin(480, SCREEN_HEIGHT - 390))
        coins.add(Coin(280, SCREEN_HEIGHT - 320))
        
        goal.add(Goal(650, SCREEN_HEIGHT - 510))
        
    elif level_num == 5:
        platforms.add(Platform(100, SCREEN_HEIGHT - 150, 80, 20))
        platforms.add(Platform(250, SCREEN_HEIGHT - 250, 80, 20))
        platforms.add(Platform(400, SCREEN_HEIGHT - 350, 80, 20))
        platforms.add(Platform(550, SCREEN_HEIGHT - 450, 80, 20))
        
        moving_platforms.add(MovingPlatform(180, SCREEN_HEIGHT - 300, 60, 20, 150, 4))
        moving_platforms.add(MovingPlatform(330, SCREEN_HEIGHT - 400, 60, 20, 120, 5))
        moving_platforms.add(MovingPlatform(480, SCREEN_HEIGHT - 200, 60, 20, 100, 3))
        
        for i in range(8):
            spikes.add(Spike(100 + i*80, SCREEN_HEIGHT - 80))
            
        spikes.add(Spike(200, SCREEN_HEIGHT - 280))
        spikes.add(Spike(350, SCREEN_HEIGHT - 380))
        spikes.add(Spike(500, SCREEN_HEIGHT - 480))
        
        enemies.add(Enemy(120, SCREEN_HEIGHT - 170, 60, 4))
        enemies.add(Enemy(270, SCREEN_HEIGHT - 270, 80, 3))
        enemies.add(Enemy(420, SCREEN_HEIGHT - 370, 100, 5))
        enemies.add(Enemy(570, SCREEN_HEIGHT - 470, 70, 4))
        
        coins.add(Coin(130, SCREEN_HEIGHT - 170))
        coins.add(Coin(280, SCREEN_HEIGHT - 270))
        coins.add(Coin(430, SCREEN_HEIGHT - 370))
        coins.add(Coin(580, SCREEN_HEIGHT - 470))
        coins.add(Coin(200, SCREEN_HEIGHT - 320))
        coins.add(Coin(350, SCREEN_HEIGHT - 420))
        coins.add(Coin(500, SCREEN_HEIGHT - 220))
        coins.add(Coin(620, SCREEN_HEIGHT - 280))
        
        goal.add(Goal(700, SCREEN_HEIGHT - 510))
    
    return platforms, spikes, moving_platforms, enemies, coins, cursed_ground, goal

def draw_health_bar(surface, x, y, health, max_health):
    bar_width = 200
    bar_height = 20
    fill = (health / max_health) * bar_width
    outline_rect = pygame.Rect(x, y, bar_width, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(surface, RED, fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 2)

def show_game_over_stats(screen, coins_collected, total_coins_collected, won_game=False):
    """Show final statistics when game ends"""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    if won_game:
        title = font_large.render("VICTORY!", True, GREEN)
    else:
        title = font_large.render("GAME OVER", True, RED)
    
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
    
    if won_game:
        coins_text = font_medium.render(f"Coins Collected: {coins_collected}", True, GOLD)
        screen.blit(coins_text, (SCREEN_WIDTH // 2 - coins_text.get_width() // 2, 220))
        
        total_text = font_medium.render(f"Total Coins in Adventure: {total_coins_collected}", True, SILVER)
        screen.blit(total_text, (SCREEN_WIDTH // 2 - total_text.get_width() // 2, 260))
        
        message = font_medium.render("You completed your journey with your treasures intact!", True, GREEN)
        screen.blit(message, (SCREEN_WIDTH // 2 - message.get_width() // 2, 320))
    else:
        coins_lost_text = font_medium.render(f"Coins Lost: {coins_collected}", True, RED)
        screen.blit(coins_lost_text, (SCREEN_WIDTH // 2 - coins_lost_text.get_width() // 2, 220))
        
        total_text = font_medium.render(f"Total Coins Collected: {total_coins_collected}", True, SILVER)
        screen.blit(total_text, (SCREEN_WIDTH // 2 - total_text.get_width() // 2, 260))
        
        message = font_medium.render("All coins lost! The curse claims its price...", True, YELLOW)
        screen.blit(message, (SCREEN_WIDTH // 2 - message.get_width() // 2, 320))
    
    restart_text = font_medium.render("Press R to restart your journey", True, WHITE)
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 400))

async def main():
    player = Player()
    platforms, spikes, moving_platforms, enemies, coins, cursed_ground, goal = create_level(player.level)
    
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    all_sprites.add(platforms)
    all_sprites.add(spikes)
    all_sprites.add(moving_platforms)
    all_sprites.add(enemies)
    all_sprites.add(coins)
    all_sprites.add(cursed_ground)
    all_sprites.add(goal)
    
    game_state = "playing"
    level_complete_timer = 0
    final_stats_shown = False
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                
                if event.key in [pygame.K_SPACE, pygame.K_UP, pygame.K_w] and game_state == "playing":
                    player.queue_jump()
                    
                if event.key == pygame.K_s and game_state == "playing":
                    player.make_sacrifice(platforms, spikes, moving_platforms, coins)
                    
                if event.key == pygame.K_r and game_state in ["win", "lose"]:
                    # Reset game
                    player = Player()
                    platforms, spikes, moving_platforms, enemies, coins, cursed_ground, goal = create_level(player.level)
                    all_sprites = pygame.sprite.Group()
                    all_sprites.add(player)
                    all_sprites.add(platforms)
                    all_sprites.add(spikes)
                    all_sprites.add(moving_platforms)
                    all_sprites.add(enemies)
                    all_sprites.add(coins)
                    all_sprites.add(cursed_ground)
                    all_sprites.add(goal)
                    game_state = "playing"
                    final_stats_shown = False
                    
                if event.key == pygame.K_n and game_state == "level_complete":
                    player.level += 1
                    if player.level > 5:
                        game_state = "win"
                    else:
                        platforms, spikes, moving_platforms, enemies, coins, cursed_ground, goal = create_level(player.level)
                        all_sprites = pygame.sprite.Group()
                        all_sprites.add(player)
                        all_sprites.add(platforms)
                        all_sprites.add(spikes)
                        all_sprites.add(moving_platforms)
                        all_sprites.add(enemies)
                        all_sprites.add(coins)
                        all_sprites.add(cursed_ground)
                        all_sprites.add(goal)
                        player.reset_position()
                        game_state = "playing"
        
        if game_state == "playing":
            
            player.update(platforms, spikes, moving_platforms, coins)       #for objects
            platforms.update()
            moving_platforms.update()
            enemies.update()
            coins.update()
            cursed_ground.update()
            
            
            if not player.invincible:               #for enemy collisions
                enemy_hit = pygame.sprite.spritecollide(player, enemies, False)
                if enemy_hit:
                    player.health -= 15
                    player.invincible = True
                    player.invincible_timer = 60
            
            if pygame.sprite.spritecollide(player, goal, False):
                game_state = "level_complete"
                level_complete_timer = 180
                
            if player.health <= 0:
                player.lives -= 1
                if player.lives <= 0:
                    game_state = "lose"
                else:
                    player.reset_position()
        
        elif game_state == "level_complete":
            level_complete_timer -= 1
            if level_complete_timer <= 0:
                player.level += 1
                if player.level > 5:
                    game_state = "win"
                else:
                    platforms, spikes, moving_platforms, enemies, coins, cursed_ground, goal = create_level(player.level)
                    all_sprites = pygame.sprite.Group()
                    all_sprites.add(player)
                    all_sprites.add(platforms)
                    all_sprites.add(spikes)
                    all_sprites.add(moving_platforms)
                    all_sprites.add(enemies)
                    all_sprites.add(coins)
                    all_sprites.add(cursed_ground)
                    all_sprites.add(goal)
                    player.reset_position()
                    game_state = "playing"
        




        screen.fill(BLACK)
        all_sprites.draw(screen)
        
        
        if player.on_ground and player.ground_damage_timer > 60:
            warning_text = font_medium.render("CURSED GROUND! FIND A PLATFORM!", True, YELLOW)
            screen.blit(warning_text, (SCREEN_WIDTH // 2 - warning_text.get_width() // 2, 100))
        
        
        draw_health_bar(screen, 10, 10, player.health, player.max_health)
        
        level_text = font_medium.render(f"Level: {player.level}/5", True, WHITE)
        screen.blit(level_text, (SCREEN_WIDTH - 120, 10))
        lives_text = font_medium.render(f"Lives: {player.lives}", True, WHITE)
        screen.blit(lives_text, (SCREEN_WIDTH - 120, 40))
        
        coin_color = GOLD if player.health > 30 else RED
        coin_text = font_medium.render(f"Coins: {player.coins_collected}", True, coin_color)
        screen.blit(coin_text, (10, 40))
        
        if player.coins_collected > 0:
            damage_warning = font_small.render(f"Each coin costs {player.coin_damage} HP!", True, RED)
            screen.blit(damage_warning, (10, 70))
        
        controls_text = font_small.render("WASD/Arrows: Move, SPACE/W/UP: Jump (hold for higher), S: Sacrifice", True, WHITE)
        screen.blit(controls_text, (SCREEN_WIDTH // 2 - controls_text.get_width() // 2, SCREEN_HEIGHT - 60))
        
        ground_info = font_small.render("The ground is cursed! Stay on platforms to avoid damage.", True, YELLOW)
        screen.blit(ground_info, (SCREEN_WIDTH // 2 - ground_info.get_width() // 2, SCREEN_HEIGHT - 30))
        




        if game_state == "win" and not final_stats_shown:
            show_game_over_stats(screen, player.coins_collected, player.total_coins_collected, won_game=True)
            final_stats_shown = True
        elif game_state == "lose" and not final_stats_shown:
            coins_lost = player.lose_all_coins()
            show_game_over_stats(screen, coins_lost, player.total_coins_collected, won_game=False)
            final_stats_shown = True
        elif game_state == "level_complete":
            complete_text = font_large.render(f"Level {player.level} Complete! Press N for next level", True, CYAN)
            screen.blit(complete_text, (SCREEN_WIDTH // 2 - complete_text.get_width() // 2, SCREEN_HEIGHT // 2))
        
        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)
asyncio.run(main())
        
