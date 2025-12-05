import pygame
import neat
import pickle
import os
from bird import Bird
from pipe import Pipe
from base import Base
from neural_visualization import draw_neural_network
from config import *

generation = 0


def draw_training_window(win, birds, pipes, base, score, gen, pipe_ind, nets=None, show_viz=False):
    if gen == 0:
        gen = 1
    win.blit(bg_img, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)

    for bird in birds:
        if DEBUG:
            try:
                pygame.draw.line(win, (255, 0, 0),
                                 (bird.x + bird.img.get_width() / 2, bird.y + bird.img.get_height() / 2),
                                 (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width() / 2, pipes[pipe_ind].height),
                                 5)
                pygame.draw.line(win, (255, 0, 0),
                                 (bird.x + bird.img.get_width() / 2, bird.y + bird.img.get_height() / 2),
                                 (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width() / 2,
                                  pipes[pipe_ind].bottom), 5)
            except:
                pass
        bird.draw(win)

    score_label = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    gen_label = STAT_FONT.render("Gen: " + str(gen - 1), 1, (255, 255, 255))
    win.blit(gen_label, (10, 10))

    alive_label = STAT_FONT.render("Alive: " + str(len(birds)), 1, (255, 255, 255))
    win.blit(alive_label, (10, 50))

    # Draw neural network visualization if enabled and we have birds
    if show_viz and nets and len(birds) > 0 and len(pipes) > 0:
        bird = birds[0]
        net = nets[0]
        inputs = (bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom))

        # Draw semi-transparent background for viz
        viz_surface = pygame.Surface((400, 700), pygame.SRCALPHA)
        viz_surface.fill((0, 0, 0, 180))
        win.blit(viz_surface, (WIN_WIDTH, 50))

        # Extend window temporarily to show viz
        extended_win = pygame.display.set_mode((WIN_WIDTH + 400, WIN_HEIGHT))
        extended_win.blit(win, (0, 0))
        draw_neural_network(extended_win, net, inputs)

        title_font = pygame.font.SysFont("comicsans", 24)
        title = title_font.render("Neural Network", 1, (255, 255, 255))
        extended_win.blit(title, (WIN_WIDTH + 200 - title.get_width() // 2, 20))

        pygame.display.update()
        return

    pygame.display.update()


def eval_genomes(genomes, config, show_viz=False):
    global generation
    generation += 1

    nets = []
    birds = []
    ge = []

    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        ge.append(genome)

    base = Base(FLOOR)
    pipes = [Pipe(700)]
    score = 0
    clock = pygame.time.Clock()
    running = True

    win = pygame.display.set_mode((WIN_WIDTH + (400 if show_viz else 0), WIN_HEIGHT))

    while running and len(birds) > 0:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
                return

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1

        for x, bird in enumerate(birds):
            ge[x].fitness += 0.1
            bird.move()

            output = nets[birds.index(bird)].activate((bird.y,
                                                       abs(bird.y - pipes[pipe_ind].height),
                                                       abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:
                bird.jump()

        base.move()

        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()
            for bird in birds:
                if pipe.collide(bird):
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            for genome in ge:
                genome.fitness += 5
            pipes.append(Pipe(WIN_WIDTH))

        for r in rem:
            pipes.remove(r)

        for bird in birds:
            if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50:
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        draw_training_window(win, birds, pipes, base, score, generation, pipe_ind, nets, show_viz)

        if score > 2000:
            pickle.dump(nets[0], open("best.pickle", "wb"))
            break

    pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))


def train_ai(config_file, show_viz=False):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(lambda genomes, config: eval_genomes(genomes, config, show_viz), 100000)
    print('\nBest genome:\n{!s}'.format(winner))