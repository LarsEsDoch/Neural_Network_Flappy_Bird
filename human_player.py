import pygame
from bird import Bird
from pipe import Pipe
from base import Base
from highscore import load_highscore, update_highscore
from config import *


def play_human(win):
    bird = Bird(230, 350)
    base = Base(FLOOR)
    pipes = [Pipe(700)]
    score = 0
    high_score = load_highscore()
    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()
                if event.key == pygame.K_ESCAPE:
                    return True

        bird.move()
        base.move()

        add_pipe = False
        rem = []
        for pipe in pipes:
            pipe.move()
            if pipe.collide(bird):
                if update_highscore(score):
                    show_game_over(win, score, high_score, True)
                else:
                    show_game_over(win, score, high_score, False)
                return True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            pipes.append(Pipe(WIN_WIDTH))

        for r in rem:
            pipes.remove(r)

        if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50:
            if update_highscore(score):
                show_game_over(win, score, high_score, True)
            else:
                show_game_over(win, score, high_score, False)
            return True

        draw_human_window(win, bird, pipes, base, score, high_score)


def draw_human_window(win, bird, pipes, base, score, high_score):
    win.blit(bg_img, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    bird.draw(win)

    score_label = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    high_label = STAT_FONT.render("High: " + str(high_score), 1, (255, 255, 255))
    win.blit(high_label, (10, 10))

    pygame.display.update()


def show_game_over(win, score, high_score, is_new_high):
    win.blit(bg_img, (0, 0))

    game_over_text = END_FONT.render("Game Over!", 1, (255, 255, 255))
    win.blit(game_over_text, (WIN_WIDTH // 2 - game_over_text.get_width() // 2, 200))

    score_text = STAT_FONT.render(f"Score: {score}", 1, (255, 255, 255))
    win.blit(score_text, (WIN_WIDTH // 2 - score_text.get_width() // 2, 300))

    if is_new_high:
        new_high_text = STAT_FONT.render("NEW HIGH SCORE!", 1, (255, 215, 0))
        win.blit(new_high_text, (WIN_WIDTH // 2 - new_high_text.get_width() // 2, 370))

    high_text = STAT_FONT.render(f"High Score: {high_score if not is_new_high else score}", 1, (255, 255, 255))
    win.blit(high_text, (WIN_WIDTH // 2 - high_text.get_width() // 2, 440))

    continue_text = MENU_FONT.render("Press any key to continue", 1, (200, 200, 200))
    win.blit(continue_text, (WIN_WIDTH // 2 - continue_text.get_width() // 2, 600))

    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                waiting = False