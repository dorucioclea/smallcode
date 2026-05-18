import pygame
import sys
import random

# --- Constants ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 150, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)

# --- Classes ---

class Enemy:
    def __init__(self, start_pos, health, speed, reward):
        self.x = start_pos[0]
        self.y = start_pos[1]
        self.health = health
        self.max_health = health
        self.speed = speed
        self.reward = reward
        self.rect = pygame.Rect(self.x, self.y, 30, 30)

    def move(self, target_pos):
        # Simple movement towards a fixed point (the end of the path)
        dx = target_pos[0] - self.x
        dy = target_pos[1] - self.y
        distance = pygame.math.Vector2(target_pos[0] - self.x, target_pos[1] - self.y).length()

        if distance > 0:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
        
        self.rect.topleft = (int(self.x), int(self.y))

    def draw(self, screen):
        # Draw enemy as a red square
        pygame.draw.rect(screen, RED, self.rect)
        # Draw health bar above the enemy
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, (255, 0, 0), (self.rect.left, self.rect.top - 10, self.rect.width * health_ratio, 5))

    def get_hit(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0
        return True # Indicates it was hit

class Tower:
    def __init__(self, x, y, tower_type="basic"):
        self.x = x
        self.y = y
        self.tower_type = tower_type
        self.range = 150
        self.damage = 10
        self.fire_rate = 60 # Frames between shots (lower is faster)
        self.last_shot_time = 0

    def draw(self, screen):
        # Draw tower as a blue square/structure
        pygame.draw.rect(screen, BLUE, (self.x - 25, self.y - 30, 50, 60))
        # Optional: Draw range indicator
        pygame.draw.circle(screen, (100, 100, 100), (int(self.x), int(self.y)), self.range, 2)

    def attack(self, enemies):
        global score
        # Find the weakest enemy in range to target
        target = None
        min_dist = float('inf')
        
        for enemy in enemies:
            distance = pygame.math.Vector2(enemy.rect.centerx, enemy.rect.centery).distance_to((self.x, self.y))
            if distance <= self.range and distance < min_dist:
                min_dist = distance
                target = enemy
        
        if target:
            # Simple attack logic: hit the first one found in range
            return True # Indicates an attack was made
        return False

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("SmallCode Tower Defense")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        # Game State Variables
        self.score = 0
        self.lives = 20
        self.wave_number = 0
        self.running = True

        # --- Game Elements Initialization ---
        self.enemies = []
        self.towers = [Tower(150, 300)] # Start with one tower at (x, y)
        self.path_end = (900, 200) # Target position for enemies

    def spawn_enemy(self):
        # Spawn point is assumed to be off-screen left
        start_pos = (0, random.randint(150, 450))
        health = 30 + self.wave_number * 5
        speed = 2 + self.wave_number * 0.1
        reward = 10 + self.wave_number * 2
        new_enemy = Enemy(start_pos, health, speed, reward)
        self.enemies.append(new_enemy)

    def update_game_state(self):
        # 1. Move Enemies
        for enemy in self.enemies:
            enemy.move(self.path_end)
            
        # 2. Tower Attacks (Simplified for now, assuming towers are placed correctly)
        for tower in self.towers:
            tower.attack(self.enemies)

        # 3. Check for Deaths/Progression
        new_enemies = []
        enemies_to_remove = []
        for i, enemy in enumerate(self.enemies):
            if enemy.rect.right > SCREEN_WIDTH - 50: # Reached the end of the map
                self.lives -= 1
                print(f"Enemy reached the end! Lives left: {self.lives}")
            else:
                new_enemies.append(enemy)
        self.enemies = new_enemies

        # 4. Wave Management (Simple spawning logic for demonstration)
        if len(self.enemies) < 10 and random.randint(1, 5) == 1:
            self.spawn_enemy()
        
        # Check win/loss conditions
        if self.lives <= 0:
            print("Game Over!")
            self.running = False

    def draw_ui(self):
        # Draw Score and Lives
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        pygame.draw.rect(self.screen, WHITE, (10, 10, 200, 40))
        self.screen.blit(score_text, (20, 20))

        lives_text = self.font.render(f"Lives: {self.lives}", True, BLACK)
        pygame.draw.rect(self.screen, WHITE, (230, 10, 150, 40))
        self.screen.blit(lives_text, (240, 20))

    def run_game(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                # Add mouse click handling for placing towers here later
                
            # Update logic
            self.update_game_state()

            # Drawing
            self.screen.fill(GREEN) # Grass background
            
            # Draw Path (Simple visual guide)
            pygame.draw.rect(self.screen, (100, 100, 100), (0, 0, SCREEN_WIDTH, 200))

            # Draw Towers
            for tower in self.towers:
                tower.draw(self.screen)
            
            # Draw Enemies and check hits
            for enemy in self.enemies:
                enemy.draw(self.screen)
            
            # Draw UI
            self.draw_ui()

            pygame.display.flip()
            self.clock.tick(FPS)

        print("Game loop finished.")


if __name__ == "__main__":
    game = Game()
    try:
        game.run_game()
    except pygame.error as e:
        print(f"Pygame Error: {e}")
        print("Make sure Pygame is installed: pip install pygame")
    finally:
        pygame.quit()