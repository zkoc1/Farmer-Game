import pygame
import sys
import torch
import torch.nn as nn
import random
pygame.init()
# süt ve yumurta toplama süreleri
# data baseden hava durumu
#para artmalı süt ve yumurtayla market centexi değişsin ve paraya göre seviye ayarlansın başlangıçta isim sorulsun oyuncuya

city_weather_data = {
    "Antalya": (32, 60, 10),
    "Mersin": (30, 70, 8),
    "Adana": (35, 55, 12),
    "Muğla": (28, 65, 7),
    "İzmir": (27, 62, 9)
}
city_fruit_data = {
    "Antalya": "Mango",
    "Mersin": "Ananas",
    "Adana": "Papaya",
    "Muğla": "Avokado",
    "İzmir": "Kivi"
}
#screen = pygame.display.set_mode((900, 700))
font = pygame.font.SysFont(None, 40)
cities = ["Antalya", "Mersin", "Adana", "Muğla", "İzmir"]
selected_animal_area = None
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 750
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Farm Game")

clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

#son
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

fruit_images = {
    "Mango": pygame.image.load("mango.png"),
    "Ananas": pygame.image.load("ananas.png"),
    "Papaya": pygame.image.load("papaya.png"),
    "Avokado": pygame.image.load("avokado.png"),
    "Kivi": pygame.image.load("kivi.png")
}
crop_images = [
    pygame.image.load("crop_stage0.png"),
    pygame.image.load("crop_stage1.png"),
    pygame.image.load("crop_stage2.png")
]

inventory = {}


background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

def apply_weather_overlay(surface, weather):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    if weather == "Güneşli":
        overlay.fill((255, 255, 0, 100))
    elif weather == "Yağmurlu":
        overlay.fill((50, 50, 100, 150))
    elif weather == "Bulutlu":
        overlay.fill((150, 150, 150, 130))
    elif weather == "Kurak":
        overlay.fill((255, 200, 0, 120))
    surface.blit(overlay, (0, 0))


market_rect = market.get_rect(topleft=(1000, 200))
profile_rect = profile_icon.get_rect(topleft=(20, SCREEN_HEIGHT - 120))
tractor_rect = tractor_img.get_rect(topleft=(500, 600))
cow_area_rect = cow_area_img.get_rect(topleft=(3, 50))
chicken_area_rect = chicken_area_img.get_rect(topleft=(300, 10))
cow_pos = [cow_area_rect.x +10, cow_area_rect.y+20 ]
chicken_pos = [chicken_area_rect.x+10 , chicken_area_rect.y+10 ]


cow_speed = [random.choice([-0.5, 0.5]), random.choice([-0.5, 0.5])]
chicken_speed = [random.choice([-0.5, 0.5]), random.choice([-0.5, 0.5])]
dragging_cow_area =False
dragging_chicken_area =False
dragging_market = False

offset_x = 0
offset_y = 0


show_profile = False
show_market_content = False
show_cow_content = False
show_chicken_content = False
show_inventory = False

player_money = 1000
player_level = 5


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


        # Ekinin farklı büyüme aşamalarına ait resimleri
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
#weather_status = "Yağmurlu"
planting_allowed = True
player_money = 1000
player_level = 5

def draw_inventory():
    pygame.draw.rect(screen, WHITE, (100, 100, 400, 400))
    pygame.draw.rect(screen, BLACK, (100, 100, 400, 400), 2)
    y_offset = 120
    for item, count in inventory.items():
        text = font.render(f"{item}: {count}", True, BLACK)
        screen.blit(text, (120, y_offset))
        y_offset += 40



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
        # Hareketli alan içinde offset'e göre pozisyon belirle
        self.offset[0] += self.speed[0]
        self.offset[1] += self.speed[1]

        # Alan sınırlarına göre çarpma kontrolü
        if self.offset[0] < 10 or self.offset[0] > area_rect.width - self.rect.width - 10:
            self.speed[0] *= -1
        if self.offset[1] < 10 or self.offset[1] > area_rect.height - self.rect.height - 10:
            self.speed[1] *= -1

        # Güncel pozisyonu hesapla
        self.rect.topleft = (area_rect.left + self.offset[0], area_rect.top + self.offset[1])

        # Yumurtlama zamanı
        current_time = pygame.time.get_ticks()
        if not self.egg_visible and current_time - self.last_egg_time >= 2000:
            self.egg_visible = True
            self.egg_rect = self.egg_icon.get_rect(midbottom=(self.rect.centerx, self.rect.top))

        # Yumurtanın pozisyonu güncellenmeli
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
    def __init__(self, offset_position):
        self.image_right = pygame.image.load("cow_right.png")
        self.image_left = pygame.image.load("cow_left.png")
        self.milk_icon = pygame.image.load("milk-bottle.png")
        self.offset = list(offset_position)
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
        if not self.milk_visible and current_time - self.last_milk_time >= 2000:
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
    screen.blit(fruit_images[tropik_fruit], (1200, 100))
    apply_weather_overlay(screen, weather_status)
    screen.blit(market, market_rect.topleft)



    cow_img = cow_img_right if cow_speed[0] > 0 else cow_img_left
    chicken_img = chicken_img_right if chicken_speed[0] > 0 else chicken_img_left



    screen.blit(cow_area_img, cow_area_rect.topleft)
    screen.blit(chicken_area_img, chicken_area_rect.topleft)
    screen.blit(profile_icon, profile_rect.topleft)
    #screen.blit(envanter_img,(700,400))
    #screen.blit(cow_img_right if cow_speed[0] > 0 else cow_img_left, cow_pos)
    #screen.blit(chicken_img_right if chicken_speed[0] > 0 else chicken_img_left, chicken_pos)
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

            # Yumurtalara tıklama kontrolü
            for chicken in chickens:
                if chicken.check_egg_click(mouse_pos):
                    inventory["Yumurta"] = inventory.get("Yumurta", 0) + 1

            # Sütlere tıklama kontrolü
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

            if planting_allowed:
                mouse_x, mouse_y = event.pos
                if not (
                        cow_area_rect.collidepoint((mouse_x, mouse_y)) or
                        chicken_area_rect.collidepoint((mouse_x, mouse_y)) or
                        market_rect.collidepoint((mouse_x, mouse_y))or
                        profile_rect.collidepoint((mouse_x, mouse_y)) or
                        tractor_rect.collidepoint((mouse_x, mouse_y))
                ):
                    crops.append(Crop((mouse_x, mouse_y)))
            elif profile_rect.collidepoint(event.pos):
                show_profile = not show_profile
            elif planting_allowed and player_money >= 50:
                crops.append(Crop(event.pos))
                player_money -= 50
                for cow in cows:
                    if cow.check_milk_click(event.pos):
                        inventory["Süt"] = inventory.get("Süt", 0) + 1
                        player_money += 20  # süt sattığında para kazanma
                        print("Süt toplandı! Envanter:", inventory)
                for chicken in chickens:
                    if chicken.check_egg_click(event.pos):
                        inventory["Yumurta"] = inventory.get("Yumurta", 0) + 1
                        player_money += 10  # yumurta sattığında para kazanma
                        print("Yumurta toplandı! Envanter:", inventory)





        elif event.type == pygame.MOUSEBUTTONUP:
            dragging_market = False
            dragging_cow_area = False
            dragging_chicken_area = False


        elif event.type == pygame.MOUSEMOTION:
            if dragging_cow_area:
                dx = (event.pos[0] + offset_x) - cow_area_rect.x
                dy = (event.pos[1] + offset_y) - cow_area_rect.y

                #cow_area_rect.x += dx
                #cow_area_rect.y += dy
                #cow_pos[0] += dx
                #cow_pos[1] += dy
                new_rect = cow_area_rect.move(dx, dy)

                if not any(new_rect.colliderect(r) for r in
                           [market_rect, chicken_area_rect, tractor_rect, profile_rect]) and \
                        not any(new_rect.colliderect(crop.rect) for crop in crops):
                    cow_area_rect = new_rect
                    cow_pos[0] += dx
                    cow_pos[1] += dy
                    for cow in cows:
                        cow.offset[0] += dx
                        cow.offset[1] += dy


            elif dragging_chicken_area:
                dx = (event.pos[0] + offset_x) - chicken_area_rect.x
                dy = (event.pos[1] + offset_y) - chicken_area_rect.y

                #chicken_area_rect.x += dx
                #chicken_area_rect.y += dy
                #chicken_pos[0] += dx
                #chicken_pos[1] += dy
                new_rect = chicken_area_rect.move(dx, dy)

                if not any(
                        new_rect.colliderect(r) for r in [market_rect, cow_area_rect, tractor_rect, profile_rect]) and \
                        not any(new_rect.colliderect(crop.rect) for crop in crops):
                    chicken_area_rect = new_rect
                    chicken_pos[0] += dx
                    chicken_pos[1] += dy
                    for chicken in chickens:
                        chicken.offset[0] += dx
                        chicken.offset[1] += dy

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
                for idx, item in enumerate(market_items):
                    if event.key == pygame.K_1 + idx and player_money >= item["price"]:
                        player_money -= item["price"]
                        inventory.append(item["name"])

    new_tractor_rect = tractor_rect

    # Çakışma varsa hareket etme
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


    for crop in crops:
        crop.update(weather_status)
        crop.draw(screen)

        if crop.is_ready_to_harvest() and crop.rect.colliderect(tractor_rect):
            inventory["Buğday"] = inventory.get("Buğday", 0) + 1
            player_money += 100
            crop.stage = 0
            crop.timer = 0

    screen.blit(tractor_img, tractor_rect.topleft)
    if  keys[pygame.K_p]:
        pygame.draw.rect(screen, WHITE, (profile_rect.x, profile_rect.y - 100, 200, 100))
        pygame.draw.rect(screen, BLACK, (profile_rect.x, profile_rect.y - 100, 200, 100), 2)
        screen.blit(font.render(f"Para: {player_money}₺", True, BLACK), (profile_rect.x + 10, profile_rect.y - 90))
        screen.blit(font.render(f"Seviye: {player_level}", True, BLACK), (profile_rect.x + 10, profile_rect.y - 60))
        screen.blit(font.render(f"Envanter için 'i'", True, BLACK), (profile_rect.x + 10, profile_rect.y - 30))
        screen.blit(cow_area_img, cow_area_rect)
        screen.blit(chicken_area_img, chicken_area_rect)
        #apply_weather_overlay(screen, weather_status)



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

    if weather_status == "Yağmurlu":
        rain_effect.update()
        rain_effect.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()