import pygame
import sys
import torch
import torch.nn as nn
import random


#sql

pygame.init()
city_weather_data = {
    "Rize": (18, 85, 10),
    "Adana": (39, 20, 5),
    "Antalya": (31, 45, 15),
    "Trabzon": (18, 50, 8),
    "Mersin": (34, 50, 12),
}
city_fruit_data = {
    "Rize": "Kestane",
    "Adana": "Portakal",
    "Antalya": "Muz",
    "Trabzon": "Fındık",
    "Mersin": "Limon"
}

font = pygame.font.SysFont(None, 40)
cities = ["Rize", "Adana", "Antalya", "Trabzon", "Mersin"]
selected_animal_area = None
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 750
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Farm Game")

clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

from username_input_screen import UsernameInputScreen
input_screen = UsernameInputScreen(screen)
username = input_screen.run()
print("Welcome,", username)




background = pygame.image.load("background.png")
market = pygame.image.load('market.png')
cow_img_right = pygame.image.load('cow_right.png')
cow_img_left = pygame.image.load('cow_left.png')
chicken_img_right = pygame.image.load('chicken_right.png')
chicken_img_left = pygame.image.load('chicken_left.png')
profile_icon = pygame.image.load('farmer.png')
tractor_img_right = pygame.image.load('tractor_right.png')
tractor_img_left = pygame.image.load('tractor_left.png')
tractor_img = tractor_img_right
cow_area_img = pygame.image.load('cow_area.png')
chicken_area_img = pygame.image.load('chicken_area.png')
envanter_img=pygame.image.load("envanter.png")
peas_img=pygame.image.load('peasant.png')
peas_x=-peas_img.get_width()
peas_y=SCREEN_HEIGHT-peas_img.get_height()-20
peas_speed=2


fruit_images = {
    "Kestane": pygame.image.load("tree.png"),
    "Portakal": pygame.image.load("tree.png"),
    "Muz": pygame.image.load("t.png"),
    "Fındık": pygame.image.load("tree.png"),
    "Limon": pygame.image.load("tree.png")
}
fruit_images1 = {
    "Kestane": pygame.image.load("k.png"),
    "Portakal": pygame.image.load("p.png"),
    "Muz": pygame.image.load("b.png"),
    "Fındık": pygame.image.load("f.png"),
    "Limon": pygame.image.load("le.png")
}
crop_images = [
    pygame.image.load("crop_stage0.png"),
    pygame.image.load("crop_stage1.png"),
    pygame.image.load("crop_stage2.png")
]

inventory= {}


background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

def apply_weather_overlay(surface, weather):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    if weather == "Bulutlu":
        for pos in cloud_positions:
            surface.blit(cloud_image, pos)

    if weather == "Güneşli":
        overlay.fill((255, 223, 0, 80))

    elif weather == "Yağmurlu":
        overlay.fill((30, 30, 120, 200))
    elif weather == "Bulutlu":
        overlay.fill((180, 180, 180, 180))
    elif weather == "Kurak":
        overlay.fill((255, 140, 0, 180))
    surface.blit(overlay, (0, 0))



    if weather == "Güneşli":
        light_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(light_overlay, (255, 255, 240, 180), (850, 100), 70)
        surface.blit(light_overlay, (0, 0))


market_rect = market.get_rect(topleft=(1190, 10))
profile_rect = profile_icon.get_rect(topleft=(20, SCREEN_HEIGHT - 120))
tractor_rect = tractor_img.get_rect(topleft=(500, 600))
cow_area_rect = cow_area_img.get_rect(topleft=(3, 50))
chicken_area_rect = chicken_area_img.get_rect(topleft=(530, 50))
cow_pos = [cow_area_rect.x +10, cow_area_rect.y+20 ]
chicken_pos = [chicken_area_rect.x+10 , chicken_area_rect.y+10 ]
cloud_image = pygame.image.load("cloudy.png").convert_alpha()
cloud_positions = [[random.randint(0, SCREEN_WIDTH), random.randint(0, 0)] for _ in range(4)]


cow_speed = [random.choice([-0.5, 0.5]), random.choice([-0.5, 0.5])]
chicken_speed = [random.choice([-0.5, 0.5]), random.choice([-0.5, 0.5])]

dragging_cow_area =False
dragging_chicken_area =False
dragging_market = False
show_dialogue=False

offset_x = 0
offset_y = 0


show_profile = False
show_market_content = False
show_cow_content = False
show_chicken_content = False
show_inventory = False

player_money=0
player_level = 0


#font = pygame.font.SysFont(None, 24)

class WeatherNet(nn.Module):
    def __init__(self):
        super(WeatherNet, self).__init__()
        self.fc1 = nn.Linear(3, 16)
        self.fc2 = nn.Linear(16, 4)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        return self.fc2(x)

model = WeatherNet()

def generate_data():
    X, y = [], []

    for _ in range(75):

        temp = random.uniform(10, 22)
        humidity = random.uniform(75, 100)
        wind = random.uniform(0, 15)
        X.append([temp, humidity, wind])
        y.append(1)  # Yağmurlu


        temp = random.uniform(36, 45)
        humidity = random.uniform(10, 25)
        wind = random.uniform(0, 15)
        X.append([temp, humidity, wind])
        y.append(2)  # Kurak


        temp = random.uniform(28, 35)
        humidity = random.uniform(30, 60)
        wind = random.uniform(0, 15)
        X.append([temp, humidity, wind])
        y.append(0)


        temp = random.uniform(15, 27)
        humidity = random.uniform(40, 70)
        wind = random.uniform(0, 15)
        X.append([temp, humidity, wind])
        y.append(3)

    return torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.long)

X, y = generate_data()
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

for epoch in range(100):
    out = model(X)
    loss = criterion(out, y)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

def predict_weather(temp, humidity, wind):
    input_tensor = torch.tensor([[temp, humidity, wind]], dtype=torch.float32)
    with torch.no_grad():
        output = model(input_tensor)
        pred = torch.argmax(output, dim=1).item()
    durumlar = ['Güneşli', 'Yağmurlu', 'Kurak', 'Bulutlu']
    return durumlar[pred]

def select_city_screen():
        selected_city = None
        while True:
            screen.fill((200, 220, 255))
            title = font.render("Bir şehir seçin (1-5):", True, (0, 0, 0))
            screen.blit(title, (250, 50))

            for i, city in enumerate(cities):
                text = font.render(f"{i + 1}. {city}", True, (0, 0, 0))
                screen.blit(text, (300, 150 + i * 50))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    # Klavyeden 1-5 arası tuşa basıldıysa
                    if pygame.K_1 <= event.key <= pygame.K_1 + len(cities) - 1:
                        index = event.key - pygame.K_1
                        selected_city = cities[index]
                        return selected_city

selected_city = select_city_screen()
print("Seçilen şehir:", selected_city)
temp, humidity, wind = city_weather_data[selected_city]
weather_status = predict_weather(temp, humidity, wind)
print("Tahmin edilen hava durumu:", weather_status)


tropik_fruit = city_fruit_data[selected_city]

class RainEffect:
    def __init__(self):
        self.drops = [[random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)] for _ in range(100)]

    def update(self):
        for drop in self.drops:
            drop[1] += 5
            if drop[1] > SCREEN_HEIGHT:
                drop[1] = 0
                drop[0] = random.randint(0, SCREEN_WIDTH)

    def draw(self, surface):
        for drop in self.drops:
            pygame.draw.line(surface, (180, 180, 255), (drop[0], drop[1]), (drop[0], drop[1]+5), 1)


class Crop:
    def __init__(self, position):
        self.position = position
        self.stage = 0
        self.timer = 0
        self.rect = pygame.Rect(position[0], position[1], 32, 32)



        self.images = [
            pygame.image.load("crop_stage0.png"),
            pygame.image.load("crop_stage1.png"),
            pygame.image.load("crop_stage2.png"),
        ]

    def update(self, weather):
        self.timer += 1
        speed = 1
        if weather == 'Yağmurlu':
            speed = 2
        elif weather == 'Kurak':
            speed = 0.3


        if self.timer > 300 / speed and self.stage < 2:
            self.stage += 1
            self.timer = 0

    def draw(self, screen):
        screen.blit(self.images[self.stage], self.position)

    def is_ready_to_harvest(self):
        return self.stage == 2


crops = []




def draw_sell_button():
    pygame.draw.rect(screen, (0, 200, 0), (market_rect.x-60, market_rect.y+20, 100, 40))  # yeşil buton
    text = font.render("Sat", True, WHITE)
    screen.blit(text, (market_rect.x-30, market_rect.y+30))

player_money1=0

def sell_items():
    global player_money
    global player_money1
    eggs = inventory.get("Yumurta",0)
    milk = inventory.get("Süt", 0)
    bugdays=inventory.get("Buğday", 0)
    tropics=inventory.get(tropik_fruit,0)

    egg_price = 5
    milk_price = 10
    bugday_price=100
    tropics_price=20



    earned = eggs * egg_price + milk * milk_price+bugday_price*bugdays+tropics*tropics_price
    player_money1=player_money1+earned
    player_money =player_money+ earned
    print(f"Satış yapıldı! Kazanç: {earned}, Toplam Para: {player_money}")
    if inventory.get("Yumurta", 0) > 0:
        inventory["Yumurta"] = 0
    if inventory.get("Süt", 0) > 0:
        inventory["Süt"] = 0
    if inventory.get("Buğday", 0) > 0:
        inventory["Buğday"]=0
    if inventory.get(tropik_fruit,0)>0:
        inventory[tropik_fruit]=0


class DustParticle:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.alpha = random.randint(100, 200)

    def update(self):
        self.x += random.choice([-1, 0, 1])
        self.y += random.choice([-1, 0, 1])
        if self.x < 0: self.x = SCREEN_WIDTH
        if self.x > SCREEN_WIDTH: self.x = 0
        if self.y < 0: self.y = SCREEN_HEIGHT
        if self.y > SCREEN_HEIGHT: self.y = 0

    def draw(self, surface):
        pygame.draw.circle(surface, (230, 210, 140, self.alpha), (int(self.x), int(self.y)), 2)

dust_particles = [DustParticle() for _ in range(80)]

class FruitTree:
    def __init__(self, rect, fruit_name):
        self.rect = rect
        self.fruit_icon = fruit_images1[fruit_name]
        self.fruits = []
        self.last_spawn_time = 0
        self.spawn_interval = 5000
        self.max_fruits_per_wave = 5

    def spawn_fruits(self):
        self.fruits = []

        spacing = self.rect.width // 3
        y_variation = self.rect.height // 3

        used_positions = []

        for i in range(self.max_fruits_per_wave):
            # X konumlarını dağınık tut
            base_x = self.rect.left + random.randint(10, self.rect.width - self.fruit_icon.get_width() - 10)
            base_y = self.rect.top + random.randint(10, self.rect.height - self.fruit_icon.get_height() - 10)

            # Üst üste gelmesin diye tekrar dene
            fruit_rect = self.fruit_icon.get_rect(topleft=(base_x, base_y))
            attempts = 0
            while any(fruit_rect.colliderect(r) for r, v in self.fruits if v) and attempts < 50:
                base_x = self.rect.left + random.randint(10, self.rect.width - self.fruit_icon.get_width() - 10)
                base_y = self.rect.top + random.randint(10, self.rect.height - self.fruit_icon.get_height() - 10)
                fruit_rect.topleft = (base_x, base_y)
                attempts += 1

            self.fruits.append((fruit_rect, True))

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_spawn_time >= self.spawn_interval:
            self.spawn_fruits()
            self.last_spawn_time = now

    def draw(self, surface):
        for fruit_rect, visible in self.fruits:
            if visible:
                surface.blit(self.fruit_icon, fruit_rect.topleft)

    def check_click(self, mouse_pos):
        global player_money
        for i, (fruit_rect, visible) in enumerate(self.fruits):
            if visible and fruit_rect.collidepoint(mouse_pos):
                self.fruits[i] = (fruit_rect, False)
                inventory[tropik_fruit] = inventory.get(tropik_fruit, 0) + 1
                print(f"{tropik_fruit} toplandı! Envanter: {inventory}")
                return True
        return False

def draw_money_and_level():
    player_level = player_money1 // 100
    money_text = font.render(f"Para: {player_money}", True, BLACK)
    level_text = font.render(f"Seviye: {player_level}", True, BLACK)
    screen.blit(money_text, (120, 60))
    screen.blit(level_text, (120, 80))


def draw_inventory():
    pygame.draw.rect(screen, WHITE, (100, 100, 400, 400))
    pygame.draw.rect(screen, BLACK, (100, 100, 400, 400), 2)
    y_offset = 120

    for item, count in inventory.items():
        if(count>0):

            text = font.render(f"{item}: {count}", True, BLACK)
            screen.blit(text, (120, y_offset))
            y_offset += 40
    draw_money_and_level()

fruit_tree_rect = pygame.Rect(1180, 390, 70, 90)
fruit_tree = FruitTree(fruit_tree_rect, tropik_fruit)

class Chicken:
    def __init__(self, offset_position):
        self.image_right = pygame.image.load("chicken_right.jpg")
        self.image_left = pygame.image.load("chicken_left.png")
        self.egg_icon = pygame.image.load("egg.png")
        self.offset = list(offset_position)
        self.speed = [1, 1]
        self.rect = self.image_right.get_rect()
        self.egg_visible = False
        self.egg_rect = None
        self.last_egg_time = pygame.time.get_ticks()

    def update(self, area_rect):
        self.offset[0] += self.speed[0]
        self.offset[1] += self.speed[1]


        if self.offset[0] < 10 or self.offset[0] > area_rect.width - self.rect.width - 10:
            self.speed[0] *= -1
        if self.offset[1] < 10 or self.offset[1] > area_rect.height - self.rect.height - 10:
            self.speed[1] *= -1


        self.rect.topleft = (area_rect.left + self.offset[0], area_rect.top + self.offset[1])


        current_time = pygame.time.get_ticks()
        if not self.egg_visible and current_time - self.last_egg_time >= 5000:
            self.egg_visible = True
            self.egg_rect = self.egg_icon.get_rect(midbottom=(self.rect.centerx, self.rect.top))


        if self.egg_visible and self.egg_rect:
            self.egg_rect.midbottom = (self.rect.centerx, self.rect.top)
    def draw(self, screen):
        if self.speed[0] >= 0:
            image = self.image_right
        else:
            image = self.image_left

        screen.blit(image, self.rect.topleft)
        if self.egg_visible:
            screen.blit(self.egg_icon, self.egg_rect.topleft)

    def check_egg_click(self, mouse_pos):
        if self.egg_visible and self.egg_rect:
            expanded_rect = self.egg_rect.inflate(40, 40)
            if expanded_rect.collidepoint(mouse_pos):
                self.egg_visible = False
                self.last_egg_time = pygame.time.get_ticks()
                return True
        return False
chickens = [
    Chicken((10, 10)),
    Chicken((50, 100))
]


class Cow:
    def __init__(self, cow_area_rect):
        self.image_right = pygame.image.load("cow_right.png")
        self.image_left = pygame.image.load("cow_left.png")
        self.milk_icon = pygame.image.load("milk-bottle.png")
        self.offset = list(cow_area_rect)
        self.speed = [1, 1]
        self.rect = self.image_right.get_rect()
        self.milk_visible = False
        self.milk_rect = None
        self.last_milk_time = pygame.time.get_ticks()

    def update(self, area_rect):
        self.offset[0] += self.speed[0]
        self.offset[1] += self.speed[1]

        if self.offset[0] < 10 or self.offset[0] > area_rect.width - self.rect.width - 10:
            self.speed[0] *= -1
        if self.offset[1] < 10 or self.offset[1] > area_rect.height - self.rect.height - 10:
            self.speed[1] *= -1

        self.rect.topleft = (area_rect.left + self.offset[0], area_rect.top + self.offset[1])

        current_time = pygame.time.get_ticks()
        if not self.milk_visible and current_time - self.last_milk_time >= 5000:
            self.milk_visible = True
            self.milk_rect = self.milk_icon.get_rect(midbottom=(self.rect.centerx, self.rect.top))

        if self.milk_visible and self.milk_rect:
            self.milk_rect.midbottom = (self.rect.centerx, self.rect.top)

    def draw(self, screen):

        if self.speed[0] >= 0:
            image = self.image_right
        else:
            image = self.image_left

        screen.blit(image, self.rect.topleft)
        if self.milk_visible:
            screen.blit(self.milk_icon, self.milk_rect.topleft)

    def check_milk_click(self, mouse_pos):
        if self.milk_visible and self.milk_rect:
            expanded_rect = self.milk_rect.inflate(40, 40)
            if expanded_rect.collidepoint(mouse_pos):
                self.milk_visible = False
                self.last_milk_time = pygame.time.get_ticks()
                return True
        return False

cows = [
    Cow((30, 50)),
    Cow((100, 150))
]
LIGHT_GREY = (200, 200, 200)
font_dialogue = pygame.font.Font(None, 24)
def draw_speech_bubble(surface, text, character_rect, offset_x=0, offset_y=0, padding=10):
    rendered_text = font_dialogue.render(text, True, BLACK)
    text_width, text_height = rendered_text.get_size()
    bubble_width = text_width + 2 * padding
    bubble_height = text_height + 2 * padding
    bubble_x = character_rect.centerx - bubble_width // 2 + offset_x
    bubble_y = character_rect.top - bubble_height - 15 + offset_y
    if bubble_x < 0:
        bubble_x = 0
    if bubble_x + bubble_width > SCREEN_WIDTH:
        bubble_x = SCREEN_WIDTH - bubble_width
    if bubble_y < 0:
        bubble_y = 0
    bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_width, bubble_height)
    pygame.draw.rect(surface, LIGHT_GREY, bubble_rect, border_radius=8)
    pygame.draw.rect(surface, BLACK, bubble_rect, 2, border_radius=8)


    tail_point1 = (character_rect.centerx + offset_x, character_rect.top + offset_y)
    tail_point2 = (bubble_rect.centerx - 10, bubble_rect.bottom)
    tail_point3 = (bubble_rect.centerx + 10, bubble_rect.bottom)
    pygame.draw.polygon(surface, LIGHT_GREY, [tail_point1, tail_point2, tail_point3])
    pygame.draw.polygon(surface, BLACK, [tail_point1, tail_point2, tail_point3], 2)


    text_x = bubble_x + padding
    text_y = bubble_y + padding
    surface.blit(rendered_text, (text_x, text_y))


def draw_market_content():
    pygame.draw.rect(screen, WHITE, (market_rect.x, market_rect.y - 150, 250, 150))
    pygame.draw.rect(screen, BLACK, (market_rect.x, market_rect.y - 150, 250, 150), 2)
    y_offset = market_rect.y - 130
    for item, count in inventory.items():
        text = font.render(f"{item}: {count}", True, BLACK)
        screen.blit(text, (market_rect.x, y_offset))
        y_offset += 40
    if inventory.get("Yumurta", 0) > 0 or inventory.get("Süt", 0) > 0 or inventory.get("Buğday", 0) > 0 or inventory.get(tropik_fruit,0)>0:
        draw_sell_button()


back_sound = pygame.mixer.music.load('farm.wav')
pygame.mixer.music.play(-1)
running = True
start_time = pygame.time.get_ticks()

while running:
    peas_rect = peas_img.get_rect(topleft=(peas_x, peas_y))
    dialogue_text = ""
    if(player_level<1):
        dialogue_text = f"Merhaba {username}! yumurta ve sütleri toplayıp satarak para kazanabilirsin"
    elif player_level==3:
        dialogue_text = "3 level oldun ekim yapabilirsin"
    elif inventory.get("Yumurta", 0) > 0 or inventory.get("Süt", 0) > 0 or inventory.get("Buğday", 0) > 0 or inventory.get(tropik_fruit,0)>0:
        dialogue_text="Ürünlerini satmanda yardımcı olabilirim istersen? \n1-Evet"
    else:
        dialogue_text=f"Harika gidiyorsun şimdiden {player_level}. levele ulaştın"
    dialogue_timer = 0
    DIALOGUE_DURATION = 30000
    screen.blit(fruit_images[tropik_fruit], (1155, 370))
    peas_x+=peas_speed
    if peas_x>SCREEN_WIDTH:
        peas_x=-peas_img.get_width()


    fruit_tree.update()
    fruit_tree.draw(screen)

    rain_effect = RainEffect()
    current_time = pygame.time.get_ticks()

    if current_time - start_time <= 3000:
        font1 = pygame.font.SysFont(None, 48)
        welcome_text = font1.render(f"Welcome, {username}", True, (255, 255, 255))
        screen.blit(welcome_text, (10, 50))


    pygame.display.flip()
    planting_allowed = True
    screen.blit(background, (0, 0))
    apply_weather_overlay(screen, weather_status)

    if weather_status == "Kurak":
        for dust in dust_particles:
            dust.update()
            dust.draw(screen)
    if weather_status == "Yağmurlu":
        rain_effect.update()
        rain_effect.draw(screen)
    screen.blit(fruit_images[tropik_fruit], (1155, 370))
    screen.blit(market, market_rect.topleft)
    if weather_status == "Bulutlu":
        for pos in cloud_positions:
            screen.blit(cloud_image, pos)
            pos[0] -= 0.5
            if pos[0] < -cloud_image.get_width():
                pos[0] = SCREEN_WIDTH
                pos[1] = random.randint(0,1)
    if weather_status == "Kurak":
        for dust in dust_particles:
            dust.update()
            dust.draw(screen)



    cow_img = cow_img_right if cow_speed[0] > 0 else cow_img_left
    chicken_img = chicken_img_right if chicken_speed[0] > 0 else chicken_img_left

    player_level = player_money // 100
    screen.blit(cow_area_img, cow_area_rect.topleft)
    screen.blit(chicken_area_img, chicken_area_rect.topleft)
    screen.blit(profile_icon, profile_rect.topleft)
    screen.blit(peas_img,(peas_x,peas_y))

    for chicken in chickens:
        chicken.update(chicken_area_rect)
        chicken.draw(screen)
    for cow in cows:
        cow.update(cow_area_rect)
        cow.draw(screen)



    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            mouse_x, mouse_y = event.pos
            if market_rect.x-50 <= mouse_x <= market_rect.x+50 and market_rect.y-50 <= mouse_y <= market_rect.y+50:
                sell_items()

            for chicken in chickens:
                if chicken.check_egg_click(mouse_pos):
                    inventory["Yumurta"] = inventory.get("Yumurta", 0) + 1


            for cow in cows:
                if cow.check_milk_click(mouse_pos):
                    inventory["Süt"] = inventory.get("Süt", 0) + 1
        if event.type == pygame.MOUSEBUTTONDOWN:

            if market_rect.collidepoint(event.pos):
                dragging_market = True
                offset_x = market_rect.x - event.pos[0]
                offset_y = market_rect.y - event.pos[1]

            elif cow_area_rect.collidepoint(event.pos):
                dragging_cow_area = True
                offset_x = cow_area_rect.x - event.pos[0]
                offset_y = cow_area_rect.y - event.pos[1]
            elif chicken_area_rect.collidepoint(event.pos):
                dragging_chicken_area = True
                offset_x = chicken_area_rect.x - event.pos[0]
                offset_y = chicken_area_rect.y - event.pos[1]

            elif profile_rect.collidepoint(event.pos):
                show_profile = not show_profile
            if fruit_tree.check_click(event.pos):
                pass


            if planting_allowed and player_level > 2 :
                mouse_x, mouse_y = event.pos
                if not (
                        cow_area_rect.collidepoint((mouse_x, mouse_y)) or
                        chicken_area_rect.collidepoint((mouse_x, mouse_y)) or
                        market_rect.collidepoint((mouse_x, mouse_y))or
                        profile_rect.collidepoint((mouse_x, mouse_y)) or
                        tractor_rect.collidepoint((mouse_x, mouse_y))
                ):
                    crops.append(Crop((mouse_x, mouse_y)))
                    crops.append(Crop(event.pos))
                    player_money -= 50

            else:
               print("Seviye 3 olmadan ekim yapılamaz!")



        elif event.type == pygame.MOUSEBUTTONUP:
            dragging_market = False
            dragging_cow_area = False
            dragging_chicken_area = False


        elif event.type == pygame.MOUSEMOTION:
            if dragging_cow_area:
                dx = (event.pos[0] + offset_x) - cow_area_rect.x
                dy = (event.pos[1] + offset_y) - cow_area_rect.y


                new_rect = cow_area_rect.move(dx, dy)

                if not any(new_rect.colliderect(r) for r in
                           [market_rect, chicken_area_rect, tractor_rect, profile_rect]) and \
                        not any(new_rect.colliderect(crop.rect) for crop in crops):
                    cow_area_rect = new_rect
                    cow_pos[0] += dx
                    cow_pos[1] += dy
                    for cow in cows:
                        cow.update(cow_area_rect)


            elif dragging_chicken_area:
                dx = (event.pos[0] + offset_x) - chicken_area_rect.x
                dy = (event.pos[1] + offset_y) - chicken_area_rect.y


                new_rect = chicken_area_rect.move(dx, dy)

                if not any(
                        new_rect.colliderect(r) for r in [market_rect, cow_area_rect, tractor_rect, profile_rect]) and \
                        not any(new_rect.colliderect(crop.rect) for crop in crops):
                    chicken_area_rect = new_rect
                    chicken_pos[0] += dx
                    chicken_pos[1] += dy
                    for chicken in chickens:
                        chicken.update(chicken_area_rect)

            elif dragging_market:
                dx = (event.pos[0] + offset_x) - market_rect.x
                dy = (event.pos[1] + offset_y) - market_rect.y

                new_rect = market_rect.move(dx, dy)

                if not any(new_rect.colliderect(r) for r in
                           [cow_area_rect, chicken_area_rect, tractor_rect, profile_rect]) and \
                        not any(new_rect.colliderect(crop.rect) for crop in crops):
                    market_rect = new_rect


        elif event.type == pygame.KEYDOWN:
            if show_market_content:
                pygame.draw.rect(screen, WHITE, (market_rect.x, market_rect.y - 150, 250, 150))
                pygame.draw.rect(screen, BLACK, (market_rect.x, market_rect.y - 150, 250, 150), 2)
                y_offset = market_rect.y - 130

                for item, count in inventory.items():

                        text = font.render(f"{item}: {count}", True, BLACK)
                        if (count > 0):
                            screen.blit(text, (market_rect.x+10, y_offset))
                        # y_offset += 40

                draw_money_and_level()


    new_tractor_rect = tractor_rect


    if (not new_tractor_rect.colliderect(market_rect) and
            not new_tractor_rect.colliderect(cow_area_rect) and
            not  new_tractor_rect.colliderect(profile_rect) and
            not new_tractor_rect.colliderect(chicken_area_rect)):
        tractor_rect = new_tractor_rect


    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        new_rect = tractor_rect.move(-5, 0)
        if not any(new_rect.colliderect(r) for r in [market_rect, cow_area_rect, chicken_area_rect]):
            tractor_rect = new_rect
        tractor_img = tractor_img_left
    if keys[pygame.K_RIGHT]:
        new_rect = tractor_rect.move(5, 0)
        if not any(new_rect.colliderect(r) for r in [market_rect, cow_area_rect, chicken_area_rect]):
            tractor_rect = new_rect
        tractor_img = tractor_img_right
    if keys[pygame.K_UP]:
        new_rect = tractor_rect.move( 0,-5)
        if not any(new_rect.colliderect(r) for r in [market_rect, cow_area_rect, chicken_area_rect]):
            tractor_rect = new_rect
        tractor_img =  tractor_img_right
    if keys[pygame.K_DOWN]:
        new_rect = tractor_rect.move(0,5)
        if not any(new_rect.colliderect(r) for r in [market_rect, cow_area_rect, chicken_area_rect]):
            tractor_rect = new_rect
        tractor_img = tractor_img_left
    if keys[pygame.K_SPACE]:
        if show_dialogue:
            if pygame.time.get_ticks() - dialogue_timer > DIALOGUE_DURATION:
                draw_speech_bubble(screen, dialogue_text, peas_rect, offset_x=0, offset_y=0)
                if keys[pygame.K_1]:
                    sell_items()
                elif keys[pygame.K_2]:
                    dialogue_text="Peki"
            else:
                draw_speech_bubble(screen, dialogue_text, peas_rect , offset_x=0, offset_y=0)

        else:

            show_dialogue = True
            dialogue_timer = pygame.time.get_ticks()


    for crop in crops:
        crop.update(weather_status)
        crop.draw(screen)

        if crop.is_ready_to_harvest() and crop.rect.colliderect(tractor_rect):
            inventory["Buğday"] = inventory.get("Buğday", 0) + 1
            crop.stage = 0
            crop.timer = 0

    screen.blit(tractor_img, tractor_rect.topleft)
    if  keys[pygame.K_p]:
        a = player_money // 100
        pygame.draw.rect(screen, WHITE, (profile_rect.x, profile_rect.y - 100, 200, 100))
        pygame.draw.rect(screen, BLACK, (profile_rect.x, profile_rect.y - 100, 200, 100), 2)
        screen.blit(font.render(f"Player:{username}",True,BLACK),(profile_rect.x + 10, profile_rect.y - 120))
        screen.blit(font.render(f"Para: {player_money}₺", True, BLACK), (profile_rect.x + 10, profile_rect.y - 90))
        screen.blit(font.render(f"Seviye: {a}", True, BLACK), (profile_rect.x + 10, profile_rect.y - 60))
        screen.blit(font.render(f"Envanter için 'i'", True, BLACK), (profile_rect.x + 10, profile_rect.y - 30))
        screen.blit(cow_area_img, cow_area_rect)
        screen.blit(chicken_area_img, chicken_area_rect)




        pygame.display.update()
    if keys[pygame.K_m]:
        show_market_content = True
    else:
        show_market_content = False
    if show_market_content:
        draw_market_content()

    if keys[pygame.K_i]: show_inventory = True
    else: show_inventory = False

    if show_inventory:
        draw_inventory()



    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()