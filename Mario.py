import pygame
from pygame.locals import *
from sys import exit
from random import randrange

#WHITE = (255, 255, 255)


def signal(x):
    if x > 0:
        return 1
    elif x == 0:
        return 0
    else:
        return -1


def get_rect(obj):
    return Rect(obj.position[0],
    obj.position[1],
    obj.rect[2],
    obj.rect[3])



class Bloco_invisivel(pygame.sprite.Sprite):
    def __init__(self, positionx, positiony, sizex, sizey):
        super().__init__()
        self.position = [positionx, positiony]
        self.rect = [0, 0, sizex, sizey]

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        positions = [(13, 17, 26, 33), (74, 17, 33, 35), (205, 17, 35, 35)]
        sheet = pygame.image.load('mario-sprite.png')
        self.ticks_to_change = 5
        self.sprite_index = 0
        self.sprite = []
        for i in range(len(positions)):
            sheet.set_clip(pygame.Rect(positions[i]))  # Locate the sprite you want
            self.sprite.append(sheet.subsurface(sheet.get_clip())) # Extract the sprite you want
        self.image = pygame.transform.flip(self.sprite[0], 1, 0)
        self.orientation = 1
        self.rect = self.image.get_rect()
        self.position = [250, 280]                                                   #posicao inicial
        self.speed = {
        'x': 0,
        'y': 0}

    def chao(self):
        self.position[1] += 1
        flag = 0
        obj_rect = get_rect(self)
        for each in lista_objetos:                                     #lista colisoes
            if obj_rect.colliderect(get_rect(each)):
                flag = 1
                break
        self.position[1] -= 1
        return flag


    def update_speed(self):
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_UP] and self.chao():
            self.speed['y'] = -15
            self.change_sprite(2)
            self.ticks_to_change = 6
            jump_sound.play()
        else:
            self.speed['y'] += 1


        if pressed_keys[K_LEFT]:
            self.speed['x'] = -5
            self.orientation = 0
        elif pressed_keys[K_RIGHT]:
            self.speed['x'] = 5
            self.orientation = 1
        else:
            self.speed['x'] = 0

    def update_position(self):
        avanco = self.speed['y']
        self.position[1] += avanco
        while(avanco != 0):
            flag = 0
            obj_rect = get_rect(self)
            for each in lista_objetos:
                if obj_rect.colliderect(get_rect(each)):
                    flag = 1
                    self.speed['y'] = 0
                    self.position[1] -=signal(avanco)
                    avanco -= signal(avanco)
                    break
            if flag == 0:
                avanco = 0


        avanco = self.speed['x']
        self.position[0] += avanco
        while(avanco != 0):
            flag = 0
            obj_rect = get_rect(self)
            for each in lista_objetos:                                     #lista colisoes
                if obj_rect.colliderect(get_rect(each)):
                    flag = 1
                    self.speed['x'] = 0
                    self.position[0] -=signal(avanco)
                    avanco -= signal(avanco)
                    break
            if flag == 0:
                avanco = 0


    def change_sprite(self, new):
        obj_rect = get_rect(self)
        for each in lista_objetos:
            if obj_rect.colliderect(get_rect(each)):
                print(str(old) + "erro" + str(new))


        old = self.sprite_index
        self.sprite_index = new
        self.position[1] -= self.sprite[new].get_rect()[3] -  self.sprite[old].get_rect()[3]
        self.rect = self.sprite[new].get_rect()
        obj_rect = get_rect(self)
        if self.orientation == 0:
            flag = 1
            while flag > 0:
                flag = 0
                for each in lista_objetos:
                    if obj_rect.colliderect(get_rect(each)):
                        flag = 1
                        self.position[0] -= 1
                        obj_rect = get_rect(self)
                        break
        else:
            self.position[0] -= self.sprite[new].get_rect()[2] - self.sprite[old].get_rect()[2]
            obj_rect = get_rect(self)
            flag = 1
            while flag > 0:
                flag = 0
                for each in lista_objetos:
                    if obj_rect.colliderect(get_rect(each)):
                        print(str(old) + "oi" + str(new))
                        flag = 1
                        self.position[0] -= 1
                        obj_rect = get_rect(self)
                        break



    def update_player(self):
        self.update_speed()
        if (self.sprite_index == 0 or self.sprite_index == 1) and self.speed['x'] != 0:
            self.ticks_to_change -= 1
            if self.ticks_to_change == 0:
                self.change_sprite(1 - self.sprite_index)
                self.ticks_to_change = 5
        else:
            if self.sprite_index == 1:
                self.change_sprite(0)
            elif self.sprite_index == 2 and self.ticks_to_change == 5 and self.chao():
                self.change_sprite(0)
            self.ticks_to_change = 5
        self.image = pygame.transform.flip(self.sprite[self.sprite_index], self.orientation, 0)
        self.update_position()


pygame.mixer.pre_init(44100, 32, 2, 4096)
pygame.init()
pygame.mixer.init(44100, -16,2,2048)
screen = pygame.display.set_mode((1200, 770), 0, 32)
pygame.display.set_caption('Mario')


mario = Player()


piso = Bloco_invisivel(0, 650, 1200, 120)
obstaculo = Bloco_invisivel(300, 550, 100, 200)
background = pygame.image.load('marioworld.png').convert()
jump_sound = pygame.mixer.Sound('Jump.wav')

lista_objetos = [piso, obstaculo]

clock = pygame.time.Clock()


while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()

    mario.update_player()

    screen.blit(background, (0, 0))                                 #print na tela
    screen.blit(mario.image, mario.position, mario.rect)
    pygame.display.update()
    clock.tick(30)
