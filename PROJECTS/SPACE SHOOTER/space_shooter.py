# space_shooter.py
import pygame
import random
import sys
import math

# Initialize pygame-ce
pygame.init()

# Game Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
GRAY = (100, 100, 100)

# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🚀 Space Shooter")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)

# Load sounds (optional - will work without sound files)
try:
    shoot_sound = pygame.mixer.Sound("shoot.wav")
    explosion_sound = pygame.mixer.Sound("explosion.wav")
    powerup_sound = pygame.mixer.Sound("powerup.wav")
except:
    # Create simple sounds if files don't exist
    pass

class Player:
    def __init__(self):
        self.width = 40
        self.height = 40
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 100
        self.speed = 7
        self.shoot_cooldown = 0
        self.shoot_delay = 10
        self.lives = 3
        self.invincible = 0
        self.score = 0
        self.level = 1
        
        # Power-ups
        self.has_shield = False
        self.shield_timer = 0
        self.double_shot = False
        self.double_shot_timer = 0
        self.speed_boost = False
        self.speed_boost_timer = 0
    
    def update(self):
        keys = pygame.key.get_pressed()
        
        # Movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed
        
        # Keep player on screen
        self.x = max(0, min(WIDTH - self.width, self.x))
        self.y = max(0, min(HEIGHT - self.height, self.y))
        
        # Cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        # Power-up timers
        if self.has_shield:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.has_shield = False
        
        if self.double_shot:
            self.double_shot_timer -= 1
            if self.double_shot_timer <= 0:
                self.double_shot = False
        
        if self.speed_boost:
            self.speed_boost_timer -= 1
            if self.speed_boost_timer <= 0:
                self.speed_boost = False
                self.speed = 7
        
        # Invincibility
        if self.invincible > 0:
            self.invincible -= 1
    
    def shoot(self, bullets):
        if self.shoot_cooldown == 0:
            if self.double_shot:
                # Two bullets
                bullets.append(Bullet(self.x + 5, self.y, 0, -10))
                bullets.append(Bullet(self.x + self.width - 5, self.y, 0, -10))
            else:
                # One bullet
                bullets.append(Bullet(self.x + self.width//2 - 2, self.y, 0, -12))
            self.shoot_cooldown = self.shoot_delay
            return True
        return False
    
    def draw(self, screen):
        # Draw ship (triangle with details)
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Main ship body
        points = [
            (center_x, self.y),  # Top
            (self.x, self.y + self.height),  # Bottom left
            (self.x + self.width, self.y + self.height)  # Bottom right
        ]
        
        # Color with invincibility flashing
        if self.invincible > 0 and self.invincible % 10 < 5:
            pygame.draw.polygon(screen, GRAY, points)
        else:
            pygame.draw.polygon(screen, CYAN, points)
            pygame.draw.polygon(screen, BLUE, points, 3)
        
        # Cockpit
        pygame.draw.circle(screen, WHITE, (center_x, self.y + 15), 8)
        pygame.draw.circle(screen, CYAN, (center_x, self.y + 15), 5)
        
        # Engine glow
        pygame.draw.circle(screen, ORANGE, (center_x, self.y + self.height), 10)
        pygame.draw.circle(screen, YELLOW, (center_x, self.y + self.height), 5)
        
        # Shield
        if self.has_shield:
            pygame.draw.circle(screen, (0, 255, 255, 50), 
                             (center_x, center_y), 35, 3)
            pygame.draw.circle(screen, (0, 255, 255, 30), 
                             (center_x, center_y), 40, 1)

class Bullet:
    def __init__(self, x, y, speed_x, speed_y):
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.width = 4
        self.height = 12
        self.damage = 1
    
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
    
    def draw(self, screen):
        # Glowing bullet
        pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, WHITE, (self.x + 1, self.y, 2, self.height - 4))
        # Trail
        pygame.draw.rect(screen, (255, 255, 0, 50), 
                        (self.x, self.y + self.height, self.width, 5))
    
    def is_off_screen(self):
        return self.y < 0 or self.y > HEIGHT or self.x < 0 or self.x > WIDTH

class Enemy:
    def __init__(self, x, y, enemy_type=0):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.width = 40
        self.height = 40
        self.shoot_timer = random.randint(30, 90)
        
        # Different enemy types
        if enemy_type == 0:  # Basic enemy
            self.speed = 2
            self.health = 1
            self.color = RED
            self.score_value = 10
        elif enemy_type == 1:  # Fast enemy
            self.speed = 4
            self.health = 1
            self.color = ORANGE
            self.score_value = 15
        elif enemy_type == 2:  # Tank enemy
            self.speed = 1
            self.health = 3
            self.color = PURPLE
            self.score_value = 30
        elif enemy_type == 3:  # Shooter enemy
            self.speed = 1.5
            self.health = 2
            self.color = GREEN
            self.score_value = 25
    
    def update(self):
        self.y += self.speed
        self.shoot_timer -= 1
    
    def draw(self, screen):
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Enemy shape based on type
        if self.enemy_type == 0:  # Basic - square
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height), 2)
            # Eyes
            pygame.draw.circle(screen, WHITE, (self.x + 10, self.y + 15), 5)
            pygame.draw.circle(screen, WHITE, (self.x + 30, self.y + 15), 5)
            pygame.draw.circle(screen, BLACK, (self.x + 10, self.y + 15), 2)
            pygame.draw.circle(screen, BLACK, (self.x + 30, self.y + 15), 2)
        
        elif self.enemy_type == 1:  # Fast - triangle
            points = [
                (center_x, self.y),
                (self.x, self.y + self.height),
                (self.x + self.width, self.y + self.height)
            ]
            pygame.draw.polygon(screen, self.color, points)
            pygame.draw.polygon(screen, ORANGE, points, 2)
        
        elif self.enemy_type == 2:  # Tank - hexagon
            points = []
            for i in range(6):
                angle = math.radians(60 * i - 30)
                px = center_x + 20 * math.cos(angle)
                py = center_y + 20 * math.sin(angle)
                points.append((px, py))
            pygame.draw.polygon(screen, self.color, points)
            pygame.draw.polygon(screen, PURPLE, points, 3)
            # Health bar
            bar_width = 30
            bar_height = 4
            health_percent = self.health / 3
            pygame.draw.rect(screen, RED, (center_x - 15, self.y - 10, bar_width, bar_height))
            pygame.draw.rect(screen, GREEN, (center_x - 15, self.y - 10, bar_width * health_percent, bar_height))
        
        elif self.enemy_type == 3:  # Shooter - circle with gun
            pygame.draw.circle(screen, self.color, (center_x, center_y), 20)
            pygame.draw.circle(screen, GREEN, (center_x, center_y), 20, 2)
            # Gun barrel
            pygame.draw.line(screen, WHITE, (center_x, center_y), (center_x, self.y - 5), 3)
            # Health bar
            bar_width = 30
            bar_height = 4
            health_percent = self.health / 2
            pygame.draw.rect(screen, RED, (center_x - 15, self.y - 10, bar_width, bar_height))
            pygame.draw.rect(screen, GREEN, (center_x - 15, self.y - 10, bar_width * health_percent, bar_height))
    
    def shoot(self, bullets):
        if self.shoot_timer <= 0 and self.enemy_type == 3:
            bullets.append(EnemyBullet(self.x + self.width//2 - 3, self.y + self.height, 5))
            self.shoot_timer = 60
            return True
        return False
    
    def is_off_screen(self):
        return self.y > HEIGHT + 50

class EnemyBullet:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.width = 6
        self.height = 10
    
    def update(self):
        self.y += self.speed
    
    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, ORANGE, (self.x + 1, self.y + 2, 4, 6))
    
    def is_off_screen(self):
        return self.y > HEIGHT

class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.type = power_type  # 0: Shield, 1: Double Shot, 2: Speed Boost
        self.width = 20
        self.height = 20
        self.speed = 2
        self.bob_offset = 0
        
        # Colors
        self.colors = {
            0: BLUE,   # Shield
            1: YELLOW, # Double Shot
            2: CYAN    # Speed Boost
        }
        self.symbols = {
            0: "🛡️",
            1: "⚡",
            2: "💨"
        }
    
    def update(self):
        self.y += self.speed
        self.bob_offset += 0.1
    
    def draw(self, screen):
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2 + math.sin(self.bob_offset) * 3
        
        # Glow effect
        pygame.draw.circle(screen, self.colors[self.type], 
                          (center_x, center_y), 25, 2)
        
        # Main shape
        pygame.draw.rect(screen, self.colors[self.type], 
                        (self.x, center_y - 10, self.width, self.height))
        pygame.draw.rect(screen, WHITE, 
                        (self.x, center_y - 10, self.width, self.height), 2)
        
        # Symbol
        text = font.render(self.symbols[self.type], True, WHITE)
        screen.blit(text, (self.x - 2, center_y - 12))
    
    def is_off_screen(self):
        return self.y > HEIGHT

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.randint(1, 3)
        self.size = random.randint(1, 3)
        self.brightness = random.randint(100, 255)
    
    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)
    
    def draw(self, screen):
        pygame.draw.circle(screen, (self.brightness, self.brightness, self.brightness), 
                          (self.x, self.y), self.size)

def show_start_screen():
    screen.fill(BLACK)
    
    # Animated title
    title = big_font.render("🚀 SPACE SHOOTER", True, CYAN)
    title_shadow = big_font.render("🚀 SPACE SHOOTER", True, BLUE)
    screen.blit(title_shadow, (WIDTH//2 - title.get_width()//2 + 3, HEIGHT//2 - 120 + 3))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 120))
    
    # Controls
    controls = [
        "🔼 Move: Arrow Keys or WASD",
        "🔫 Shoot: SPACE",
        "🛡️ Shield: Press S",
        "",
        "Press SPACE to Start"
    ]
    
    for i, text in enumerate(controls):
        rendered = font.render(text, True, WHITE if "SPACE" not in text else YELLOW)
        screen.blit(rendered, (WIDTH//2 - rendered.get_width()//2, HEIGHT//2 - 20 + i * 40))
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False

def spawn_enemy(enemies, level):
    # Spawn rate based on level
    spawn_chance = min(0.02 + level * 0.005, 0.08)
    
    if random.random() < spawn_chance:
        enemy_type = 0
        # Different enemy types at higher levels
        if level >= 2:
            enemy_type = random.choices([0, 1, 2, 3], weights=[5, 3, 2, 1])[0]
        elif level >= 1:
            enemy_type = random.choices([0, 1], weights=[7, 3])[0]
        
        x = random.randint(0, WIDTH - 40)
        enemies.append(Enemy(x, -40, enemy_type))

def main():
    # Initialize
    player = Player()
    bullets = []
    enemy_bullets = []
    enemies = []
    powerups = []
    stars = [Star() for _ in range(50)]
    
    score = 0
    level = 1
    enemies_destroyed = 0
    game_over = False
    paused = False
    spawn_timer = 0
    
    show_start_screen()
    
    # Main game loop
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_p:
                    paused = not paused
                if event.key == pygame.K_SPACE and not game_over and not paused:
                    if player.shoot(bullets):
                        try:
                            shoot_sound.play()
                        except:
                            pass
                if event.key == pygame.K_s and not game_over and not paused:
                    # Activate shield power-up if available
                    pass
                if event.key == pygame.K_SPACE and game_over:
                    # Restart
                    player = Player()
                    bullets = []
                    enemy_bullets = []
                    enemies = []
                    powerups = []
                    score = 0
                    level = 1
                    enemies_destroyed = 0
                    game_over = False
        
        if not game_over and not paused:
            # Update player
            player.update()
            
            # Shoot with space held down
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                if player.shoot(bullets):
                    try:
                        shoot_sound.play()
                    except:
                        pass
            
            # Update bullets
            for bullet in bullets[:]:
                bullet.update()
                if bullet.is_off_screen():
                    bullets.remove(bullet)
            
            # Update enemy bullets
            for bullet in enemy_bullets[:]:
                bullet.update()
                if bullet.is_off_screen():
                    enemy_bullets.remove(bullet)
            
            # Spawn enemies
            spawn_timer += 1
            if spawn_timer > 30:
                spawn_enemy(enemies, level)
                spawn_timer = 0
            
            # Update enemies
            for enemy in enemies[:]:
                enemy.update()
                if enemy.is_off_screen():
                    enemies.remove(enemy)
                else:
                    # Enemy shooting
                    if enemy.shoot(enemy_bullets):
                        pass
            
            # Update powerups
            for powerup in powerups[:]:
                powerup.update()
                if powerup.is_off_screen():
                    powerups.remove(powerup)
            
            # Update stars
            for star in stars:
                star.update()
            
            # Collision detection - Bullets vs Enemies
            for bullet in bullets[:]:
                for enemy in enemies[:]:
                    if (bullet.x < enemy.x + enemy.width and
                        bullet.x + bullet.width > enemy.x and
                        bullet.y < enemy.y + enemy.height and
                        bullet.y + bullet.height > enemy.y):
                        # Hit!
                        enemy.health -= bullet.damage
                        bullets.remove(bullet)
                        if enemy.health <= 0:
                            enemies.remove(enemy)
                            enemies_destroyed += 1
                            score += enemy.score_value
                            
                            # Level up
                            if enemies_destroyed % 10 == 0:
                                level += 1
                            
                            # Drop power-up
                            if random.random() < 0.15:  # 15% chance
                                power_type = random.randint(0, 2)
                                powerups.append(PowerUp(enemy.x, enemy.y, power_type))
                                try:
                                    powerup_sound.play()
                                except:
                                    pass
                            
                            try:
                                explosion_sound.play()
                            except:
                                pass
                        break
            
            # Collision detection - Enemy bullets vs Player
            for bullet in enemy_bullets[:]:
                if (bullet.x < player.x + player.width and
                    bullet.x + bullet.width > player.x and
                    bullet.y < player.y + player.height and
                    bullet.y + bullet.height > player.y):
                    if player.invincible == 0 and not player.has_shield:
                        player.lives -= 1
                        player.invincible = 60
                        enemy_bullets.remove(bullet)
                        if player.lives <= 0:
                            game_over = True
                    elif player.has_shield:
                        enemy_bullets.remove(bullet)
                        player.has_shield = False
            
            # Collision detection - Enemies vs Player
            for enemy in enemies[:]:
                if (enemy.x < player.x + player.width and
                    enemy.x + enemy.width > player.x and
                    enemy.y < player.y + player.height and
                    enemy.y + enemy.height > player.y):
                    if player.invincible == 0 and not player.has_shield:
                        player.lives -= 1
                        player.invincible = 60
                        enemies.remove(enemy)
                        if player.lives <= 0:
                            game_over = True
                    elif player.has_shield:
                        enemies.remove(enemy)
                        player.has_shield = False
            
            # Collision detection - Powerups vs Player
            for powerup in powerups[:]:
                if (powerup.x < player.x + player.width and
                    powerup.x + powerup.width > player.x and
                    powerup.y < player.y + player.height and
                    powerup.y + powerup.height > player.y):
                    if powerup.type == 0:  # Shield
                        player.has_shield = True
                        player.shield_timer = 300
                    elif powerup.type == 1:  # Double Shot
                        player.double_shot = True
                        player.double_shot_timer = 300
                    elif powerup.type == 2:  # Speed Boost
                        player.speed_boost = True
                        player.speed_boost_timer = 300
                        player.speed = 12
                    powerups.remove(powerup)
                    try:
                        powerup_sound.play()
                    except:
                        pass
            
            # Update player score
            player.score = score
            player.level = level
        
        # Drawing
        screen.fill(BLACK)
        
        # Draw stars (parallax)
        for star in stars:
            star.draw(screen)
        
        # Draw powerups
        for powerup in powerups:
            powerup.draw(screen)
        
        # Draw bullets
        for bullet in bullets:
            bullet.draw(screen)
        
        # Draw enemy bullets
        for bullet in enemy_bullets:
            bullet.draw(screen)
        
        # Draw enemies
        for enemy in enemies:
            enemy.draw(screen)
        
        # Draw player
        if not game_over:
            player.draw(screen)
        
        # Draw UI
        ui_y = 10
        
        # Score and level
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, ui_y))
        
        level_text = font.render(f"Level: {level}", True, YELLOW)
        screen.blit(level_text, (10, ui_y + 35))
        
        # Lives
        lives_text = font.render(f"❤️ x {player.lives}", True, RED)
        screen.blit(lives_text, (WIDTH - lives_text.get_width() - 10, ui_y))
        
        # Power-up indicators
        power_y = ui_y + 35
        if player.has_shield:
            shield_text = font.render("🛡️ Shield", True, BLUE)
            screen.blit(shield_text, (WIDTH - shield_text.get_width() - 10, power_y))
            power_y += 30
        if player.double_shot:
            double_text = font.render("⚡ Double Shot", True, YELLOW)
            screen.blit(double_text, (WIDTH - double_text.get_width() - 10, power_y))
            power_y += 30
        if player.speed_boost:
            speed_text = font.render("💨 Speed Boost", True, CYAN)
            screen.blit(speed_text, (WIDTH - speed_text.get_width() - 10, power_y))
        
        # Pause screen
        if paused:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            pause_text = big_font.render("PAUSED", True, WHITE)
            screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 50))
            continue_text = font.render("Press P to continue", True, GRAY)
            screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT//2 + 20))
        
        # Game Over screen
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            game_over_text = big_font.render("GAME OVER", True, RED)
            score_text_go = font.render(f"Score: {score}", True, WHITE)
            level_text_go = font.render(f"Level Reached: {level}", True, YELLOW)
            restart_text = font.render("Press SPACE to restart", True, GREEN)
            quit_text = font.render("Press ESC to quit", True, GRAY)
            
            screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 100))
            screen.blit(score_text_go, (WIDTH//2 - score_text_go.get_width()//2, HEIGHT//2 - 20))
            screen.blit(level_text_go, (WIDTH//2 - level_text_go.get_width()//2, HEIGHT//2 + 30))
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 90))
            screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 130))
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()