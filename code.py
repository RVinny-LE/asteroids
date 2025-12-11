import pygame
import random
import math
import sys

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 100)
BLUE = (100, 150, 255)
YELLOW = (255, 255, 50)
GRAY = (150, 150, 150)

# Класс для астероидов
class Asteroid:
    def __init__(self):
        # Случайный размер астероида
        self.size = random.randint(20, 60)
        
        # Случайная позиция появления за пределами экрана
        side = random.randint(0, 3)  # 0: верх, 1: право, 2: низ, 3: лево
        
        if side == 0:  # Верх
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = -self.size
        elif side == 1:  # Право
            self.x = SCREEN_WIDTH + self.size
            self.y = random.randint(0, SCREEN_HEIGHT)
        elif side == 2:  # Низ
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = SCREEN_HEIGHT + self.size
        else:  # Лево
            self.x = -self.size
            self.y = random.randint(0, SCREEN_HEIGHT)
        
        # Случайное направление движения (к центру экрана с отклонением)
        center_x = SCREEN_WIDTH / 2
        center_y = SCREEN_HEIGHT / 2
        
        # Вектор направления к центру
        dx = center_x - self.x
        dy = center_y - self.y
        
        # Добавляем случайное отклонение
        angle_deviation = random.uniform(-0.5, 0.5)  # отклонение в радианах
        length = math.sqrt(dx*dx + dy*dy)
        
        if length > 0:
            # Нормализуем вектор
            dx /= length
            dy /= length
            
            # Поворачиваем вектор на случайный угол
            cos_a = math.cos(angle_deviation)
            sin_a = math.sin(angle_deviation)
            new_dx = dx * cos_a - dy * sin_a
            new_dy = dx * sin_a + dy * cos_a
            
            # Задаем скорость в зависимости от размера (большие медленнее)
            speed = random.uniform(1.0, 3.0) * (60.0 / self.size)
            self.dx = new_dx * speed
            self.dy = new_dy * speed
        else:
            self.dx = random.uniform(-2, 2)
            self.dy = random.uniform(-2, 2)
        
        # Цвет астероида
        self.color = random.choice([GRAY, (180, 180, 180), (200, 200, 200)])
        
        # Очки за уничтожение (меньше за большие астероиды)
        self.points = max(100 - self.size, 20)
    
    def update(self):
        # Движение астероида
        self.x += self.dx
        self.y += self.dy
        
        # Проверка выхода за границы экрана и перенос на противоположную сторону
        if self.x < -self.size * 2:
            self.x = SCREEN_WIDTH + self.size
        elif self.x > SCREEN_WIDTH + self.size * 2:
            self.x = -self.size
            
        if self.y < -self.size * 2:
            self.y = SCREEN_HEIGHT + self.size
        elif self.y > SCREEN_HEIGHT + self.size * 2:
            self.y = -self.size
    
    def draw(self, screen):
        # Рисуем астероид как круг (без эффекта объема)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        
        # Простой контур
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size, 2)
    
    def get_rect(self):
        # Возвращает прямоугольник для проверки столкновений
        return pygame.Rect(self.x - self.size, self.y - self.size, 
                          self.size * 2, self.size * 2)

# Класс для снарядов
class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.radius = 4
        self.speed = 10
        
        # Направление выстрела
        self.dx = math.cos(angle) * self.speed
        self.dy = -math.sin(angle) * self.speed  # Отрицательное значение, т.к. ось Y направлена вниз
        
        # Время жизни снаряда (в кадрах)
        self.lifetime = 90  # 1.5 секунды при 60 FPS
        
        # Цвет снаряда
        self.color = YELLOW
    
    def update(self):
        # Движение снаряда
        self.x += self.dx
        self.y += self.dy
        
        # Уменьшаем время жизни
        self.lifetime -= 1
        
        # Проверка выхода за границы экрана и перенос на противоположную сторону
        if self.x < -self.radius:
            self.x = SCREEN_WIDTH + self.radius
        elif self.x > SCREEN_WIDTH + self.radius:
            self.x = -self.radius
            
        if self.y < -self.radius:
            self.y = SCREEN_HEIGHT + self.radius
        elif self.y > SCREEN_HEIGHT + self.radius:
            self.y = -self.radius
        
        # Возвращает True, если снаряд еще "жив"
        return self.lifetime > 0
    
    def draw(self, screen):
        # Рисуем снаряд (без эффекта пламени)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
    
    def get_rect(self):
        # Возвращает прямоугольник для проверки столкновений
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)

# Класс для пушки
class Cannon:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 50
        self.width = 40
        self.height = 30
        self.angle = 0  # Угол в радианах, 0 = направлено вверх
        self.rotation_speed = 0.05
        self.color = BLUE
        self.cooldown = 0  # Время перезарядки
        self.cooldown_max = 10  # Кадры между выстрелами
    
    def update(self, keys):
        # Вращение пушки
        if keys[pygame.K_LEFT]:
            self.angle += self.rotation_speed
        if keys[pygame.K_RIGHT]:
            self.angle -= self.rotation_speed
        
        # Ограничение угла поворота
        if self.angle > math.pi / 2.2:  # Ограничение поворота влево
            self.angle = math.pi / 2.2
        if self.angle < -math.pi / 2.2:  # Ограничение поворота вправо
            self.angle = -math.pi / 2.2
        
        # Обновление перезарядки
        if self.cooldown > 0:
            self.cooldown -= 1
    
    def shoot(self):
        # Создание снаряда, если пушка готова стрелять
        if self.cooldown <= 0:
            self.cooldown = self.cooldown_max
            
            # Координаты дула пушки
            muzzle_x = self.x + math.cos(self.angle) * 40
            muzzle_y = self.y - math.sin(self.angle) * 40
            
            return Bullet(muzzle_x, muzzle_y, self.angle)
        return None
    
    def draw(self, screen):
        # Рисуем основание пушки
        pygame.draw.rect(screen, self.color, 
                        (self.x - self.width//2, self.y - self.height//2, 
                         self.width, self.height))
        
        # Рисуем ствол пушки
        barrel_length = 40
        barrel_end_x = self.x + math.cos(self.angle) * barrel_length
        barrel_end_y = self.y - math.sin(self.angle) * barrel_length
        
        pygame.draw.line(screen, GRAY, (self.x, self.y), 
                        (barrel_end_x, barrel_end_y), 12)

# Класс для игры
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Астероиды")
        self.clock = pygame.time.Clock()
        
        # Игровые объекты
        self.cannon = Cannon()
        self.asteroids = []
        self.bullets = []
        
        # Игровые параметры
        self.score = 0
        self.lives = 3
        self.level = 1
        self.asteroids_count = 5
        self.font = pygame.font.SysFont(None, 36)
        self.game_over = False
        self.game_started = False
        
        # Создание начальных астероидов
        for _ in range(self.asteroids_count):
            self.asteroids.append(Asteroid())
        
        # Время для генерации новых астероидов
        self.asteroid_timer = 0
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                # Запуск игры при нажатии пробела
                if event.key == pygame.K_SPACE:
                    if not self.game_started or self.game_over:
                        self.__init__()  # Перезапуск игры
                        self.game_started = True
                    else:
                        # Выстрел
                        bullet = self.cannon.shoot()
                        if bullet:
                            self.bullets.append(bullet)
        
        return True
    
    def update(self):
        if not self.game_started or self.game_over:
            return
        
        # Обновление состояния пушки
        keys = pygame.key.get_pressed()
        self.cannon.update(keys)
        
        # Автоматическая стрельба при удержании пробела
        if keys[pygame.K_SPACE]:
            bullet = self.cannon.shoot()
            if bullet:
                self.bullets.append(bullet)
        
        # Обновление астероидов
        for asteroid in self.asteroids[:]:
            asteroid.update()
        
        # Обновление снарядов
        for bullet in self.bullets[:]:
            if not bullet.update():
                self.bullets.remove(bullet)
        
        # Проверка столкновений снарядов с астероидами
        for bullet in self.bullets[:]:
            for asteroid in self.asteroids[:]:
                # Простая проверка столкновения по расстоянию
                distance = math.sqrt((bullet.x - asteroid.x)**2 + (bullet.y - asteroid.y)**2)
                if distance < asteroid.size + bullet.radius:
                    # Столкновение произошло
                    self.score += asteroid.points
                    self.asteroids.remove(asteroid)
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break
        
        # Проверка столкновений астероидов с пушкой
        for asteroid in self.asteroids[:]:
            # Проверяем столкновение астероида с пушкой
            cannon_rect = pygame.Rect(self.cannon.x - self.cannon.width//2,
                                     self.cannon.y - self.cannon.height//2,
                                     self.cannon.width, self.cannon.height)
            
            if asteroid.get_rect().colliderect(cannon_rect):
                self.asteroids.remove(asteroid)
                self.lives -= 1
                
                if self.lives <= 0:
                    self.game_over = True
        
        # Генерация новых астероидов
        self.asteroid_timer += 1
        if self.asteroid_timer >= 60:  # Новый астероид каждую секунду
            self.asteroid_timer = 0
            if len(self.asteroids) < 10 + self.level:  # Ограничение количества астероидов
                self.asteroids.append(Asteroid())
        
        # Повышение уровня
        if self.score >= self.level * 1000:
            self.level += 1
            # Добавляем больше астероидов при повышении уровня
            for _ in range(2):
                self.asteroids.append(Asteroid())
    
    def draw(self):
        # Задний фон (космос)
        self.screen.fill(BLACK)
        
        # Рисуем звезды на фоне
        for i in range(100):
            x = (i * 17) % SCREEN_WIDTH
            y = (i * 23) % SCREEN_HEIGHT
            size = (i % 3) + 1
            brightness = random.randint(150, 255)
            pygame.draw.circle(self.screen, (brightness, brightness, brightness), 
                             (x, y), size)
        
        # Рисуем астероиды
        for asteroid in self.asteroids:
            asteroid.draw(self.screen)
        
        # Рисуем снаряды
        for bullet in self.bullets:
            bullet.draw(self.screen)
        
        # Рисуем пушку
        self.cannon.draw(self.screen)
        
        # Отображение информации
        score_text = self.font.render(f"Очки: {self.score}", True, GREEN)
        self.screen.blit(score_text, (10, 10))
        
        lives_text = self.font.render(f"Жизни: {self.lives}", True, GREEN)
        self.screen.blit(lives_text, (10, 50))
        
        level_text = self.font.render(f"Уровень: {self.level}", True, GREEN)
        self.screen.blit(level_text, (10, 90))
        
        # Инструкции
        if not self.game_started:
            title_font = pygame.font.SysFont(None, 72)
            title_text = title_font.render("АСТЕРОИДЫ", True, BLUE)
            self.screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 150))
            
            instruction_font = pygame.font.SysFont(None, 36)
            instruction1 = instruction_font.render("Управление: ← → для поворота, ПРОБЕЛ для стрельбы", True, WHITE)
            instruction2 = instruction_font.render("Нажмите ПРОБЕЛ для начала игры", True, YELLOW)
            
            self.screen.blit(instruction1, (SCREEN_WIDTH//2 - instruction1.get_width()//2, 300))
            self.screen.blit(instruction2, (SCREEN_WIDTH//2 - instruction2.get_width()//2, 350))
            
            # Рисуем пример астероида
            example_asteroid = Asteroid()
            example_asteroid.x = SCREEN_WIDTH // 2
            example_asteroid.y = 450
            example_asteroid.size = 40
            example_asteroid.draw(self.screen)
            
            asteroid_info = instruction_font.render("Сбивайте астероиды, не дайте им вас уничтожить!", True, WHITE)
            self.screen.blit(asteroid_info, (SCREEN_WIDTH//2 - asteroid_info.get_width()//2, 500))
        
        # Сообщение о конце игры
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))  # Полупрозрачный черный
            self.screen.blit(overlay, (0, 0))
            
            game_over_font = pygame.font.SysFont(None, 72)
            game_over_text = game_over_font.render("ИГРА ОКОНЧЕНА", True, RED)
            self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 200))
            
            final_score_text = self.font.render(f"Ваш счет: {self.score}", True, YELLOW)
            self.screen.blit(final_score_text, (SCREEN_WIDTH//2 - final_score_text.get_width()//2, 300))
            
            restart_text = self.font.render("Нажмите ПРОБЕЛ для новой игры", True, GREEN)
            self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, 400))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# Запуск игры
if __name__ == "__main__":
    game = Game()
    game.run()
