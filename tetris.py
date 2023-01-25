import pygame as pg
import random
import time
import sys
from pygame.locals import *

fps = 30
window_w, window_h = 400, 600
block, cup_h, cup_w = 20, 20, 10

side_freq, down_freq = 0.15, 0.1

side_margin = int((window_w - cup_w * block) / 2)
top_margin = window_h - (cup_h * block) - 5
side_margin = 10

bg_color = (244, 227, 215)
brd_color = (161, 92, 6)
bg_cup_color = (233, 198, 175)
col1, col2 = (200, 113, 55), (211, 141, 94)
colors = (col1, col1, col1, col1)
lightcolors = (col2, col2, col2, col2)
txt_color = (80, 45, 22)
title_color = (212, 85, 0)
info_color = txt_color

fig_w, fig_h = 5, 5

figures = {
    'Z': [['-----',
           '-----',
           '-++--',
           '--++-',
           '-----'],
          ['-----',
           '--+--',
           '-++--',
           '-+---',
           '-----']],
    'L': [['-----', '---+-', '-+++-', '-----', '-----'],
          ['-----', '--+--', '--+--', '--++-', '-----'],
          ['-----', '-----', '-+++-', '-+---', '-----'],
          ['-----', '-++--', '--+--', '--+--', '-----']],
    'I': [['-----', '--+--', '--+--', '--+--', '--+--'],
          ['-----', '-----', '++++-', '-----', '-----']],
    'S': [['-----', '-----', '--++-', '-++--', '-----'],
          ['-----', '--+--', '--++-', '---+-', '-----']],
    'O': [['-----', '-----', '-++--', '-++--', '-----']],
    'T': [['-----', '--+--', '-+++-', '-----', '-----'],
          ['-----', '--+--', '--++-', '--+--', '-----'],
          ['-----', '-----', '-+++-', '--+--', '-----'],
          ['-----', '--+--', '-++--', '--+--', '-----']],
    'J': [['-----', '-+---', '-+++-', '-----', '-----'],
          ['-----', '--++-', '--+--', '--+--', '-----'],
          ['-----', '-----', '-+++-', '---+-', '-----'],
          ['-----', '--+--', '--+--', '-++--', '-----']]}

empty = '-'


def pauseScreen():
    pause = pg.Surface((window_w, window_h), pg.SRCALPHA)
    pause.fill((50, 50, 50, 200))
    display_surf.blit(pause, (0, 0))


def main():
    global fps_clock, display_surf, basic_font, big_font, help_font
    pg.init()
    fps_clock = pg.time.Clock()
    display_surf = pg.display.set_mode((window_w, window_h))

    basic_font = pg.font.SysFont('veranda', 25)
    big_font = pg.font.SysFont('verdana', 45)
    pg.display.set_caption('Тетрис')
    help_font = pg.font.SysFont('arial', 20)
    showText('Тетрис')
    while True:
        runTetris()
        pauseScreen()
        showText('Игра закончена')


def runTetris():
    cup = emptycup()
    last_move_down = time.time()
    last_side_move = time.time()
    last_fall = time.time()
    go_down = False
    go_left = False
    go_right = False
    points = 0
    level, fall_speed = calcSpeed(points)
    falling_fig = getNewFig()
    nextFig = getNewFig()

    while True:
        if falling_fig == None:
            falling_fig = nextFig
            nextFig = getNewFig()
            last_fall = time.time()

            if not checkPos(cup, falling_fig):
                return
        quitGame()
        for event in pg.event.get():
            if event.type == KEYUP:
                if event.key == K_SPACE:
                    pauseScreen()
                    showText('Пауза')
                    last_fall = time.time()
                    last_move_down = time.time()
                    last_side_move = time.time()
                elif event.key == K_LEFT:
                    go_left = False
                elif event.key == K_RIGHT:
                    go_right = False
                elif event.key == K_DOWN:
                    go_down = False

            elif event.type == KEYDOWN:
                if event.key == K_LEFT and checkPos(cup, falling_fig, adjX=-1):
                    falling_fig['x'] -= 1
                    go_left = True
                    go_right = False
                    last_side_move = time.time()

                elif event.key == K_RIGHT and checkPos(cup, falling_fig, adjX=1):
                    falling_fig['x'] += 1
                    go_right = True
                    go_left = False
                    last_side_move = time.time()

                elif event.key == K_UP:
                    falling_fig['rotation'] = (
                        falling_fig['rotation'] + 1) % len(figures[falling_fig['shape']])
                    if not checkPos(cup, falling_fig):
                        falling_fig['rotation'] = (
                            falling_fig['rotation'] - 1) % len(figures[falling_fig['shape']])

                elif event.key == K_DOWN:
                    go_down = True
                    if checkPos(cup, falling_fig, adjY=1):
                        falling_fig['y'] += 1
                    last_move_down = time.time()

                elif event.key == K_RETURN:
                    go_down = False
                    go_left = False
                    go_right = False
                    for i in range(1, cup_h):
                        if not checkPos(cup, falling_fig, adjY=i):
                            break
                    falling_fig['y'] += i - 1

        if (go_left or go_right) and time.time() - last_side_move > side_freq:
            if go_left and checkPos(cup, falling_fig, adjX=-1):
                falling_fig['x'] -= 1
            elif go_right and checkPos(cup, falling_fig, adjX=1):
                falling_fig['x'] += 1
            last_side_move = time.time()

        if go_down and time.time() - last_move_down > down_freq and checkPos(cup, falling_fig, adjY=1):
            falling_fig['y'] += 1
            last_move_down = time.time()

        if time.time() - last_fall > fall_speed:
            if not checkPos(cup, falling_fig, adjY=1):
                addToCup(cup, falling_fig)
                points += clearCompleted(cup)
                level, fall_speed = calcSpeed(points)
                falling_fig = None
            else:
                falling_fig['y'] += 1
                last_fall = time.time()

        display_surf.fill(bg_color)
        drawTitle()
        gamecup(cup)
        drawInfo(points, level)
        drawnextFig(nextFig)
        if falling_fig != None:
            drawFig(falling_fig)
        pg.display.update()
        fps_clock.tick(fps)


def txtObjects(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def stopGame():
    pg.quit()
    sys.exit()


def checkKeys():
    quitGame()

    for event in pg.event.get([KEYDOWN, KEYUP]):
        if event.type == KEYDOWN:
            continue
        return event.key
    return None


def showText(text):
    titleSurf, titleRect = txtObjects(text, big_font, title_color)
    titleRect.center = (int(window_w / 2) - 3, int(window_h / 2) - 3)
    display_surf.blit(titleSurf, titleRect)

    pressKeySurf, pressKeyRect = txtObjects(
        'Нажмите любую клавишу для продолжения', basic_font, title_color)
    pressKeyRect.center = (int(window_w / 2), int(window_h / 2) + 100)
    display_surf.blit(pressKeySurf, pressKeyRect)

    while checkKeys() == None:
        pg.display.update()
        fps_clock.tick()


def quitGame():
    for event in pg.event.get(QUIT):

        stopGame()

    for event in pg.event.get(KEYUP):

        if event.key == K_ESCAPE:
            stopGame()
        pg.event.post(event)


def calcSpeed(points):
    level = points // 10 + 1
    fall_speed = 0.27 - (level * 0.02)
    return level, fall_speed


def getNewFig():
    shape = random.choice(list(figures.keys()))
    newFigure = {'shape': shape,
                 'rotation': random.randint(0, len(figures[shape]) - 1),
                 'x': int(cup_w / 2) - int(fig_w / 2),
                 'y': -2,
                 'color': random.randint(0, len(colors)-1)}
    return newFigure


def addToCup(cup, fig):
    for x in range(fig_w):
        for y in range(fig_h):
            if figures[fig['shape']][fig['rotation']][y][x] != empty:
                cup[x + fig['x']][y + fig['y']] = fig['color']


def emptycup():
    # создает пустой стакан
    cup = []
    for i in range(cup_w):
        cup.append([empty] * cup_h)
    return cup


def incup(x, y):
    return x >= 0 and x < cup_w and y < cup_h


def checkPos(cup, fig, adjX=0, adjY=0):
    for x in range(fig_w):
        for y in range(fig_h):
            abovecup = y + fig['y'] + adjY < 0
            if abovecup or figures[fig['shape']][fig['rotation']][y][x] == empty:
                continue
            if not incup(x + fig['x'] + adjX, y + fig['y'] + adjY):
                return False
            if cup[x + fig['x'] + adjX][y + fig['y'] + adjY] != empty:
                return False
    return True


def isCompleted(cup, y):
    for x in range(cup_w):
        if cup[x][y] == empty:
            return False
    return True


def clearCompleted(cup):
    removed_lines = 0
    y = cup_h - 1
    while y >= 0:
        if isCompleted(cup, y):
            for pushDownY in range(y, 0, -1):
                for x in range(cup_w):
                    cup[x][pushDownY] = cup[x][pushDownY - 1]
            for x in range(cup_w):
                cup[x][0] = empty
            removed_lines += 1
        else:
            y -= 1
    return removed_lines


def convertCoords(block_x, block_y):
    return (side_margin + (block_x * block)), (top_margin + (block_y * block))


def drawBlock(block_x, block_y, color, pixelx=None, pixely=None):
    # отрисовка
    if color == empty:
        return
    if pixelx == None and pixely == None:
        pixelx, pixely = convertCoords(block_x, block_y)
    pg.draw.rect(display_surf,
                 colors[color], (pixelx + 1, pixely + 1, block - 1, block - 1), 0, 1)
    pg.draw.rect(display_surf, lightcolors[color],
                 (pixelx + 1, pixely + 1, block - 3, block - 3), 0, 1)
    # pg.draw.circle(display_surf, colors[color], (pixelx + block / 2, pixely + block / 2), 5)
    pg.draw.circle(display_surf, bg_cup_color,
                   (pixelx + block / 2, pixely + block / 2), 2)


def gamecup(cup):
    pg.draw.rect(display_surf, brd_color, (side_margin-4, top_margin -
                 block-2, (cup_w * block) + 8, (cup_h * (block+1)) + 8), 4)

    pg.draw.rect(display_surf, bg_cup_color, (side_margin,
                 top_margin-block+2, block * cup_w, (block+1) * cup_h))
    for x in range(cup_w):
        for y in range(cup_h):
            drawBlock(x, y, cup[x][y])


def drawTitle():
    titleSurf = big_font.render('Тетрис', True, title_color)
    titleRect = titleSurf.get_rect()
    titleRect.topleft = (int(window_w/3), 30)
    display_surf.blit(titleSurf, titleRect)


def drawInfo(points, level):

    leftB = side_margin * 2 + cup_w*block + 20

    pointsSurf = basic_font.render(f'Баллы: {points}', True, txt_color)
    pointsRect = pointsSurf.get_rect()
    pointsRect.topleft = (leftB, window_h-cup_h * block - block)
    display_surf.blit(pointsSurf, pointsRect)

    levelSurf = basic_font.render(f'Уровень: {level}', True, txt_color)
    levelRect = levelSurf.get_rect()
    levelRect.topleft = (leftB, window_h-cup_h * block - block + 40)
    display_surf.blit(levelSurf, levelRect)

    pausebSurf = help_font.render('Пауза: пробел', True, info_color)
    pausebRect = pausebSurf.get_rect()
    pausebRect.topleft = (leftB, window_h - 60)
    display_surf.blit(pausebSurf, pausebRect)

    escbSurf = help_font.render('Выход: Esc', True, info_color)
    escbRect = escbSurf.get_rect()
    escbRect.topleft = (leftB, window_h - 30)
    display_surf.blit(escbSurf, escbRect)


def drawFig(fig, pixelx=None, pixely=None):
    figToDraw = figures[fig['shape']][fig['rotation']]
    if pixelx == None and pixely == None:
        pixelx, pixely = convertCoords(fig['x'], fig['y'])

    for x in range(fig_w):
        for y in range(fig_h):
            if figToDraw[y][x] != empty:
                drawBlock(None, None, fig['color'], pixelx +
                          (x * block), pixely + (y * block))


def drawnextFig(fig):  
    nextSurf = basic_font.render('Следующая:', True, txt_color)
    nextRect = nextSurf.get_rect()
    nextRect.topleft = (side_margin*2 + cup_w * block + 20,
                        window_h-cup_h * block - block + 80)
    display_surf.blit(nextSurf, nextRect)
    drawFig(fig, pixelx=window_w-150, pixely=window_h-cup_h*block - block + 100)


if __name__ == '__main__':
    main()
