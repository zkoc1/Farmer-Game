
import pygame
import sys

class UsernameInputScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 48)
        self.title_font = pygame.font.Font(None, 64)
        self.input_box = pygame.Rect(300, 300, 300, 60)
        self.active = False
        self.username = ""
        self.clock = pygame.time.Clock()

    def run(self):
        while True:
            self.screen.fill((135, 210, 235))

            pygame.draw.rect(self.screen, (34, 139, 34), (0, 600, 2000, 200))


            pygame.draw.circle(self.screen, (255, 255, 0), (80, 80), 50)
            title_text = self.title_font.render("Farm Game", True, (139, 69, 19))
            self.screen.blit(title_text, (230, 100))


            label = self.font.render("Enter your username:", True, (0, 0, 0))
            self.screen.blit(label, (300, 240))


            pygame.draw.rect(self.screen, (160, 82, 45), self.input_box, border_radius=10)
            pygame.draw.rect(self.screen, (0, 0, 0), self.input_box, 2, border_radius=10)

            # Kullanıcı adı
            text_surface = self.font.render(self.username, True, (255, 255, 255))
            self.screen.blit(text_surface, (self.input_box.x + 10, self.input_box.y + 15))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.active = self.input_box.collidepoint(event.pos)

                elif event.type == pygame.KEYDOWN and self.active:
                    if event.key == pygame.K_RETURN and self.username.strip() != "":
                        return self.username
                    elif event.key == pygame.K_BACKSPACE:
                        self.username = self.username[:-1]
                    else:
                        if len(self.username) < 15:
                            self.username += event.unicode

            pygame.display.flip()
            self.clock.tick(30)
