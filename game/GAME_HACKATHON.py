from pygame import *
import os

init()        
font.init()   

class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y):
        sprite.Sprite.__init__(self)
        self.image_normal = transform.scale(image.load(player_image), (size_x, size_y))
        self.image = self.image_normal
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
    
    def update(self, mouse_pos, player_image_hover, size_x, size_y):
        if self.rect.collidepoint(mouse_pos):
            self.image_hover = transform.scale(image.load(player_image_hover), (size_x, size_y))
            self.image = self.image_hover 
        else:
            self.image = self.image_normal

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_x_speed, player_y_speed):
        GameSprite.__init__(self, player_image, player_x, player_y, size_x, size_y)
        self.x_speed = player_x_speed
        self.y_speed = player_y_speed

        # Стандартне зображення
        self.image_idle = self.image_normal

        # Анімація вправо
        self.image_walk_r1 = transform.scale(image.load('Harry_walk1.png'), (size_x, size_y))
        self.image_walk_r2 = transform.scale(image.load('Harry_walk2.png'), (size_x, size_y))
        self.walk_images_right = [self.image_walk_r1, self.image_walk_r2]

        # Анімація вліво (віддзеркалені зображення)
        self.image_walk_l1 = transform.flip(self.image_walk_r1, True, False)
        self.image_walk_l2 = transform.flip(self.image_walk_r2, True, False)
        self.walk_images_left = [self.image_walk_l1, self.image_walk_l2]

        self.walk_index = 0
        self.walk_counter = 0
        self.facing = "right"  # напрямок руху

    def update(self, barriers): 
        moving = False

        if self.x_speed < 0:
            self.facing = "left"
        elif self.x_speed > 0:
            self.facing = "right"

        if self.rect.x <= win_width - 60 and self.x_speed > 0 or self.rect.x >= 0 and self.x_speed < 0:
            self.rect.x += self.x_speed
            moving = True

        platforms_touched = sprite.spritecollide(self, barriers, False)
        if self.x_speed > 0:
            for p in platforms_touched:
                self.rect.right = min(self.rect.right, p.rect.left) 
        elif self.x_speed < 0:
            for p in platforms_touched:
                self.rect.left = max(self.rect.left, p.rect.right)

        if self.rect.y <= win_height - 60 and self.y_speed > 0 or self.rect.y >= 0 and self.y_speed < 0:
            self.rect.y += self.y_speed
            moving = True

        platforms_touched = sprite.spritecollide(self, barriers, False)
        if self.y_speed > 0:
            for p in platforms_touched:
                self.rect.bottom = min(self.rect.bottom, p.rect.top) 
        elif self.y_speed < 0:
            for p in platforms_touched:
                self.rect.top = max(self.rect.top, p.rect.bottom)

        # Анімація
        if moving:
            self.walk_counter += 1
            if self.walk_counter >= 10:
                self.walk_counter = 0
                self.walk_index = (self.walk_index + 1) % 2
            if self.facing == "right":
                self.image = self.walk_images_right[self.walk_index]
            else:
                self.image = self.walk_images_left[self.walk_index]
        else:
            self.image = self.image_idle

    def fire(self):
        global bullets

        if self.facing == "right":
            bullet_x = self.rect.centerx # край справа
            bullet_y = self.rect.y + self.rect.height - 30  # трохи нижче центру
        else:
            bullet_x = self.rect.centerx  # край зліва (і відступ щоб не з'являлась всередині)
            bullet_y = self.rect.y + self.rect.height - 30

        bullet = Bullet('bullet.png', bullet_x, bullet_y, 50, 15, 30 if self.facing == "right" else -15)
        bullets.add(bullet)


class Enemy_h(GameSprite):
    side = "left"
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed, x1, x2):
        GameSprite.__init__(self, player_image, player_x, player_y, size_x, size_y)
        self.speed = player_speed
        self.x1 = x1
        self.x2 = x2

    def update(self):
        if self.rect.x <= self.x1: 
            self.side = "right"
        if self.rect.x >= self.x2:
            self.side = "left"
        if self.side == "left":
            self.rect.x -= self.speed
        else:
            self.rect.x += self.speed

class Enemy_v(GameSprite):
    side = "up"
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed, y1, y2):
        GameSprite.__init__(self, player_image, player_x, player_y, size_x, size_y)
        self.speed = player_speed
        self.y1 =y1
        self.y2 =y2

    def update(self):
        if self.rect.y <= self.y1: 
            self.side = "down"
        if self.rect.y >= self.y2:
            self.side = "up"
        if self.side == "up":
            self.rect.y -= self.speed
        else:
            self.rect.y += self.speed

class Voldemort(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, move_speed, move_range_up, move_range_down, fire_interval):
        GameSprite.__init__(self, player_image, player_x, player_y, size_x, size_y)
        self.move_speed = move_speed
        self.move_range_up = move_range_up
        self.move_range_down = move_range_down
        self.fire_interval = fire_interval
        self.fire_timer = 0
        self.moving_down = True # Початковий напрямок

    def update(self):
        # Вертикальний рух Волдеморта
        if self.moving_down:
            self.rect.y += self.move_speed
            if self.rect.y >= self.move_range_down:
                self.moving_down = False
        else:
            self.rect.y -= self.move_speed
            if self.rect.y <= self.move_range_up:
                self.moving_down = True

        # Стрільба Волдеморта
        self.fire_timer += 1
        if self.fire_timer >= self.fire_interval:
            self.fire()
            self.fire_timer = 0

    def fire(self):
        global voldemort_bullets
        # Напрямок пострілу
        bullet_speed = 30
        bullet = Bullet('Voldemort_bullet.png', self.rect.centerx - 20, self.rect.centery, 50, 15, bullet_speed)
        voldemort_bullets.add(bullet)
        
class Bullet(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        GameSprite.__init__(self, player_image, player_x, player_y, size_x, size_y)
        self.speed = player_speed

    def update(self):
        self.rect.x += self.speed
        if self.rect.x > win_width + 10 or self.rect.x < -10:
            self.kill()

# Клас кнопки
class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = Rect(x, y, width, height)
        self.color = (150, 111, 51)
        self.hover_color = (200, 160, 100)
        self.text = text
        self.action = action
        self.font = font.Font(None, 60)

    def draw(self, surface):
        mouse_pos = mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            draw.rect(surface, self.hover_color, self.rect)
        else:
            draw.rect(surface, self.color, self.rect)
        text_render = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_render.get_rect(center=self.rect.center)
        surface.blit(text_render, text_rect)

    def is_clicked(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()

# Слайдер для гучності
class Slider:
    def __init__(self, x, y, width, min_val, max_val, start_val):
        self.rect = Rect(x, y, width, 10)
        self.min = min_val
        self.max = max_val
        self.value = start_val
        self.knob_x = x + int((start_val - min_val) / (max_val - min_val) * width)
        self.dragging = False

    def draw(self, surface):
        draw.rect(surface, (180, 180, 180), self.rect)
        draw.circle(surface, (255, 100, 100), (self.knob_x, self.rect.centery), 10)

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if abs(event.pos[0] - self.knob_x) <= 10 and abs(event.pos[1] - self.rect.centery) <= 10:
                self.dragging = True
        elif event.type == MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == MOUSEMOTION:
            if self.dragging:
                self.knob_x = max(self.rect.left, min(event.pos[0], self.rect.right))
                self.value = self.min + (self.knob_x - self.rect.left) / self.rect.width * (self.max - self.min)
                mixer.music.set_volume(self.value / 100)

class TextButton:
    def __init__(self, text, x, y, font, color=(255,255,255), hover_color=(255,215,0)):
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.rendered = self.font.render(self.text, True, self.color)
        self.rect = self.rendered.get_rect(topleft=(x, y))

    def draw(self, surface, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            rendered = self.font.render(self.text, True, self.hover_color)
        else:
            rendered = self.font.render(self.text, True, self.color)
        surface.blit(rendered, self.rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

def fade(screen, width, height):
    fade_surface = Surface((width, height))
    fade_surface.fill((0, 0, 0))
    for alpha in range(0, 255, 5):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        display.update()
        time.delay(30)

def save_progress(amount):
    with open("save.txt", "w") as f:
        f.write(str(amount))

def load_progress():
    if os.path.exists("save.txt"):
        with open("save.txt", "r") as f:
            return int(f.read())
    return 0

win_width = 1500
win_height = 750
window = display.set_mode((win_width, win_height))
display.set_caption("Harry Potter Adventure")

# Стан гри
in_main_menu = True
in_volume_settings = False
in_help = False
in_pause_menu = False
show_slideshow = False # Новий стан для слайдшоу
slideshow_images = []
current_slide = 0
slideshow_timer = 0
SLIDESHOW_DURATION = 150 # Кількість кадрів для показу одного слайду

# Дії для кнопок
def start_game():
    global in_main_menu, a, paused_game, current_level, num, amount, finish
    in_main_menu = False
    paused_game = False
    current_level = 1
    a = "lvl1"
    num = 0
    amount = 0
    finish = False

    # Скидаємо бонуси й монстрів
    bonus.empty()
    bonus.add(GameSprite("horcrux_1.png", 200, 300, 40, 40))
    bonus.add(GameSprite("horcrux_2.png", 600, 50, 40, 40))
    bonus.add(GameSprite("horcrux_3.png", 850, 50, 40, 40))
    bonus.add(GameSprite("horcrux_4.png", 850, 700, 40, 40))
    bonus.add(GameSprite("horcrux_5.png", 1400, 550, 40, 40))

    monsters.empty()
    monsters.add(monster1, monster2, monster3, monster4, monster5, monster6)

    # Повертаємо героя на старт
    hero.rect.x = 5
    hero.rect.y = win_height - 80
    hero.x_speed = 0
    hero.y_speed = 0

    mixer.music.stop()
    mixer.music.load("Statues.mp3")
    mixer.music.play(-1)

    refresh_menu_buttons()

def open_help():
    global in_help
    in_help = True

def back_to_menu():
    global in_help
    in_help = False

def exit_game():
    quit()

def open_volume_settings():
    global in_volume_settings
    in_volume_settings = True

def close_volume_settings():
    global in_volume_settings
    in_volume_settings = False

def resume_game():
    global in_main_menu, a, paused_game
    in_main_menu = False
    a = paused_level
    paused_game = False

# Кнопки меню
buttons = []

def refresh_menu_buttons():
    buttons.clear()
    if paused_game:
        buttons.append(Button(600, 550, 320, 60, "ПРОДОВЖИТИ", resume_game))
    buttons.append(Button(200, 500, 320, 60, "НОВА ГРА", start_game))
    buttons.append(Button(200, 600, 320, 60, "ДОПОМОГА", open_help))
    buttons.append(Button(980, 500, 320, 60, "ЗВУК", open_volume_settings))
    buttons.append(Button(980, 600, 320, 60, "ВИХІД", exit_game))

paused_game = False
paused_level = "lvl1"

refresh_menu_buttons()

back_button = Button(600, 600, 300, 60, "Назад", back_to_menu)
volume_back_button = Button(600, 600, 300, 60, "Назад", close_volume_settings)

back_m = transform.scale(image.load("Main_menu.png"), (win_width, win_height))
font.init()

def draw_slider():
    volume_slider.draw(window)

mixer.init()
mixer.music.load("Statues.mp3")
mixer.music.set_volume(0.02)
mixer.music.play(-1)
lose = mixer.Sound("lose.wav")
lose.set_volume(0.02)
win = mixer.Sound("win.wav")
win.set_volume(0.02)

# Повзунок гучності
volume_slider = Slider(600, 400, 300, 0, 100, int(mixer.music.get_volume() * 100))
volume_handle = Rect(1000 + int(200 * mixer.music.get_volume()), 595, 10, 20)
sliding = False

total_amount = load_progress()

############## 1 lvl #####################
amount = 0

back = transform.scale(image.load("forest.jpg"), (win_width, win_height))
bullets = sprite.Group()
barriers = sprite.Group()
monsters = sprite.Group()

#Створюємо групу для бонусів
bonus = sprite.Group()
bonus.add(GameSprite("horcrux_1.png", 200, 300, 40, 40))
bonus.add(GameSprite("horcrux_2.png", 600, 50, 40, 40))
bonus.add(GameSprite("horcrux_3.png", 850, 50, 40, 40))
bonus.add(GameSprite("horcrux_4.png", 850, 700, 40, 40))
bonus.add(GameSprite("horcrux_5.png", 1400, 550, 40, 40))
num = 0 #Лічильник бонусів

# Список для вертикальних стін (x, y)
vertical_walls = [
    (100, 700), (100, 650), (100, 600), (100, 450), (100, 400), (100, 350),
    (100, 300), (100, 250), (100, 200), (100, 50), (100, 0), 
    (260, 150), (260, 100), (260, 200), (260, 250), (260, 300), (260, 350), 
    (260, 400), (260, 450), (340, 500), (340, 550), (340, 600), 
    (660, 50), (660, 0), (660, 350), (660, 400), (660, 450), (660, 500), 
    (660, 550), (660, 600), (940, 600), (940, 650), (940, 700),
    (1020, 600), (1100, 600), (1100, 550), (1100, 500), (1100, 450),
    (780, 400), (780, 250), (780, 200), (780, 150), (780, 100),
    (1260, 550), (1260, 500), (1260, 450), (900, 350), (900, 300),
    (900, 250), (1020, 200), (1020, 150), (1020, 100), (900, 50), (900, 0)
]

# Створюємо вертикальні стіни через цикл
for idx, (x, y) in enumerate(vertical_walls, 1):
    barrier = GameSprite('tree_wall.png', x, y, 40, 50)
    barriers.add(barrier)

# Список для горизонтальних стін (x, y)
horizontal_walls = [
    (140, 200), (180, 200), (220, 200), (260, 200), (300, 100), (340, 100),
    (380, 100), (300, 450), (340, 450), (300, 600), (260, 600), 
    (300, 300), (340, 300), (380, 300), (420, 300), (460, 300), 
    (500, 300), (540, 300), (580, 300), (620, 300), (660, 300),
    (500, 100), (540, 100), (580, 100), (620, 100), (660, 100),
    (500, 700), (500, 650), (500, 600), (500, 550), (500, 500),
    (500, 450), (700, 600), (740, 600), (780, 600), (820, 600),
    (1060, 450), (1020, 450), (980, 450), (940, 450), (900, 450),
    (860, 450), (820, 450), (780, 450), (820, 100), (860, 100),
    (900, 100), (1260, 600), (1300, 600), (1340, 600), (1380, 600),
    (1420, 600), (1460, 600), (1500, 600), (940, 250), (980, 250),
    (1020, 250), (1140, 250), (1180, 250), (1220, 250), (1260, 250),
    (1300, 250), (1340, 250), (1380, 250), (1420, 250), (1460, 250),
    (1500, 250), (1060, 100), (1100, 100), (1140, 100), (1180, 100),
    (1220, 100), (1260, 100), (1300, 100), (1420, 100), (1460, 100),
    (1500, 100)
]

# Створюємо горизонтальні стіни через цикл
for idx, (x, y) in enumerate(horizontal_walls, 1):
    barrier = GameSprite('tree_wall.png', x, y, 40, 50)
    barriers.add(barrier)


hero = Player('Harry_Potter.png', 5, win_height - 80, 60, 60, 0, 0)
final_sprite = GameSprite('snich.png', 1400, 680, 25, 25)

monster1 = Enemy_v('Dementor.png', 700, 200, 80, 80, 10, 200, 400)
monster2 = Enemy_v('Dementor.png', 160, 350, 80, 80, 10, 350, 600)
monster3 = Enemy_h('Dementor.png', 400, 220, 80, 80, 10, 400, 600)
monster4 = Enemy_h('Dementor.png', 0, 120, 80, 80, 10, 0, 200)
monster5 = Enemy_h('Dementor.png', 320, 370, 80, 80, 10, 320, 600)
monster6 = Enemy_h('Dementor.png', 1000, 370, 80, 80, 10, 1000, 1400)

monsters.add(monster1)
monsters.add(monster2)
monsters.add(monster3)
monsters.add(monster4)
monsters.add(monster5)
monsters.add(monster6)

############## 2 lvl #####################
amount_2 = 0

back_2 = transform.scale(image.load("Hogwarts.png"), (win_width, win_height))
barriers_2 = sprite.Group()
monsters_2 = sprite.Group()

hero_2 = Player('Harry_Potter.png', 1300, 400, 80, 80, 0, 0)

voldemort = Voldemort('Voldemort.png', 50, 400, 80, 80, 5, 200, 600, 40)
monsters_2.add(voldemort)
voldemort_bullets = sprite.Group()

finish = False
run = True
paused_game = False
paused_level = None  # Щоб памʼятати, де зупинилися: lvl1 чи lvl2

a = "menu"
music = "on"

while run:
    mouse_pos = mouse.get_pos()
    
    for e in event.get():
        if e.type == QUIT:
            run = False

        # --- Обробка подій у меню ---
        if a == "menu":
            if in_help:
                back_button.is_clicked(e)
            elif in_volume_settings:
                volume_slider.handle_event(e)
                volume_back_button.is_clicked(e)
            else:
                for btn in buttons:
                    btn.is_clicked(e)

        # --- Обробка рухів у грі ---
        if a == "lvl1":
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    paused_game = True
                    paused_level = a  # запам’ятати рівень
                    a = "menu"
                    in_main_menu = True
                    refresh_menu_buttons()
                elif e.key == K_LEFT:
                    hero.x_speed = -5
                elif e.key == K_RIGHT:
                    hero.x_speed = 5
                elif e.key == K_UP:
                    hero.y_speed = -5
                elif e.key == K_DOWN:
                    hero.y_speed = 5
                elif e.key == K_SPACE:
                    hero.fire()

            elif e.type == KEYUP:
                if e.key in [K_LEFT, K_RIGHT]:
                    hero.x_speed = 0
                elif e.key in [K_UP, K_DOWN]:
                    hero.y_speed = 0

    
            


        if a == "lvl2":
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    paused_game = True
                    paused_level = a  # запам’ятати рівень
                    a = "menu"
                    in_main_menu = True
                    refresh_menu_buttons()
                elif e.key == K_LEFT:
                    hero_2.x_speed = -5
                elif e.key == K_RIGHT:
                    hero_2.x_speed = 5
                elif e.key == K_UP:
                    hero_2.y_speed = -5
                elif e.key == K_DOWN:
                    hero_2.y_speed = 5
                elif e.key == K_SPACE:
                    hero_2.fire()

            elif e.type == KEYUP:
                if e.key in [K_LEFT, K_RIGHT]:
                    hero_2.x_speed = 0
                elif e.key in [K_UP, K_DOWN]:
                    hero_2.y_speed = 0


            

    # === Відображення головного меню ===
    if a == "menu":
        window.blit(back_m, (0, 0))

        if in_help:
            help_font = font.Font(None, 28)

            # Координати для блоків
            x_left = 50      # Ліва частина екрана
            x_right = 950     # Права частина екрана
            y_top = 250       # Верхній відступ
            spacing = 30      # Відступ між рядками

            # 1. Управління персонажем
            control_text = [
                "Управління персонажем:",
                "Стрілка вгору — рух угору",
                "Стрілка вниз — рух донизу",
                "Стрілка вниз — рух вліво",
                "Стрілка вправо — рух вправо",
                "Пробіл (Space) — постріл"
            ]

            # 2. Головне меню
            menu_text = [
                "Головне меню:",
                "Нова гра — почати з початку",
                "Продовжити — повернення з моменту паузи",
                "Звук — змінити гучність музики",
                "Вийти — вийти з гри",
                "Esc — меню під час гри"
            ]

            # 3. Мета гри
            goal_text = [
                "Мета гри:",
                "Пройти всі рівні, уникаючи дементорів та вбий Волдеморта!"
            ]

            # 4. Рівень 1 та 2
            levels_text = [
                "Рівень 1:",
                "Знищіть 5 горокраксів, доторкнувшись до них",
                "",
                "Рівень 2:",
                "Переможіть Волдеморта, уникаючи його атак"
            ]

            # Виведення кожного блоку:
            # Block 1: Управління персонажем
            for i, line in enumerate(control_text):
                rendered = help_font.render(line, True, (255, 255, 255))
                window.blit(rendered, (x_left, y_top + i * spacing))

            # Block 2: Головне меню
            for i, line in enumerate(menu_text):
                rendered = help_font.render(line, True, (255, 255, 255))
                window.blit(rendered, (x_right, y_top + i * spacing))

            # Block 3: Мета гри
            goal_y_start = y_top + len(control_text) * spacing + 50
            for i, line in enumerate(goal_text):
                rendered = help_font.render(line, True, (255, 255, 255))
                window.blit(rendered, (x_left, goal_y_start + i * spacing))

            # Block 4: Рівні
            levels_y_start = y_top + len(menu_text) * spacing + 50
            for i, line in enumerate(levels_text):
                rendered = help_font.render(line, True, (255, 255, 255))
                window.blit(rendered, (x_right, levels_y_start + i * spacing))

            back_button.draw(window)

        elif in_volume_settings:
            help_font = font.Font(None, 40)
            text = help_font.render("Гучнiсть: " + str(int(volume_slider.value)) + "%", True, (255, 255, 255))
            window.blit(text, (630, 300))
            volume_slider.draw(window)
            volume_back_button.draw(window)
        
        else:
            for btn in buttons:
                btn.draw(window)

    # === Перший рівень ===
    elif a == "lvl1":
        if not finish:
            window.blit(back, (0, 0))

            hero.update(barriers)
            hero.reset()
            bullets.update()
            bullets.draw(window)
            barriers.draw(window)
            bonus.draw(window)
            final_sprite.reset()

            monsters.update()
            monsters.draw(window)

            collected = sprite.spritecollide(hero, bonus, True)
            if collected:
                num += len(collected)


            sprite.groupcollide(monsters, bullets, True, True)
            sprite.groupcollide(bullets, barriers, True, False)

            if sprite.spritecollide(hero, monsters, False):
                finish = True
                mixer.music.stop()
                lose.play()
                img = image.load("loser.jpg")
                window.blit(transform.scale(img, (win_width, win_height)), (0, 0))
            if sprite.collide_rect(hero, final_sprite) and num >= 5:
                fade(window, win_width, win_height)
                a = "pause"
        
    # === Пауза між рівнями ===
    elif a == "pause":
        window.blit(back_m, (0, 0))
        a = "lvl2"

    # === Другий рівень ===
    elif a == "lvl2":
        if not finish:
            window.blit(back_2, (0, 0))

            hero_2.update(barriers_2)
            hero_2.reset()
            bullets.update()
            bullets.draw(window)
            barriers_2.draw(window)

            monsters_2.update()
            monsters_2.draw(window)

            # Оновлення та відображення пострілів Волдеморта
            voldemort_bullets.update()
            voldemort_bullets.draw(window)

            sprite.groupcollide(monsters_2, bullets, True, True)
            sprite.groupcollide(bullets, barriers_2, True, False)
            sprite.groupcollide(voldemort_bullets, barriers_2, True, False) # Щоб кулі Волдеморта теж могли врізатися в стіни

            if sprite.spritecollide(hero_2, monsters_2, False) or sprite.spritecollide(hero_2, voldemort_bullets, False):
                finish = True
                mixer.music.stop()
                lose.play()
                img = image.load("loser.jpg")
                window.blit(transform.scale(img, (win_width, win_height)), (0, 0))
            if not monsters_2: # Перевіряємо, чи група монстрів (включаючи Волдеморта) порожня
                finish = True
                mixer.music.stop()
                win.play()
                img = image.load("winner.png")
                window.blit(transform.scale(img, (win_width, win_height)), (0, 0))
    
    display.update()
    time.delay(20)
