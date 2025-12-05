import pygame
import os
from main_menu import show_menu
from human_player import play_human
from versus_mode import play_against_ai
from neat_trainer import train_ai
from config import WIN, WIN_WIDTH, WIN_HEIGHT


def main():
    pygame.display.set_caption("Flappy Bird AI")

    while True:
        pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        choice = show_menu(WIN)

        if choice == "quit":
            break
        elif choice == "play":
            continue_playing = play_human(WIN)
            if not continue_playing:
                break
        elif choice == "vs_ai":
            continue_playing = play_against_ai(WIN)
            if not continue_playing:
                break
        elif choice == "train":
            local_dir = os.path.dirname(__file__)
            config_path = os.path.join(local_dir, 'config-feedforward.txt')
            train_ai(config_path, show_viz=False)
        elif choice == "train_viz":
            local_dir = os.path.dirname(__file__)
            config_path = os.path.join(local_dir, 'config-feedforward.txt')
            train_ai(config_path, show_viz=True)

    pygame.quit()


if __name__ == '__main__':
    main()