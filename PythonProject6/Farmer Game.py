import pygame
import sys
import torch
import torch.nn as nn
import random
pygame.init()

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 750
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Farm Game")

clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


background = pygame.image.load("background.png")
market = pygame.image.load('market.png')
fence = pygame.image.load('fence.png')
cow_img = pygame.image.load('cow.png')
chicken_img = pygame.image.load('chicken.png')
profile_icon = pygame.image.load('farmer.png')
tractor_img = pygame.image.load('tractor.png')

crop_images = [
    pygame.image.load("crop_stage0.png"),
    pygame.image.load("crop_stage1.png"),
    pygame.image.load("crop_stage2.png")
]

background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

def apply_weather_overlay(surface, weather):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    if weather == "Güneşli":
        overlay.fill((255, 255, 255, 60))  # Parlaklık efekti
    elif weather == "Yağmurlu":
        overlay.fill((100, 100, 100, 100))  # Gri filtre
    elif weather == "Bulutlu":
        overlay.fill((120, 120, 120, 90))  # Yarı şeffaf gri perde
    elif weather == "Kurak":
        overlay.fill((255, 255, 102, 80))  # Sarımsı filtre
    surface.blit(overlay, (0, 0))


market_rect = market.get_rect(topleft=(1000, 200))
fence_area_rect = pygame.Rect(1000, 500, 300, 200)
profile_rect = profile_icon.get_rect(topleft=(20, SCREEN_HEIGHT - 120))
tractor_rect = tractor_img.get_rect(topleft=(500, 600))

cow_pos = [fence_area_rect.x + 50, fence_area_rect.y + 50]
chicken_pos = [fence_area_rect.x + 150, fence_area_rect.y + 100]

cow_speed = [random.choice([-1, 1]), random.choice([-1, 1])]
chicken_speed = [random.choice([-1, 1]), random.choice([-1, 1])]

dragging_market = False
dragging_fence = False
offset_x = 0
offset_y = 0

show_profile = False
show_market_content = False
show_inventory = False

player_money = 1000
player_level = 5
inventory = []

market_items = [
    {"name": "Buğday Tohumu", "price": 100},
    {"name": "Hayvan Yemi", "price": 50},
    {"name": "Traktör Yakıtı", "price": 150}
]

font = pygame.font.SysFont(None, 24)

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
    for _ in range(300):
        temp = random.uniform(10, 40)
        humidity = random.uniform(10, 100)
        wind = random.uniform(0, 20)
        if humidity > 70 and temp < 25:
            label = 1
        elif temp > 35 and humidity < 30:
            label = 2
        elif temp > 25:
            label = 0
        else:
            label = 3
        X.append([temp, humidity, wind])
        y.append(label)
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

class RainEffect:
    def __init__(self):
        self.drops = [[random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)] for _ in range(100)]

    def update(self):
        for drop in self.drops:
            drop[1] += 5
            if drop[1] > SCREEN_HEIGHT:
                drop[1] = 0
                drop[0] = random.randint(0, SCREEN_WIDTH)

    def draw(self, screen):
        for drop in self.drops:
            pygame.draw.line(screen, (0, 0, 255), (drop[0], drop[1]), (drop[0], drop[1] + 5), 1)

rain_effect = RainEffect()

class Crop:
    def __init__(self, position):
        self.position = position
        self.stage = 0
        self.timer = 0
        self.rect = pygame.Rect(position[0], position[1], 32, 32)

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
        screen.blit(crop_images[self.stage], self.rect.topleft)

    def is_ready_to_harvest(self):
        return self.stage == 2

crops = []
weather_status = "Güneşli"
planting_allowed = True
player_money = 1000
player_level = 5

def draw_inventory():
    pygame.draw.rect(screen, WHITE, (100, 100, 400, 400))
    pygame.draw.rect(screen, BLACK, (100, 100, 400, 400), 2)
    y_offset = 120
    for item in inventory:
        text = font.render(item, True, BLACK)
        screen.blit(text, (120, y_offset))
        y_offset += 40

def move_animals():
    cow_pos[0] += cow_speed[0]
    cow_pos[1] += cow_speed[1]
    if cow_pos[0] < fence_area_rect.x + 20 or cow_pos[0] > fence_area_rect.x + 200:
        cow_speed[0] *= -1
    if cow_pos[1] < fence_area_rect.y + 20 or cow_pos[1] > fence_area_rect.y + 100:
        cow_speed[1] *= -1
    chicken_pos[0] += chicken_speed[0]
    chicken_pos[1] += chicken_speed[1]
    if chicken_pos[0] < fence_area_rect.x + 20 or chicken_pos[0] > fence_area_rect.x + 200:
        chicken_speed[0] *= -1
    if chicken_pos[1] < fence_area_rect.y + 20 or chicken_pos[1] > fence_area_rect.y + 100:
        chicken_speed[1] *= -1

def draw_market_content():
    pygame.draw.rect(screen, WHITE, (market_rect.x, market_rect.y - 150, 250, 150))
    pygame.draw.rect(screen, BLACK, (market_rect.x, market_rect.y - 150, 250, 150), 2)
    y_offset = market_rect.y - 130
    for idx, item in enumerate(market_items):
        text = font.render(f"{idx+1}) {item['name']} - {item['price']}₺", True, BLACK)
        screen.blit(text, (market_rect.x + 10, y_offset))
        y_offset += 40

# --- MAIN LOOP ---
back_sound = pygame.mixer.music.load('farm.wav')
pygame.mixer.music.play(-1)
running = True
while running:
    screen.fill(WHITE)
    screen.blit(background, (0, 0))
    screen.blit(background, (0, 0))
    apply_weather_overlay(screen, weather_status)
    screen.blit(market, market_rect.topleft)

    for i in range(5):
        screen.blit(fence, (fence_area_rect.x + i * 60, fence_area_rect.y))
    for i in range(3):
        screen.blit(fence, (fence_area_rect.x, fence_area_rect.y + i * 60))
        screen.blit(fence, (fence_area_rect.x + 240, fence_area_rect.y + i * 60))
    for i in range(5):
        screen.blit(fence, (fence_area_rect.x + i * 60, fence_area_rect.y + 120))

    screen.blit(cow_img, cow_pos)
    screen.blit(chicken_img, chicken_pos)
    screen.blit(profile_icon, profile_rect.topleft)
    screen.blit(tractor_img, tractor_rect.topleft)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if market_rect.collidepoint(event.pos):
                dragging_market = True
                offset_x = market_rect.x - event.pos[0]
                offset_y = market_rect.y - event.pos[1]
                show_market_content = not show_market_content
            elif fence_area_rect.collidepoint(event.pos):
                dragging_fence = True
                offset_x = fence_area_rect.x - event.pos[0]
                offset_y = fence_area_rect.y - event.pos[1]
            elif profile_rect.collidepoint(event.pos):
                show_profile = not show_profile
            elif planting_allowed and player_money >= 50:
                crops.append(Crop(event.pos))
                player_money -= 50
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging_market = False
            dragging_fence = False
        elif event.type == pygame.MOUSEMOTION:
            if dragging_market:
                market_rect.x = event.pos[0] + offset_x
                market_rect.y = event.pos[1] + offset_y
            if dragging_fence:
                fence_area_rect.x = event.pos[0] + offset_x
                fence_area_rect.y = event.pos[1] + offset_y
        elif event.type == pygame.KEYDOWN:
            if show_market_content:
                for idx, item in enumerate(market_items):
                    if event.key == pygame.K_1 + idx and player_money >= item["price"]:
                        player_money -= item["price"]
                        inventory.append(item["name"])

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: tractor_rect.x -= 5
    if keys[pygame.K_RIGHT]: tractor_rect.x += 5
    if keys[pygame.K_UP]: tractor_rect.y -= 5
    if keys[pygame.K_DOWN]: tractor_rect.y += 5

    move_animals()

    for crop in crops:
        crop.update(weather_status)
        crop.draw(screen)
        if crop.is_ready_to_harvest() and crop.rect.colliderect(tractor_rect):
            player_money += 100
            crop.stage = 0
            crop.timer = 0

    if show_profile:
        pygame.draw.rect(screen, WHITE, (profile_rect.x, profile_rect.y - 100, 200, 100))
        pygame.draw.rect(screen, BLACK, (profile_rect.x, profile_rect.y - 100, 200, 100), 2)
        screen.blit(font.render(f"Para: {player_money}₺", True, BLACK), (profile_rect.x + 10, profile_rect.y - 90))
        screen.blit(font.render(f"Seviye: {player_level}", True, BLACK), (profile_rect.x + 10, profile_rect.y - 60))
        screen.blit(font.render(f"Envanter için 'i'", True, BLACK), (profile_rect.x + 10, profile_rect.y - 30))

    if show_market_content:
        draw_market_content()

    if keys[pygame.K_i]: show_inventory = True
    else: show_inventory = False

    if show_inventory:
        draw_inventory()

    if weather_status == "Yağmurlu":
        rain_effect.update()
        rain_effect.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()