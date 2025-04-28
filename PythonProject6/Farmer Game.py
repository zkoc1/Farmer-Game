import pygame
import sys
import random

pygame.init()


SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 750
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Farm Game Full")

clock = pygame.time.Clock()


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


background = pygame.image.load("C:/Users/fkoc8/PycharmProjects/PythonProject6/png/background.png")

market = pygame.image.load('C:/Users/fkoc8/PycharmProjects/PythonProject6/png/market.png')
fence = pygame.image.load('C:/Users/fkoc8/PycharmProjects/PythonProject6/png/fence.png')
cow_img = pygame.image.load('C:/Users/fkoc8/PycharmProjects/PythonProject6/png/cow.png')
chicken_img = pygame.image.load('C:/Users/fkoc8/PycharmProjects/PythonProject6/png/chicken.png')
profile_icon = pygame.image.load('C:/Users/fkoc8/PycharmProjects/PythonProject6/png/farmer.png')
tractor_img = pygame.image.load('C:/Users/fkoc8/PycharmProjects/PythonProject6/png/tractor.png')

background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))


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


running = True
while running:
    screen.fill(WHITE)
    screen.blit(background, (0, 0))

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
                if event.key == pygame.K_1:
                    selected_item = market_items[0]
                    if player_money >= selected_item["price"]:
                        player_money -= selected_item["price"]
                        inventory.append(selected_item["name"])
                elif event.key == pygame.K_2:
                    selected_item = market_items[1]
                    if player_money >= selected_item["price"]:
                        player_money -= selected_item["price"]
                        inventory.append(selected_item["name"])
                elif event.key == pygame.K_3:
                    selected_item = market_items[2]
                    if player_money >= selected_item["price"]:
                        player_money -= selected_item["price"]
                        inventory.append(selected_item["name"])


    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        tractor_rect.x -= 5
    if keys[pygame.K_RIGHT]:
        tractor_rect.x += 5
    if keys[pygame.K_UP]:
        tractor_rect.y -= 5
    if keys[pygame.K_DOWN]:
        tractor_rect.y += 5

    move_animals()


    if show_profile:
        pygame.draw.rect(screen, WHITE, (profile_rect.x, profile_rect.y - 100, 200, 100))
        pygame.draw.rect(screen, BLACK, (profile_rect.x, profile_rect.y - 100, 200, 100), 2)
        money_text = font.render(f"Para: {player_money}₺", True, BLACK)
        level_text = font.render(f"Seviye: {player_level}", True, BLACK)
        screen.blit(money_text, (profile_rect.x + 10, profile_rect.y - 90))
        screen.blit(level_text, (profile_rect.x + 10, profile_rect.y - 60))
        inv_text = font.render(f"Envanter için 'i'", True, BLACK)
        screen.blit(inv_text, (profile_rect.x + 10, profile_rect.y - 30))


    if show_market_content:
        draw_market_content()

  
    if keys[pygame.K_i]:
        show_inventory = True
    else:
        show_inventory = False

    if show_inventory:
        draw_inventory()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
