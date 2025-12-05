import pygame
from config import *
from highscore import load_highscore


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, win):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(win, color, self.rect)
        pygame.draw.rect(win, (255, 255, 255), self.rect, 3)

        text_surface = MENU_FONT.render(self.text, 1, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        win.blit(text_surface, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


def show_menu(win):
    buttons = [
        Button(150, 260, 300, 60, "Play Solo", (70, 130, 180), (90, 150, 200)),
        Button(150, 340, 300, 60, "Play vs AI", (70, 130, 180), (90, 150, 200)),
        Button(150, 420, 300, 60, "Train AI", (70, 130, 180), (90, 150, 200)),
        Button(90, 500, 420, 60, "Train AI (Visualized)", (70, 130, 180), (90, 150, 200)),
        Button(225, 580, 150, 60, "Quit", (180, 70, 70), (200, 90, 90))
    ]

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for button in buttons:
            button.check_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if buttons[0].is_clicked(mouse_pos):
                    return "play"
                elif buttons[1].is_clicked(mouse_pos):
                    return "vs_ai"
                elif buttons[2].is_clicked(mouse_pos):
                    return "train"
                elif buttons[3].is_clicked(mouse_pos):
                    return "train_viz"
                elif buttons[4].is_clicked(mouse_pos):
                    return "quit"

        win.blit(bg_img, (0, 0))

        dark_overlay = pygame.Surface(bg_img.get_size()).convert_alpha()
        dark_overlay.fill((0, 0, 0, 50))

        win.blit(dark_overlay, (0, 0))

        title = END_FONT.render("Flappy Bird AI", 1, (255, 255, 255))
        win.blit(title, (WIN_WIDTH // 2 - title.get_width() // 2, 50))

        high_score = load_highscore()
        high_text = MENU_FONT.render(f"Human High Score: {high_score}", 1, (255, 215, 0))
        win.blit(high_text, (WIN_WIDTH // 2 - high_text.get_width() // 2, 160))

        for button in buttons:
            button.draw(win)

        controls_font = pygame.font.SysFont(None, 20)
        controls = controls_font.render("Press SPACE to jump | ESC to return to menu", 1, (200, 200, 200))
        win.blit(controls, (WIN_WIDTH // 2 - controls.get_width() // 2, 700))

        pygame.display.update()