# snake_game.py
import pygame
import random
import sys

# Initialize pygame-ce
pygame.init()

# Game Constants
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (40, 40, 40)

# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🐍 Snake Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)

class Snake:
    def __init__(self):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.grow = False
    
    def move(self):
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False
    
    def change_direction(self, new_dir):
        # Prevent reversing
        if (new_dir[0] * -1, new_dir[1] * -1) != self.direction:
            self.direction = new_dir
    
    def check_collision(self):
        head = self.body[0]
        # Wall collision
        if head[0] < 0 or head[0] >= GRID_WIDTH or head[1] < 0 or head[1] >= GRID_HEIGHT:
            return True
        # Self collision
        if head in self.body[1:]:
            return True
        return False
    
    def draw(self, screen):
        for i, segment in enumerate(self.body):
            color = DARK_GREEN if i == 0 else GREEN
            pygame.draw.rect(screen, color,
                           (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE,
                            GRID_SIZE - 2, GRID_SIZE - 2))
            # Draw eyes on head
            if i == 0:
                eye_size = 3
                if self.direction == (1, 0):  # Right
                    pygame.draw.circle(screen, WHITE, 
                                     (segment[0] * GRID_SIZE + GRID_SIZE - 6, 
                                      segment[1] * GRID_SIZE + 5), eye_size)
                    pygame.draw.circle(screen, WHITE,
                                     (segment[0] * GRID_SIZE + GRID_SIZE - 6,
                                      segment[1] * GRID_SIZE + GRID_SIZE - 5), eye_size)
                elif self.direction == (-1, 0):  # Left
                    pygame.draw.circle(screen, WHITE,
                                     (segment[0] * GRID_SIZE + 6,
                                      segment[1] * GRID_SIZE + 5), eye_size)
                    pygame.draw.circle(screen, WHITE,
                                     (segment[0] * GRID_SIZE + 6,
                                      segment[1] * GRID_SIZE + GRID_SIZE - 5), eye_size)
                elif self.direction == (0, -1):  # Up
                    pygame.draw.circle(screen, WHITE,
                                     (segment[0] * GRID_SIZE + 5,
                                      segment[1] * GRID_SIZE + 6), eye_size)
                    pygame.draw.circle(screen, WHITE,
                                     (segment[0] * GRID_SIZE + GRID_SIZE - 5,
                                      segment[1] * GRID_SIZE + 6), eye_size)
                else:  # Down
                    pygame.draw.circle(screen, WHITE,
                                     (segment[0] * GRID_SIZE + 5,
                                      segment[1] * GRID_SIZE + GRID_SIZE - 6), eye_size)
                    pygame.draw.circle(screen, WHITE,
                                     (segment[0] * GRID_SIZE + GRID_SIZE - 5,
                                      segment[1] * GRID_SIZE + GRID_SIZE - 6), eye_size)

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.respawn([])
    
    def respawn(self, snake_body):
        while True:
            new_pos = (random.randint(0, GRID_WIDTH - 1),
                      random.randint(0, GRID_HEIGHT - 1))
            if new_pos not in snake_body:
                self.position = new_pos
                break
    
    def draw(self, screen):
        # Animated food with glow effect
        pygame.draw.rect(screen, RED,
                        (self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE,
                         GRID_SIZE - 2, GRID_SIZE - 2))
        # Small inner square
        pygame.draw.rect(screen, YELLOW,
                        (self.position[0] * GRID_SIZE + 5, self.position[1] * GRID_SIZE + 5,
                         10, 10))

def draw_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

def show_start_screen():
    screen.fill(BLACK)
    title = big_font.render("SNAKE GAME", True, GREEN)
    subtitle = font.render("Press SPACE to start", True, WHITE)
    controls = font.render("Arrow Keys to move", True, GRAY)
    
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 100))
    screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//2))
    screen.blit(controls, (WIDTH//2 - controls.get_width()//2, HEIGHT//2 + 50))
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

def main():
    # Show start screen
    show_start_screen()
    
    # Game variables
    snake = Snake()
    food = Food()
    score = 0
    game_over = False
    high_score = 0
    
    # Main game loop
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if not game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        snake.change_direction((0, -1))
                    elif event.key == pygame.K_DOWN:
                        snake.change_direction((0, 1))
                    elif event.key == pygame.K_LEFT:
                        snake.change_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        snake.change_direction((1, 0))
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    # Restart game
                    snake = Snake()
                    food = Food()
                    score = 0
                    game_over = False
        
        if not game_over:
            # Move snake
            snake.move()
            
            # Check food collision
            if snake.body[0] == food.position:
                snake.grow = True
                score += 10
                if score > high_score:
                    high_score = score
                food.respawn(snake.body)
            
            # Check game over
            if snake.check_collision():
                game_over = True
        
        # Drawing
        screen.fill(BLACK)
        draw_grid()
        
        # Draw food
        food.draw(screen)
        
        # Draw snake
        snake.draw(screen)
        
        # Draw UI
        score_text = font.render(f"Score: {score}", True, WHITE)
        high_text = font.render(f"Best: {high_score}", True, YELLOW)
        screen.blit(score_text, (10, 10))
        screen.blit(high_text, (WIDTH - high_text.get_width() - 10, 10))
        
        # Game over screen
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            game_over_text = big_font.render("GAME OVER", True, RED)
            score_text_go = font.render(f"Score: {score}", True, WHITE)
            restart_text = font.render("Press SPACE to restart", True, GREEN)
            
            screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 80))
            screen.blit(score_text_go, (WIDTH//2 - score_text_go.get_width()//2, HEIGHT//2))
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))
        
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()