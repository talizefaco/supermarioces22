import pygame
from pygame.locals import *
from sys import exit
from operator import attrgetter

import xinput

"""Inicializar o pygame"""
pygame.mixer.pre_init(44100, 32, 2, 4096)
pygame.init()
pygame.mixer.init(44100, -16, 2, 2048)
screen = pygame.display.set_mode((1280, 768), 0, 32)
pygame.display.set_caption('Mario')
myfont = pygame.font.SysFont("monospace", 30)
pygame.joystick.init()
joysticks = xinput.XInputJoystick.enumerate_devices()
device_numbers = list(map(attrgetter('device_number'), joysticks))
joystick = [None, None]
if device_numbers:
    joystick[0] = xinput.XInputJoystick(device_numbers[0])
    if device_numbers > 1:
        joystick[1]  = xinput.XInputJoystick(device_numbers[1])

try:
    sheet = pygame.image.load('sprites.png')
    background = pygame.image.load('background.png').convert()
    jump_sound = pygame.mixer.Sound('Jump.wav')
    coin_sound = pygame.mixer.Sound('Coin.wav')
    bomb_sound = pygame.mixer.Sound('Bomb.wav')
    death_sound = pygame.mixer.Sound('Death.wav')
    mush_sound = pygame.mixer.Sound('Mush_up.wav')


except:
    print("Erro: Arquivo não encontrado. Certifique-se de que todos estão na mesma pasta do jogo")
    exit()

def clip_sheet(position):
    sheet.set_clip(pygame.Rect(position))  # Locate the sprite you want
    return sheet.subsurface(sheet.get_clip())

def signal(x):
    """Essa função retorna o sinal de um número x: 1 para +, -1 para - e 0 para 0"""
    if x > 0:
        return 1
    elif x == 0:
        return 0
    else:
        return -1

def collides(obj, lista, inicial = None):   #interage com o pygame
    """Essa função detecta colisão de um ojeto com uma determinada lista de objetos e retorna a primeira colisão que encontrar
    Caso receba um argumento adicional, ela só começa a procurar colisão a partir do objeto recebido"""
    if(inicial != None):
        i = 0
        while(lista[i] != inicial):
            i += 1
        lista2 = lista[i+1:]
    else:
        lista2 = lista

    obj_rect = obj.get_rect()
    for each in lista2:
        if obj_rect.colliderect(each.get_rect()) and each != obj:
            return each
    return 0

class Bloco():
    """Essa classe é usada para criar um bloco qualquer no jogo"""
    def __init__(self, positionx, positiony, sizex, sizey, image, explosivo = 0, lista = 0):
        self.list_index = lista
        self.position = [positionx, positiony]
        self.sizex = sizex
        self.sizey = sizey
        self.image = image
        self.explosivo = explosivo
        lista_obj[lista].append(self)
        self.speedy = 0

    def get_rect(self):
        """Retorna o retangulo correspondente a posicao do bloco"""
        return Rect(self.position[0],
                    self.position[1],
                    self.sizex,
                    self.sizey)

    def explode(self):
        lista_obj[self.list_index].remove(self)
        try:
            funcoes_update.remove(self.update)
        except:
            pass
        return 1

    def collision(self, who_triggers):
        return 0

    def cair(self, companion = None):
        self.speedy += 1
        avanco = self.speedy
        while avanco > 0:
            self.position[1] += 1
            if companion != None:
                companion.position[1] += 1
            if collides(self, lista_obj[0]) != 0:
                self.position[1] -= 1
                if companion != None:
                    companion.position[1] -= 1
                self.speedy = 0
                break
            self.trigger_events()
            avanco -= 1

    def trigger_events(self):
        x = collides(self, lista_obj[1])
        anterior = None
        while  x != 0:
            if x.collision(self) == 1:
                x = collides(self, lista_obj[1], anterior)
            else:
                anterior = x
                x = collides(self, lista_obj[1], anterior)

class Cogumelo(Bloco):
    def __init__(self, positionx, positiony, vel = 0):
        super().__init__(positionx, positiony, 32, 32, clip_sheet([594, 0, 32, 32]), 1, 1)
        self.vel = vel
        funcoes_update.append(self.update)

    def  collision(self, who_triggers):
        used = 0
        try:
            who_triggers.grow()
            used = 1
            lista_obj[1].remove(self)
            funcoes_update.remove(self.update)
            return 1
        except:
            if used == 1:
                return 1
        return 0

    def update(self):
        self.cair()
        avanco = self.vel
        while avanco != 0:
            self.position[0] += signal(avanco)
            who_collides = collides(self, lista_obj[0])
            if who_collides != 0:
                try:
                    who_collides.grow()
                    self.explode()
                except:
                    pass
                self.position[0] -= signal(avanco)
                self.vel = -1*self.vel
                break
            avanco -= signal(avanco)

class Box(Bloco):
    def __init__(self, positionx, positiony, content = "Coin"):
        self.content = content
        self.sprite = []
        positions = [(98, 0, 32, 32), (132, 0, 32, 32), (166, 0, 32, 32), (328, 0, 32, 32)]
        for i in range(len(positions)):
            self.sprite.append(clip_sheet(positions[i]))
        self.ticks_to_change = 5
        self.sprite_index = 0
        super().__init__(positionx, positiony, 32, 32, self.sprite[self.sprite_index], 1)
        funcoes_update.append(self.update)
        self.trig = BoxTrigger(self)

    def update(self):
        if self.ticks_to_change == 0:
            self.ticks_to_change = 5
            self.sprite_index = (self.sprite_index + 1) % 3
            self.image = self.sprite[self.sprite_index]
        else:
            self.ticks_to_change -= 1

    def trigger(self, who_triggers):
        self.trig = None
        self.sprite_index = 3
        self.image = self.sprite[3]
        funcoes_update.remove(self.update)
        if(self.content == "Coin"):
            try:
                who_triggers.coins += 1
                coin_sound.play()
            except:
                pass
            Animacao_Moeda(self.position[0], self.position[1] - 32)
        elif(self.content == "Cogumelo"):
            Cogumelo(self.position[0], self.position[1] - 32, -4)
    def explode(self):
        if self.trig != None:
            lista_obj[1].remove(self.trig)
            funcoes_update.remove(self.update)
        self.explosivo = 0
        self.sprite_index = 3
        self.image = self.sprite[3]
        return 0

class BoxTrigger(Bloco):
    def __init__(self, box):
        self.mybox = box
        super().__init__(self.mybox.position[0], self.mybox.position[1] + 32, 32, 1, None, 0, 1)


    def collision(self, who_triggers):
        self.mybox.trigger(who_triggers)
        lista_obj[1].remove(self)
        return 1

class Lava(Bloco):
    def __init__(self, positionx, positiony):
        super().__init__(positionx, positiony + 4, 32, 28, clip_sheet([390, 0, 32, 28]), 0, 1)

    def  collision(self, who_triggers):
        try:
            who_triggers.damage(1)
        except:
            pass
        try:
            who_triggers.explode()
        except:
            pass

class Coin(Bloco):
    def __init__(self, positionx, positiony):
        super().__init__(positionx + 4, positiony, 24, 32, clip_sheet([302, 0, 24, 32]), 1, 1)

    def  collision(self, who_triggers):
        try:
            who_triggers.coins += 1
            coin_sound.play()
            lista_obj[1].remove(self)
            return 1
        except:
            pass
        return 0

class Animacao_Moeda(Bloco):
    def __init__(self, positionx, positiony):
        super().__init__(positionx + 4, positiony, 24, 32, clip_sheet([302, 0, 24, 32]), 1, 1)
        self.tick = 10
        funcoes_update.append(self.update)

    def update(self):
        if self.tick == 0:
            lista_obj[1].remove(self)
            funcoes_update.remove(self.update)
        else:
            self.tick -= 1

class Bomb(Bloco):
    def __init__(self, positionx, positiony):
        self.raio_de_explosao = 60
        self.tick = 100
        super().__init__(positionx + 1, positiony - 16, 30, 48, clip_sheet([360, 0, 30, 48]), 1)
        funcoes_update.append(self.update)
        self.dragger = Bomb_Dragger(self)

    def update(self):
        self.tick -= 1
        if self.tick == 0:
            self.detonate()
        self.cair(self.dragger)

    def explode(self):
        self.detonate()

    def detonate(self):
        bomb_sound.play()
        Animacao_Bomba(self.position[0] - 15, self.position[1] - 15)
        obj_explosao = Bloco(self.position[0] - self.raio_de_explosao, self.position[1] - self.raio_de_explosao, 2*self.raio_de_explosao + self.sizex, 2*self.raio_de_explosao + self.sizey, None, 0, 1)
        lista_obj[1].remove(obj_explosao)
        self.remove()
        for i in [0, 1]:
            x = collides(obj_explosao, lista_obj[i])
            anterior = None
            while x != 0:
                if x.explosivo == 1:
                    if x.explode() == 0:
                        anterior = x
                else:
                    anterior = x
                x = collides(obj_explosao, lista_obj[i], anterior)

    def remove(self):
        funcoes_update.remove(self.update)
        lista_obj[0].remove(self)
        lista_obj[1].remove(self.dragger)

class Explosao(Bloco):
    def __init__(self, myBomb):
        super().__init__(myBomb.position[0] - 60, myBomb.position[1] - 60, 120 + myBomb.sizex, 120 + myBomb.sizey, None, 0, 1)
        lista_obj[1].remove(self)

class Bomb_Dragger(Bloco):
    def __init__(self, myBomb):
        self.myBomb = myBomb
        super().__init__(self.myBomb.position[0] - 1, self.myBomb.position[1] + 1, 32, 47, None, 0, 1)

    def collision(self, who_triggers):
        if(who_triggers != self.myBomb):
            if who_triggers.position[0] < self.position[0]:
                self.position[0] += 1
                self.myBomb.position[0] += 1
                if collides(self.myBomb, lista_obj[0]) != 0:
                    self.position[0] -= 1
                    self.myBomb.position[0] -= 1
            else:
                self.position[0] -= 1
                self.myBomb.position[0] -= 1
                if collides(self.myBomb, lista_obj[0]) != 0:
                    self.position[0] += 1
                    self.myBomb.position[0] += 1
        self.trigger_events()

class Animacao_Bomba(Bloco):
    def __init__(self, positionx, positiony):
        self.sprite = []
        for i in range(9):
            self.sprite.append(clip_sheet([70*i, 63,62,62]))
        super().__init__(positionx , positiony, 62, 62, self.sprite[0], 0, 1)
        self.tick = 2
        funcoes_update.append(self.update)
        self.sprite_index = 0

    def update(self):
        self.tick -= 1
        if self.tick == 0:
            if self.sprite_index < 8:
                self.sprite_index += 1
                self.image = self.sprite[self.sprite_index]
                self.tick = 2
            else:
                lista_obj[1].remove(self)
                funcoes_update.remove(self.update)

class Player(Bloco):
    """Essa classe é usada para criar o jogador"""
    def __init__(self, posx, posy, player = 0):
        self.player = player
        positions = [[(0, 0, 28, 40), (32, 0, 30, 38), (64, 0, 32, 44), (0, 180, 30, 56), (34, 180, 32, 54), (68, 180, 32, 62)],
                     [(0, 130, 28, 40), (32, 130, 30, 38), (64, 130, 32, 44), (0, 250, 30, 56), (34, 250, 32, 54), (68, 250, 32, 62)]]         #representa a posicao e o tamanho das sprites na sprite sheet
        lista_obj[0].append(self)
        self.bomb_button_hold = 0
        self.grande = 1
        self.coins = 0
        self.bombs = 5
        self.explosivo = 1
        self.ticks_to_change = 5
        self.sprite_index = 2                                                       #inicia com a sprite do Mario pulando
        self.change_pending = self.sprite_index
        self.ticks_to_stop = 0
        #inicializa as sprites
        self.sprite = [[], []]
        for j in range(2):
            for i in range(len(positions[j])):
                self.sprite[j].append(clip_sheet(positions[j][i])) # Extract the sprite you want

        #inicializa a imagem do player
        self.orientation = 1
        self.image = pygame.transform.flip(self.sprite[self.player][self.sprite_index], self.orientation, 0)
        self.sizex = self.sprite[self.player][self.sprite_index].get_rect()[2]
        self.sizey = self.sprite[self.player][self.sprite_index].get_rect()[3]
        self.position = [posx, posy]                                                  #posicao inicial
        self.speed = [0, 0]                                                         #velocidade inicial
        funcoes_update.append(self.update_player)
        funcoes_update.append(self.print_info)

    def esta_no_chao(self):
        """Retorna 1 se o objeto está em contato com alguma superfícia abaixo"""
        self.position[1] += 1
        x = collides(self, lista_obj[0])
        self.position[1] -=1
        if x == 0:
            return x
        else:
            return 1

    def get_inputs(self):
        pressed_keys = pygame.key.get_pressed()

        if ((pressed_keys[K_UP] and self.player == 0) or (pressed_keys[K_w] and self.player == 1) or joystick_commands[self.player]['A']) and self.esta_no_chao():
            self.speed[1] = -15
            self.ticks_to_change = 5
            jump_sound.play()
        else:
            self.speed[1] += 1

        if (pressed_keys[K_LEFT] and self.player == 0)  or (pressed_keys[K_a] and self.player == 1) or joystick_commands[self.player]['x_axis'] < -0.2:
            self.speed[0] = -5
            self.orientation = 0
        elif (pressed_keys[K_RIGHT] and self.player == 0) or (pressed_keys[K_d] and self.player == 1) or joystick_commands[self.player]['x_axis'] > 0.2:
            self.speed[0] = 5
            self.orientation = 1
        else:
            self.speed[0] = 0

        if (pressed_keys[K_RSHIFT] and self.player == 0) or (pressed_keys[K_LSHIFT] and self.player == 1)  or (pressed_keys[K_d] and self.player == 1)or joystick_commands[self.player]['R_trigger'] > 0:
            self.speed[0] *= 1.6

        if ((pressed_keys[K_RCTRL] and self.player == 0) or (pressed_keys[K_SPACE] and self.player == 1) or joystick_commands[self.player]['X']) and self.bombs > 0 and not self.bomb_button_hold:
            self.bomb_button_hold = 1
            if self.orientation == 0:
                bomba = Bomb(self.position[0] - 32, self.position[1] - (48-self.sizey))
            else:
                bomba = Bomb(self.position[0] + self.sizex, self.position[1] - (48-self.sizey))
            if collides(bomba, lista_obj[0]) != 0:
                bomba.remove()
            else:
                self.bombs -= 1
        elif not((pressed_keys[K_RCTRL] and self.player == 0) or (pressed_keys[K_LCTRL] and self.player == 1) or joystick_commands[self.player]['X']):
            self.bomb_button_hold = 0

    def change_sprite(self, new):
        self.change_pending = new
        """Essa função não é tão trivial. Quando a sprite muda, o seu tamanho também pode mudar, causando problemas de colisão."""
        old = self.sprite_index
        self.sprite_index = new
        self.ticks_to_change = 5

        posx = self.position[0]
        posy = self.position[1]
        self.sizey = self.sprite[self.player][new].get_rect()[3]
        self.position[1] -= self.sprite[self.player][new].get_rect()[3] -  self.sprite[self.player][old].get_rect()[3]  #mantém a a borda inferior da sprite no mesmo lugar
        contador = 0
        while collides(self, lista_obj[0]):
            contador += 1
            self.position[1] += 1
            if contador > self.sprite[self.player][new].get_rect()[3] - self.sprite[self.player][old].get_rect()[3]:
                self.position[1] = posy
                self.sprite_index = old
                self.sizey = self.sprite[self.player][old].get_rect()[3]
                return()

        self.sizex = self.sprite[self.player][new].get_rect()[2]
        contador = 0
        if self.orientation == 0:   #mantém a borda esquerda da sprite no mesmo lugar
            while collides(self, lista_obj[0]) != 0:
                self.position[0] -= 1
                contador += 1
                if contador > self.sprite[self.player][new].get_rect()[2] - self.sprite[self.player][old].get_rect()[2]:
                    self.position[0] = posx
                    self.position[1] = posy
                    self.sprite_index = old
                    self.sizex = self.sprite[self.player][old].get_rect()[2]
                    self.sizey = self.sprite[self.player][old].get_rect()[3]
        else:                       #mantém a borda direita da sprite no mesmo lugar
            self.position[0] -= self.sprite[self.player][new].get_rect()[2] - self.sprite[self.player][old].get_rect()[2]
            while collides(self, lista_obj[0]) != 0:
                self.position[0] += 1
                contador += 1
                if contador > self.sprite[self.player][new].get_rect()[2] - self.sprite[self.player][old].get_rect()[2]:
                    self.position[0] = posx
                    self.position[1] = posy
                    self.sprite_index = old
                    self.sizex = self.sprite[self.player][old].get_rect()[2]
                    self.sizey = self.sprite[self.player][old].get_rect()[3]

    def update_sprite(self):
        if self.change_pending != self.sprite_index:
            self.change_sprite(self.sprite_index)

        if not self.grande:
            if not self.esta_no_chao():
                self.change_sprite(2)
            if (self.sprite_index == 0 or self.sprite_index == 1) and self.speed[0] != 0:
                self.ticks_to_change -= 1
                if self.ticks_to_change == 0:
                    self.change_sprite(1 - self.sprite_index)
            else:
                self.ticks_to_change = 5
                if self.sprite_index == 1:          #speed == 0
                    self.change_sprite(0)
                elif self.sprite_index == 2 and self.esta_no_chao():
                    self.change_sprite(0)
        else:
            if not self.esta_no_chao():
                self.change_sprite(5)
            if (self.sprite_index == 3 or self.sprite_index == 4) and self.speed[0] != 0:
                self.ticks_to_change -= 1
                if self.ticks_to_change == 0:
                    self.change_sprite(7 - self.sprite_index)
            else:
                self.ticks_to_change = 5
                if self.sprite_index == 4:          #speed == 0
                    self.change_sprite(3)
                elif self.sprite_index == 5 and self.esta_no_chao():
                    self.change_sprite(3)

        self.image = pygame.transform.flip(self.sprite[self.player][self.sprite_index], self.orientation, 0)

    def update_position(self):
         for i in [0, 1]:
            avanco = self.speed[i]
            while avanco != 0:
                self.position[i] += signal(avanco)
                if collides(self, lista_obj[0]) != 0:
                    self.position[i] -= signal(avanco)
                    self.speed[i] = 0
                    avanco = 0
                avanco -= signal(avanco)
                self.trigger_events()

    def print_info(self):
        label = myfont.render(str(self.coins), 1, (0, 0, 0))
        label2 = myfont.render(str(self.bombs), 1, (0, 0, 0))
        if self.player == 0:
            screen.blit(label, (65, 30))
            screen.blit(label2, (135, 30))
            screen.blit(clip_sheet([302, 0, 24, 32]), [30, 27])
            screen.blit(clip_sheet([360, 0, 30, 48]), [100, 12])
        else:
            screen.blit(label, (1165, 30))
            screen.blit(label2, (1235, 30))
            screen.blit(clip_sheet([302, 0, 24, 32]), [1130, 27])
            screen.blit(clip_sheet([360, 0, 30, 48]), [1200, 12])

    def update_player(self):
        self.get_inputs()
        self.update_position()
        self.update_sprite()
        self.image = pygame.transform.flip(self.sprite[self.player][self.sprite_index], self.orientation, 0)

    def explode(self):
        return self.damage()

    def stop_vibration(self):
        self.ticks_to_stop -= 1
        if self.ticks_to_stop == 0:
            try:
                joystick[self.player].set_vibration(0, 0)
            finally:
                funcoes_update.remove(self.stop_vibration)

    def damage(self, critic = 0):
        try:
            if self.ticks_to_stop == 0:
                joystick[self.player].set_vibration(5000, 5000)
                funcoes_update.append(self.stop_vibration)
                self.ticks_to_stop = 20
        except:
            pass

        if self.grande and not critic:
            self.grande = 0
            if self.sprite_index >= 3:
                self.change_sprite(self.sprite_index - 3)
        else:
            death_sound.play()
            funcoes_update.remove(self.update_player)
            lista_obj[0].remove(self)
            return 1
        return 0

    def grow(self):
        mush_sound.play()
        self.grande = 1
        if self.sprite_index < 3:
            self.change_sprite(self.sprite_index + 3)

def inicializa_mapa():
    funcoes_update.append(print_background)
    """Inicializar o cenário"""
    mapa  = open('stage.txt', 'r')
    linhas = mapa.readlines()
    for i in range(24):
        for j in range(40):
            if linhas[i][j] == 'T':
                Bloco(32*j, 32*i, 32, 32, clip_sheet([200, 0,32,32]))
            elif linhas[i][j] == 'U':
                Bloco(32*j, 32*i, 32, 32, clip_sheet([234, 0,32,32]))
            elif linhas[i][j] == 'S':
                Bloco(32*j, 32*i, 32, 32, clip_sheet([268, 0,32,32]))
            elif linhas[i][j] == '1':
                Bloco(32*j, 32*i, 32, 32, clip_sheet([424, 0,32,32]))
            elif linhas[i][j] == '2':
                Bloco(32*j, 32*i, 32, 32, clip_sheet([458, 0,32,32]))
            elif linhas[i][j] == '3':
                Bloco(32*j, 32*i, 32, 32, clip_sheet([492, 0,32,32]))
            elif linhas[i][j] == '4':
                Bloco(32*j, 32*i, 32, 32, clip_sheet([526, 0,32,32]))
            elif linhas[i][j] == 'J':
                Bloco(32 * j, 32 * i, 32, 32, clip_sheet([560, 0, 32, 32]), 1)
            elif linhas[i][j] == 'M':
                mario = Player(32*j, 32*i)
            elif linhas[i][j] == 'L':
                mario = Player(32*j, 32*i, 1)
            elif linhas[i][j] == 'B':
                Box(32*j, 32*i)
            elif linhas[i][j] == 'Z':
                Box(32*j, 32*i, "Cogumelo")
            elif linhas[i][j] == 'C':
                Coin(32*j, 32*i)
            elif linhas[i][j] == 'Y':
                Cogumelo(32*j, 32*i)
            elif linhas[i][j] == 'F':
                Lava(32 * j, 32 * i)
            elif linhas[i][j] == 'X':
                Bomb(32*j, 32*i)
    mapa.close()
    funcoes_update.append(print_tela)

    if mario == None:
        print("Mapa com defeito. Não foi definida a posição inicial do jogador")
        exit()

    Bloco(1280, 0, 100, 768, None)
    Bloco(-100, 0, 100, 768, None)

def print_background():
    screen.blit(background, (0, 0))

def print_tela():
    for i in [1, 0]:
        for obj in lista_obj[i]:
            if(obj.image != None):
                screen.blit(obj.image, obj.position)
    pygame.display.update()

def game_restart():
    del lista_obj[0][:]
    del lista_obj[1][:]
    del funcoes_update[:]
    inicializa_mapa()

def get_joystick_input(i):
    try:
        joystick[i].dispatch_events()
    except:
        pass
    for event in pygame.event.get():
        if event.type == JOYAXISMOTION:
            if event.axis == 5:
                joystick_commands[i]["R_trigger"] = event.value
            elif event.axis == 0:
                joystick_commands[i]["y_axis"] = event.value * -1
            elif event.axis == 1:
                joystick_commands[i]["x_axis"] = event.value
        elif event.type == JOYBUTTONDOWN:
            if event.button == 0:
                joystick_commands[i]["A"] = 1
            if event.button == 1:
                joystick_commands[i]["B"] = 1
            if event.button == 2:
                joystick_commands[i]["X"] = 1
            if event.button == 3:
                joystick_commands[i]["Y"] = 1
        elif event.type == JOYBUTTONUP:
            if event.button == 0:
                joystick_commands[i]["A"] = 0
            if event.button == 1:
                joystick_commands[i]["B"] = 0
            if event.button == 2:
                joystick_commands[i]["X"] = 0
            if event.button == 3:
                joystick_commands[i]["Y"] = 0

clock = pygame.time.Clock()
lista_obj = [[], []]
funcoes_update = []
pygame.font.init()
joystick_commands = [{"R_trigger": 0, "A": 0, "B": 0, "X": 0, "Y": 0, "Start": 0, "x_axis": 0, "y_axis": 0},
                     {"R_trigger": 0, "A": 0, "B": 0, "X": 0, "Y": 0, "Start": 0, "x_axis": 0, "y_axis": 0}]

inicializa_mapa()
while(1):
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
    get_joystick_input(0)
    for funcao in funcoes_update:
        funcao()

    pressed_keys = pygame.key.get_pressed()
    if (pressed_keys[K_LCTRL] or pressed_keys[K_RCTRL]) and pressed_keys[K_r]:
        game_restart()
    clock.tick(30)