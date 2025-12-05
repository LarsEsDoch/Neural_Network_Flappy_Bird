import pygame
import pickle
import os
from bird import Bird
from pipe import Pipe
from base import Base
from highscore import load_highscore, update_highscore
from config import *


def play_against_ai(win):
    if not os.path.exists("best.pickle"):
        show_error(win, "No trained AI found!", "Train the AI first")
        return True

    with open("best.pickle", "rb") as f:
        ai_net = pickle.load(f)

    human_bird = Bird(230, 350)
    ai_bird = Bird(230, 350)
    base = Base(FLOOR)
    pipes = [Pipe(700)]
    score = 0
    ai_score = 0
    high_score = load_highscore()
    clock = pygame.time.Clock()
    running = True
    human_alive = True
    ai_alive = True

    while running and (human_alive or ai_alive):
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and human_alive:
                    human_bird.jump()
                if event.key == pygame.K_ESCAPE:
                    return True

        pipe_ind = 0
        if len(pipes) > 1 and human_bird.x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
            pipe_ind = 1

        if human_alive:
            human_bird.move()

        if ai_alive:
            ai_bird.move()
            output = ai_net.activate((ai_bird.y, abs(ai_bird.y - pipes[pipe_ind].height),
                                      abs(ai_bird.y - pipes[pipe_ind].bottom)))
            if output[0] > 0.5:
                ai_bird.jump()

        base.move()

        add_pipe = False
        rem = []
        for pipe in pipes:
            pipe.move()

            if human_alive and pipe.collide(human_bird):
                human_alive = False

            if ai_alive and pipe.collide(ai_bird):
                ai_alive = False

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < max(human_bird.x if human_alive else 0,
                                                ai_bird.x if ai_alive else 0):
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            if human_alive:
                score += 1
            if ai_alive:
                ai_score += 1
            pipes.append(Pipe(WIN_WIDTH))

        for r in rem:
            pipes.remove(r)

        if human_alive and (human_bird.y + human_bird.img.get_height() - 10 >= FLOOR or human_bird.y < -50):
            human_alive = False

        if ai_alive and (ai_bird.y + ai_bird.img.get_height() - 10 >= FLOOR or ai_bird.y < -50):
            ai_alive = False

        if not human_alive and not ai_alive:
            update_highscore(score)
            show_vs_result(win, score, ai_score, high_score)
            return True

        draw_vs_window(win, human_bird, ai_bird, pipes, base, score, ai_score,
                       high_score, human_alive, ai_alive)


def draw_vs_window(win, human_bird, ai_bird, pipes, base, score, ai_score,
                   high_score, human_alive, ai_alive):
    win.blit(bg_img, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)

    if human_alive:
        human_bird.draw(win)
    if ai_alive:
        ai_bird.draw(win)

    human_label = STAT_FONT.render(f"You: {score}", 1, (100, 255, 100) if human_alive else (150, 150, 150))
    win.blit(human_label, (10, 10))

    ai_label = STAT_FONT.render(f"AI: {ai_score}", 1, (255, 100, 100) if ai_alive else (150, 150, 150))
    win.blit(ai_label, (10, 60))

    high_label = MENU_FONT.render(f"High: {high_score}", 1, (255, 255, 255))
    win.blit(high_label, (WIN_WIDTH - high_label.get_width() - 15, 10))

    pygame.display.update()


def show_vs_result(win, human_score, ai_score, high_score):
    win.blit(bg_img, (0, 0))

    if human_score > ai_score:
        result_text = END_FONT.render("You Win!", 1, (100, 255, 100))
    elif ai_score > human_score:
        result_text = END_FONT.render("AI Wins!", 1, (255, 100, 100))
    else:
        result_text = END_FONT.render("Draw!", 1, (255, 255, 100))

    win.blit(result_text, (WIN_WIDTH // 2 - result_text.get_width() // 2, 200))

    human_text = STAT_FONT.render(f"Your Score: {human_score}", 1, (255, 255, 255))
    win.blit(human_text, (WIN_WIDTH // 2 - human_text.get_width() // 2, 320))

    ai_text = STAT_FONT.render(f"AI Score: {ai_score}", 1, (255, 255, 255))
    win.blit(ai_text, (WIN_WIDTH // 2 - ai_text.get_width() // 2, 390))

    high_text = MENU_FONT.render(f"High Score: {high_score}", 1, (255, 215, 0))
    win.blit(high_text, (WIN_WIDTH // 2 - high_text.get_width() // 2, 480))

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


def show_error(win, title, message):
    win.blit(bg_img, (0, 0))

    title_text = END_FONT.render(title, 1, (255, 100, 100))
    win.blit(title_text, (WIN_WIDTH // 2 - title_text.get_width() // 2, 300))

    msg_text = STAT_FONT.render(message, 1, (255, 255, 255))
    win.blit(msg_text, (WIN_WIDTH // 2 - msg_text.get_width() // 2, 400))

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