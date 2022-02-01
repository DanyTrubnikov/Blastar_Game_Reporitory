import random
import time

import pygame
import os
import sys

pygame.init()

size = width, height = 900, 700

screen = pygame.display.set_mode(size)

clock = pygame.time.Clock()

BG = (206, 249, 101)
screen.fill(BG)
hp = 150
enemy_hp = 100
boss_hp = 3000
ALIEN_SPEED = 1
SPACING = 25
SHIP_SPEED = 10

FPS = 60


# Загрузка изображения
def load_image(name, colorkey=-1):

    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


def end_screen():
    intro_text = ["GAME OVER"]
    show_screen(intro_text)


def start_screen():
    intro_text = ["", "BLASTAR", "", "",
                  "Правила игры:", "",
                  "Управление осуществляется на стрелки влево и вправо", "",
                  "Выстрел осуществляется на пробел"]
    show_screen(intro_text)


def show_screen(intro_text):
    fon = pygame.transform.scale(load_image('Space_background.jpg', None), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return

        pygame.display.flip()
        clock.tick(FPS)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)

# Границы поля
class Border(pygame.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        if x1 == x2:  # вертикальная стенка
            self.add(vertical_borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:  # горизонтальная стенка
            self.add(horizontal_borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


class Player(pygame.sprite.Sprite):
    def __init__(self, screen):
        super().__init__(all_sprites)
        self.screen_rect = screen.get_rect()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.x = width // 2 - self.rect.width // 2
        self.rect.bottom = height
        self.mask = pygame.mask.from_surface(self.image)
        self.movie_right = False
        self.movie_left = False

    def update(self):
        global hp
        shot = None
        collision_with_enemy = None
        collision_with_asteroid = None
        #for laser_shot in enemy_shot_group.sprites():
            #shot = pygame.sprite.collide_mask(self, laser_shot)
        for ship in enemy_group.sprites():
            collision_with_enemy = pygame.sprite.collide_mask(self, ship)
        for asteroid in asteroid_group.sprites():
            collision_with_asteroid = pygame.sprite.collide_mask(self, asteroid)
        if self.movie_right and self.rect.right < self.screen_rect.right:
            self.rect.x += SHIP_SPEED
        elif self.movie_left and self.rect.left > 0:
            self.rect.x -= SHIP_SPEED

        if shot:
            hp -= 1
            if hp <= 0:
                self.image = boom_player_image
                '''Приостанавливаем время выполнения замены картинки взрыва на None
                   (то есть приостанавливаем убийство, чтобы взрыв можно было увидеть) на 1 секунду'''
                time.sleep(1)
                # Меняем картинку врага на None, чтобы она исчезла (само убийство)
                self.kill()
                terminate()

        if collision_with_enemy:
            hp -= 5
            if hp <= 0:
                self.image = boom_player_image
                '''Приостанавливаем время выполнения замены картинки взрыва на None
                   (то есть приостанавливаем убийство, чтобы взрыв можно было увидеть) на 1 секунду'''
                # Меняем картинку врага на None, чтобы она исчезла (само убийство)
                self.kill()
                terminate()

        if collision_with_asteroid:
            hp -= 10
            if hp <= 0:
                self.image = boom_player_image
                '''Приостанавливаем время выполнения замены картинки взрыва на None
                   (то есть приостанавливаем убийство, чтобы взрыв можно было увидеть) на 1 секунду'''
                self.kill()
                terminate()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, screen, number):
        super().__init__(all_sprites)
        self.screen_rect = screen.get_rect()
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.rect.x = (self.rect.width + SPACING) * number
        self.rect.bottom = 0

        self.mask = pygame.mask.from_surface(enemy_image)

    def update(self):
        global enemy_hp
        self.rect.y += ALIEN_SPEED
        if self.rect.top > self.screen_rect.bottom:
            self.kill()
        if self.rect.bottom > self.screen_rect.bottom:
            self.kill()
            # end_screen()

        shot = None
        shot = pygame.sprite.spritecollideany(self, laser_shot_group)
        if shot:
            enemy_hp -= 20
            if enemy_hp <= 0:
                self.image = boom_image
                '''Приостанавливаем время выполнения замены картинки взрыва на None
                   (то есть приостанавливаем убийство, чтобы взрыв можно было увидеть) на 1 секунду'''
                # Меняем картинку врага на None, чтобы она исчезла (само убийство)
                shot.kill()
                self.kill()


class Boss(pygame.sprite.Sprite):
    def __init__(self, screen, number):
        super().__init__(all_sprites)
        self.screen_rect = screen.get_rect()
        self.image = boss_image
        self.rect = self.image.get_rect()
        self.rect.x = (self.rect.width + SPACING) * number
        self.rect.bottom = 0

        self.mask = pygame.mask.from_surface(enemy_image)

    def update(self):
        global boss_hp
        self.rect.y += ALIEN_SPEED
        shot = None
        shot = pygame.sprite.spritecollideany(self, laser_shot_group)
        if self.rect.top > self.screen_rect.bottom:
            self.kill()
        if self.rect.bottom > self.screen_rect.bottom:
            self.kill()
            # end_screen()
        if shot:
            boss_hp -= 20
            if boss_hp <= 0:
                self.image = boom_boss_image
                '''Приостанавливаем время выполнения замены картинки взрыва на None
                   (то есть приостанавливаем убийство, чтобы взрыв можно было увидеть) на 1 секунду'''
                # Меняем картинку врага на None, чтобы она исчезла (само убийство)
                shot.kill()
                self.kill()


screen_rect = (0, 0, width, height)

class Laser_shot(pygame.sprite.Sprite):
    def __init__(self, plane, screen):
        super().__init__()
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.rect = pygame.Rect(0, 0, 3, 15)
        if random.randint(0, 10) % 2:
            self.rect.right = plane.rect.right - 15
        else:
            self.rect.left = plane.rect.left + 15
        self.rect.centery = plane.rect.centery
        self.color = ('red')

    def update(self):
        self.rect.y -= 10

    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.rect)


def draw_and_remove_laser_shot(laser_shot_group, player):

    for shot in laser_shot_group.sprites():
        shot.draw()
        if shot.rect.bottom > player.screen_rect.height:
            laser_shot_group.remove(shot)


class Enemy_shot(pygame.sprite.Sprite):
    def __init__(self, enemy, screen):
        super().__init__()
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.rect = pygame.Rect(0, 0, 3, 15)
        if random.randint(0, 10) % 2:
            self.rect.right = enemy.rect.right - 15
        else:
            self.rect.left = enemy.rect.left + 15
        self.rect.centery = enemy.rect.centery
        self.color = ('green')

    def update(self):
        self.rect.y -= -10

    def draw_enemy_shot(self):
        pygame.draw.rect(self.screen, self.color, self.rect)


def draw_and_remove_enemy_shot(enemy_shot_group):

    for shot in enemy_shot_group.sprites():
        shot.draw_enemy_shot()
        if shot.rect.bottom > enemy.screen_rect.height:
            enemy_shot_group.remove(shot)


class Asteroid(pygame.sprite.Sprite):
    def __init__(self, screen, number):
        super().__init__(all_sprites)
        self.screen_rect = screen.get_rect()
        self.image = asteroid_image
        self.rect = self.image.get_rect()
        self.rect.x = (self.rect.width + SPACING) * number
        self.rect.bottom = 0

        self.mask = pygame.mask.from_surface(asteroid_image)

    def update(self):
        global hp
        global running
        shot = None
        collision_with_player = None

        shot = pygame.sprite.spritecollideany(self, laser_shot_group)
        collision_with_player = pygame.sprite.collide_mask(self, player)
        self.rect.y -= -2

        if self.rect.top > self.screen_rect.bottom:
            self.kill()
        if self.rect.bottom > self.screen_rect.bottom:
            self.kill()

        if shot:
            shot.kill()
            self.kill()


running = True
if __name__ == '__main__':

    player_image = load_image('player_ship.jpg')
    enemy_image = load_image('enemy_ship.jpg')
    boss_image = load_image('third_boss.jpg')
    laser_shot_image = load_image('laser_shot.png')
    enemy_shot_image = load_image('enemy_laser_shots.png')
    boom_image = load_image('boom.png')
    boom_player_image = load_image('boom_player.jpg')
    boom_boss_image = load_image('boss_boom.jpg')
    asteroid_image = load_image('asteroid.jpg')

    all_sprites = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    asteroid_group = pygame.sprite.Group()
    laser_shot_group = pygame.sprite.Group()
    enemy_shot_group = pygame.sprite.Group()
    boss_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    horizontal_borders = pygame.sprite.Group()
    vertical_borders = pygame.sprite.Group()

    player = Player(screen)

    level = load_level("level.txt")
    counter = 0
    counter_for_shot = 0
    line = 0

    game_over = False
    win = False

    clock = pygame.time.Clock()

    start_screen()

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif not game_over and not win and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    player.movie_right = True
                if event.key == pygame.K_LEFT:
                    player.movie_left = True
            elif not game_over and not win and event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    player.movie_right = False
                if event.key == pygame.K_LEFT:
                    player.movie_left = False
                if event.key == pygame.K_SPACE:
                    laser_shot_group.add(Laser_shot(player, screen))
            elif game_over and event.type == pygame.MOUSEBUTTONDOWN: # на данный момент game_over=True
                game_over = False
            elif win and event.type == pygame.MOUSEBUTTONDOWN:
                print(win)
                win = False

        if not game_over and not win: #на данный момент game_over=False и win=False
            if pygame.sprite.spritecollideany(player, enemy_group):
                enemy_group.empty()
                all_sprites.empty()
                enemy_shot_group.empty()
                laser_shot_group.empty()
                asteroid_group.empty()
                level = load_level('level.txt')
                counter = 0
                line = 0
                hp = 150
                enemy_hp = 100
                boss_hp = 3000
                player = Player(screen)
                game_over = True

            if pygame.sprite.spritecollideany(player, enemy_shot_group):
                enemy_group.empty()
                all_sprites.empty()
                enemy_shot_group.empty()
                laser_shot_group.empty()
                asteroid_group.empty()
                level = load_level('level.txt')
                counter = 0
                line = 0
                hp = 150
                enemy_hp = 100
                boss_hp = 3000
                player = Player(screen)
                game_over = True

            if pygame.sprite.spritecollideany(player, asteroid_group):
                enemy_group.empty()
                all_sprites.empty()
                enemy_shot_group.empty()
                laser_shot_group.empty()
                asteroid_group.empty()
                level = load_level('level.txt')
                counter = 0
                line = 0
                hp = 150
                enemy_hp = 100
                boss_hp = 3000
                player = Player(screen)
                game_over = True

            if boss_hp <= 0:
                enemy_group.empty()
                all_sprites.empty()
                enemy_shot_group.empty()
                laser_shot_group.empty()
                asteroid_group.empty()
                level = load_level('level.txt')
                counter = 0
                line = 0
                hp = 150
                enemy_hp = 100
                boss_hp = 3000
                player = Player(screen)
                win = True

            if counter == 0:
                gen = level[line]
                i = 0
                for _ in range(len(gen)):
                    if gen[i] == 'x':
                        enemy_group.add(Enemy(screen, i))
                    elif gen[i] == 'B':
                        boss_group.add(Boss(screen, i))
                    elif gen[i] == '@':
                        asteroid_group.add(Asteroid(screen, i))
                    elif gen[i] == '#':
                        pass
                    i += 1
                line += 1

            if counter_for_shot % 100 == 0:
                for enemy in enemy_group.sprites():
                    enemy_shot_group.add(Enemy_shot(enemy, screen))

            screen.blit(load_image('space_bg_for_game.jpg', None), screen.get_rect())

            all_sprites.draw(screen)
            all_sprites.update()
            laser_shot_group.update()
            enemy_shot_group.update()
            draw_and_remove_laser_shot(laser_shot_group, player)
            draw_and_remove_enemy_shot(enemy_shot_group)
            counter = (counter + 1) % 150
            counter_for_shot += 1

        elif win: #на данный момент win=True
            screen.blit(load_image('win_screen.jpg', None), (0, 0))

        elif game_over: #на данный момент game_over=True
            screen.blit(load_image('gameover2_1.jpg', None), (0, 0))

        pygame.display.flip()
        clock.tick(FPS)