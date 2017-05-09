import pygame
from pygame.locals import *
from sys import exit
from operator import attrgetter
import time
import xinput
import random
import queue
from threading import Thread, RLock

lock = RLock()

def worker():
    while True:
        q.get()()
        q.task_done()

screen_x = 1280
screen_y = 768

green = Color('#00FF00')
"""Inicializar o pygame"""

pygame.mixer.pre_init(44100, 32, 2, 4096)
pygame.init()
pygame.mixer.init(44100, -16, 2, 2048)
screen = pygame.display.set_mode((screen_x, screen_y), 0, 32)
pygame.display.set_caption('Mario')
menufont = pygame.font.Font("SuperMarioBros.ttf", 90)
gamefont = pygame.font.Font("SuperMarioBros.ttf", 70)
myfont = pygame.font.Font("SuperMarioBros.ttf", 30)

pygame.joystick.init()
joysticks = xinput.XInputJoystick.enumerate_devices()
device_numbers = list(map(attrgetter('device_number'), joysticks))
joystick = [None, None]
if device_numbers:
    joystick[0] = xinput.XInputJoystick(device_numbers[0])
    if len(device_numbers) > 1:
        joystick[1]  = xinput.XInputJoystick(device_numbers[1])

try:
    sheet = pygame.image.load('sprites.png')
    background = pygame.image.load('background.png').convert()
    back_menu = pygame.image.load('back_menu.png').convert()
    mario_wins = pygame.image.load('mario_wins.png').convert()
    luigi_wins = pygame.image.load('luigi_wins.png').convert()
    draw_round = pygame.image.load('draw_round.png').convert()
    jump_sound = pygame.mixer.Sound('Jump.wav')
    coin_sound = pygame.mixer.Sound('Coin.wav')
    bomb_sound = pygame.mixer.Sound('Bomb.wav')
    death_sound = pygame.mixer.Sound('Death.wav')
    mush_sound = pygame.mixer.Sound('Mush_up.wav')
    pause_sound = pygame.mixer.Sound('Pause.wav')
except:
    print("Erro: Arquivo não encontrado. Certifique-se de que todos estão na mesma pasta do jogo")
    exit()

grav = 1
bomb_time = 3.5
jump_speed = 17
max_mana = 1500
mana_per_coin = 350
mana_gain_per_tick = 2
mana_cost_per_tick = 25
player_speed = 5
player_acceleration = 0.1
player_max_speed = 8

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
    with lock:
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

class Option():
    def __init__(self, label, option):
        self.label = label
        self.option = option
    def choose(self, last_menu):
        if self.option.__class__.__name__ == 'Menu':
            funcoes_update.append(self.option.update)
            self.option.last_menu = last_menu
        else:
            self.option()

class Menu():
    def __init__(self, *args):
        self.selected = 0
        self.options = []
        self.num_options = 0
        self.button_pressed = 1
        for option in args:
            self.options.append(option)
            self.num_options += 1
        self.last_menu = None

    def update(self):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_UP] or pressed_keys[K_w] or joystick_commands[0]['y_axis'] > 0.2 or joystick_commands[1]['y_axis'] > 0.2:
            if  not self.button_pressed:
                self.selected = (self.selected - 1)%self.num_options
                self.button_pressed = 1
        elif pressed_keys[K_DOWN] or pressed_keys[K_s] or joystick_commands[0]['y_axis'] < -0.2 or joystick_commands[1]['y_axis'] < -0.2:
            if not self.button_pressed:
                self.selected = (self.selected + 1)%self.num_options
                self.button_pressed = 1
        elif pressed_keys[K_RETURN] or pressed_keys[K_SPACE] or joystick_commands[0]['A']or joystick_commands[1]['A'] :
            if not self.button_pressed:
                self.button_pressed = 1
                self.options[self.selected].choose(self)
                funcoes_update.remove(self.update)
        elif pressed_keys[K_ESCAPE] or pressed_keys[K_BACKSPACE] or joystick_commands[0]['B'] or joystick_commands[1]['B']:
            if not self.button_pressed:
                if self.last_menu != None:
                    funcoes_update.append(self.last_menu.update)
                    funcoes_update.remove(self.update)
                self.button_pressed = 1
        else:
            self.button_pressed = 0
        self.print()

    def print(self):
        screen.blit(back_menu, (0, 0))
        i = 0
        for opt in self.options:
            label = menufont.render(str(opt.label), 1, (0, 0,255*(self.selected == i)))
            screen.blit(label, ((screen_x - menufont.size(opt.label)[0])/2, screen_y/2 - 75*self.num_options + 150*i + (150 - menufont.size(opt.label)[1])/2))
            i += 1

class Bloco():
    """Essa classe é usada para criar um bloco qualquer no jogo"""
    def __init__(self, positionx, positiony, sizex, sizey, image, explosivo = 0, lista = 0):
        self.collision_coefficient = [0, 0]
        self.list_index = lista
        self.position = [float(positionx), float(positiony)]
        self.sizex = sizex
        self.sizey = sizey
        self.image = image
        self.explosivo = explosivo
        lista_obj[lista].append(self)
        self.speed = [float(0), float(0)]
        self.last_update = time.clock()

    def get_rect(self):
        """Retorna o retangulo correspondente a posicao do bloco"""
        return Rect(int(self.position[0]),
                    int(self.position[1]),
                    int(self.sizex),
                    int(self.sizey))

    def explode(self):
        lista_obj[self.list_index].remove(self)
        try:
            funcoes_update.remove(self.update)
        except:
            pass
        try:
            funcoes_update.remove(self.update_position)
        except:
            pass
        return 1

    def collision(self, who_triggers):
        return 0

    def update_position(self, companion = None):
        with lock:
            if self.list_index == 0:
                x = collides(self, lista_obj[0])
                if x:
                    print(self.get_rect()[0],self.get_rect()[1],self.get_rect()[2],self.get_rect()[3], self.__class__.__name__)
                    print(x.get_rect()[0],x.get_rect()[1],x.get_rect()[2],x.get_rect()[3], x.__class__.__name__)
                    #raise()
            self.speed[1] += grav*deltat*30
            for axis in range(2):
                avanco = self.speed[axis]*deltat*30
                if avanco > 0.5 or avanco < -0.5:
                    self.position[axis] += signal(avanco)
                    if companion != None:
                        companion.position[axis] += signal(avanco)
                    self.trigger_events()
                    x = collides(self, lista_obj[0])
                    if x != 0:
                        self.collision(x)
                        self.position[axis] -= signal(avanco)
                        if companion != None:
                            companion.position[axis] -= signal(avanco)
                        self.speed[axis] = self.collision_coefficient[axis]* self.speed[axis]
                        avanco = 0
                    avanco -= signal(avanco)

                if avanco > 0.5 or avanco < -0.5:
                    self.position[axis] += avanco
                    if companion != None:
                        companion.position[axis] += avanco
                    if collides(self, lista_obj[0]) != 0:
                        self.position[axis] -= avanco
                        if companion != None:
                            companion.position[axis] -= avanco
                    else:
                        avanco = 0
                        self.trigger_events()

                while avanco > 0.5 or avanco < -0.5:
                    self.position[axis] += signal(avanco)
                    if companion != None:
                        companion.position[axis] += signal(avanco)
                    self.trigger_events()
                    x = collides(self, lista_obj[0])
                    if x != 0:
                        self.collision(x)
                        self.position[axis] -= signal(avanco)
                        if companion != None:
                            companion.position[axis] -= signal(avanco)
                        self.speed[axis] = self.collision_coefficient[axis]* self.speed[axis]
                        break
                    avanco -= signal(avanco)

    def trigger_events(self):
        x = collides(self, lista_obj[1])
        anterior = None
        with lock:
            while  x != 0:
                if x.collision(self) == 1:
                    x = collides(self, lista_obj[1], anterior)
                else:
                    anterior = x
                    x = collides(self, lista_obj[1], anterior)

class Cogumelo(Bloco):
    def __init__(self, positionx, positiony, vel = 0):
        super().__init__(positionx, positiony, 32, 32, clip_sheet([594, 0, 32, 32]), 1, 1)
        self.speed[0] = vel
        self.collision_coefficient = [-1, 0]
        funcoes_update.append(self.update_position)

    def  collision(self, who_triggers):
        used = 0
        try:
            who_triggers.grow()
            used = 1
            lista_obj[1].remove(self)
            funcoes_update.remove(self.update_position)
        except:
            pass
        return used

class Box(Bloco):
    def __init__(self, positionx, positiony, content = "Coin", qtd = 1):
        positions = [(98, 0, 32, 32), (132, 0, 32, 32), (166, 0, 32, 32), (328, 0, 32, 32)]
        self.sprite = []
        for i in range(len(positions)):
            self.sprite.append(clip_sheet(positions[i]))
        self.sprite_index = 0
        super().__init__(positionx, positiony, 32, 32, self.sprite[self.sprite_index], 1)
        self.ticks_to_change = 5
        self.content = content
        self.qtd = qtd
        funcoes_update.append(self.update)
        self.trig = BoxTrigger(self)

    def update(self):
        if self.sprite_index < 3:
            if self.ticks_to_change == 0:
                self.ticks_to_change = 5
                self.sprite_index = (self.sprite_index + 1) % 3
                self.image = self.sprite[self.sprite_index]
            else:
                self.ticks_to_change -= 1

    def trigger(self, who_triggers):
        self.sprite_index = 3
        self.image = self.sprite[3]
        lista_obj[1].remove(self.trig)
        funcoes_update.remove(self.update)
        self.explosivo = 0
        if(self.content == "Coin"):
            try:
                who_triggers.coins += 1
                coin_sound.play()
            except:
                pass
            Animacao_Moeda(self.position[0], self.position[1] - 32)
        elif(self.content == "Cogumelo"):
            Cogumelo(self.position[0], self.position[1] - 32, random.choice([-4, 4]))
        elif(self.content == "Bomb"):
            funcoes_update.append(self.spawn_items)

    def spawn_items(self):
        if self.content == "Bomb":
            with lock:
                bomba = Bomb(self.position[0], self.position[1] - 32, random.choice([-4, 4]), 1)
                if collides(bomba, lista_obj[0]) != 0:
                    bomba.remove()
                else:
                    self.qtd -= 1
                    funcoes_update.append(bomba.update)
                    bomba.dragger = Dragger(bomba)
                    lista_obj[0].append(bomba)

        if self.qtd == 0:
            funcoes_update.remove(self.spawn_items)

    def explode(self):
        lista_obj[1].remove(self.trig)
        funcoes_update.remove(self.update)
        self.explosivo = 0
        self.sprite_index = 3
        self.image = self.sprite[3]
        return 0

class Box_headbuttable(Bloco):
    def __init__(self, positionx, positiony):
        super().__init__(positionx, positiony, 32, 32, clip_sheet([560, 0, 32, 32]), 1)
        self.trig = BoxTrigger(self)

    def trigger(self, who_triggers):
        self.explode()
        who_triggers.speed[1] = 0

    def explode(self):
        lista_obj[1].remove(self.trig)
        lista_obj[0].remove(self)
        return 1

class BoxTrigger(Bloco):
    def __init__(self, box):
        self.mybox = box
        super().__init__(self.mybox.position[0] + 1, self.mybox.position[1] + 31, 30, 1, None, 0, 1)


    def collision(self, who_triggers):
        self.mybox.trigger(who_triggers)
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
    def __init__(self, positionx, positiony, vx = 0, imaginario = 0):
        super().__init__(positionx + 1, positiony - 16, 30, 48, clip_sheet([360, 0, 30, 48]), 1)
        self.raio_de_explosao = 60
        self.spawned_time = last_time
        self.collision_coefficient = [-1, -0.5]
        self.speed[0] = vx
        if not imaginario:
            self.dragger = Dragger(self)
            funcoes_update.append(self.update)
        else:
            lista_obj[0].remove(self)

    def update(self):
        self.dragger.cont = 0
        if last_time - self.spawned_time >= bomb_time:
            self.detonate()
        self.update_position(self.dragger)

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
        try:
            funcoes_update.remove(self.update)
            lista_obj[0].remove(self)
            lista_obj[1].remove(self.dragger)
        except:
            pass

class Explosao(Bloco):
    def __init__(self, myBomb):
        super().__init__(myBomb.position[0] - 60, myBomb.position[1] - 60, 120 + myBomb.sizex, 120 + myBomb.sizey, None, 0, 1)
        lista_obj[1].remove(self)

class Dragger(Bloco):
    def __init__(self, myobj):
        self.myobj = myobj
        self.cont = 0
        super().__init__(self.myobj.position[0], self.myobj.position[1] + 1, 30, 47, None, 0, 1)

    def collision(self, who_triggers):
        self.cont += 1
        if self.cont <= 6:
            if (who_triggers != self.myobj and who_triggers != self):
                with lock:
                    if who_triggers.position[0] < self.position[0]:
                        self.position[0] += 1
                        self.myobj.position[0] += 1
                        self.trigger_events()
                        if collides(self.myobj, lista_obj[0]) != 0:
                            self.position[0] -= 1
                            self.myobj.position[0] -= 1
                    else:
                        self.position[0] -= 1
                        self.myobj.position[0] -= 1
                        self.trigger_events()
                        if collides(self.myobj, lista_obj[0]) != 0:
                            self.position[0] += 1
                            self.myobj.position[0] += 1
        return 0

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
        positions = [[(0, 0, 28, 40), (32, 0, 30, 38), (64, 0, 32, 44), (628, 0, 30, 28), (0, 180, 30, 56), (34, 180, 32, 54), (68, 180, 32, 62), (102, 180, 32, 30)],
                     [(0, 130, 28, 40), (32, 130, 30, 38), (64, 130, 32, 44), (98, 130, 30, 28), (0, 250, 30, 56), (34, 250, 32, 54), (68, 250, 32, 62), (102, 250, 32, 30)]]         #representa a posicao e o tamanho das sprites na sprite sheet
        self.sprite = [[], []]
        self.orientation = 1
        self.sprite_index = 2                                                       #inicia com a sprite do Mario pulando
        for j in range(2):
            for i in range(len(positions[j])):
                self.sprite[j].append(clip_sheet(positions[j][i])) # Extract the sprite you want
        super().__init__(posx, posy, self.sprite[self.player][self.sprite_index].get_rect()[2], self.sprite[self.player][self.sprite_index].get_rect()[3],
                         pygame.transform.flip(self.sprite[self.player][self.sprite_index], self.orientation, grav < 0), 1, 0)
        self.controlling_grav = 0
        self.bomb_button_hold = 0
        self.buy_button_hold = 0
        self.mana = max_mana
        self.grande = 0
        self.coins = 0
        self.bombs = bombs_per_player
        self.ticks_to_change = 5
        self.change_pending = self.sprite_index
        self.ticks_to_stop = 0
        self.is_dead = 0
        funcoes_update.append(self.update_player)
        funcoes_update.append(self.print_info)

    def esta_no_chao(self):
        """Retorna 1 se o objeto está em contato com alguma superfícia abaixo"""
        self.position[1] += grav
        x = collides(self, lista_obj[0])
        self.position[1] -=grav
        if x == 0:
            return x
        else:
            return 1

    def get_inputs(self):
        pressed_keys = pygame.key.get_pressed()
        global grav

        if (pressed_keys[comandos[self.player]['Comprar Mana']] or joystick_commands[self.player]['B'] > 0.1) and self.mana < max_mana and self.coins and not self.buy_button_hold:
            self.buy_button_hold = 1
            self.controlling_grav = 1
            self.coins -= 1
            self.mana += mana_per_coin
            if self.mana >= max_mana:
                self.mana = max_mana
        elif not (pressed_keys[comandos[self.player]['Comprar Mana']] or joystick_commands[self.player]['B'] > 0.1):
            self.buy_button_hold = 0

        if (pressed_keys[comandos[self.player]['Poder']] or joystick_commands[self.player]['L_trigger'] > 0.1) and self.mana >= mana_cost_per_tick:
            self.controlling_grav = 1
            self.mana -= mana_cost_per_tick
            grav = -1*grav*signal(grav)
        else:
            if self.controlling_grav:
                self.controlling_grav = 0
                grav = grav*signal(grav)

        if grav > 0:
            if pressed_keys[comandos[self.player]['Abaixa']] or joystick_commands[self.player]['y_axis'] < -0.2:
                self.isdown = 1
            else:
                self.isdown = 0
            if (pressed_keys[comandos[self.player]['Pula']]or joystick_commands[self.player]['A']) and self.esta_no_chao():
                self.speed[1] = -jump_speed * grav
                jump_sound.play()
        else:
            if pressed_keys[comandos[self.player]['Pula']] or joystick_commands[self.player]['y_axis'] > 0.2:
                self.isdown = 1
            else:
                self.isdown = 0
            if (pressed_keys[comandos[self.player]['Abaixa']] or joystick_commands[self.player]['A']) and self.esta_no_chao():
                self.speed[1] = -jump_speed * grav
                jump_sound.play()

        if pressed_keys[comandos[self.player]['Esquerda']]or joystick_commands[self.player]['x_axis'] < -0.2:
            if self.speed[0] > -1*player_speed:
                self.speed[0] = -player_speed
            self.orientation = 0
        elif pressed_keys[comandos[self.player]['Direita']] or joystick_commands[self.player]['x_axis'] > 0.2:
            if self.speed[0] < player_speed:
                self.speed[0] = player_speed
            self.orientation = 1
        else:
            self.speed[0] = 0

        if pressed_keys[comandos[self.player]['Corre']] or joystick_commands[self.player]['R_trigger'] > 0:
            self.speed[0] += player_acceleration*signal(self.speed[0])
            if self.speed[0] > player_max_speed or self.speed[0] < -1*player_max_speed:
                self.speed[0] = signal(self.speed[0])* player_max_speed

        if (pressed_keys[comandos[self.player]['Bomba']] or joystick_commands[self.player]['X']) and self.bombs > 0 and not self.bomb_button_hold:
            self.bomb_button_hold = 1
            if self.orientation == 0:
                bomba = Bomb(self.position[0] - 32, self.position[1] - (48-self.sizey))
            else:
                bomba = Bomb(self.position[0] + self.sizex, self.position[1] - (48-self.sizey))
            if collides(bomba, lista_obj[0]) != 0:
                bomba.remove()
            else:
                self.bombs -= 1
        elif not (pressed_keys[comandos[self.player]['Bomba']] or joystick_commands[self.player]['X']):
            self.bomb_button_hold = 0

    def change_sprite(self, new):
        self.change_pending = new
        """Essa função não é tão trivial. Quando a sprite muda, o seu tamanho também pode mudar, causando problemas de colisão."""
        old = self.sprite_index
        self.sprite_index = new
        self.ticks_to_change = 8

        posx = self.position[0]
        posy = self.position[1]
        self.sizey = self.sprite[self.player][new].get_rect()[3]
        if grav == 1:
            self.position[1] -= self.sprite[self.player][new].get_rect()[3] -  self.sprite[self.player][old].get_rect()[3]  #mantém a a borda inferior da sprite no mesmo lugar
        contador = 0
        while collides(self, lista_obj[0]):
            contador += 1
            self.position[1] += grav
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
            if self.isdown:
                self.change_sprite(3)
            elif self.sprite_index == 3:
                self.change_sprite(0)
            if not self.esta_no_chao():
                self.change_sprite(2)
            elif (self.sprite_index == 0 or self.sprite_index == 1) and self.speed[0] != 0:
                self.ticks_to_change -= 1
                if self.ticks_to_change == 0:
                    self.change_sprite(1 - self.sprite_index)
            else:
                self.ticks_to_change = 8
                if self.sprite_index == 1:          #speed == 0
                    self.change_sprite(0)
                elif self.sprite_index == 2 and self.esta_no_chao():
                    self.change_sprite(0)
        else:
            if self.isdown:
                self.change_sprite(7)
            elif self.sprite_index == 7:
                self.change_sprite(4)
            elif not self.esta_no_chao():
                self.change_sprite(6)
            elif (self.sprite_index == 4 or self.sprite_index == 5) and self.speed[0] != 0:
                self.ticks_to_change -= 1
                if self.ticks_to_change == 0:
                    self.change_sprite(9 - self.sprite_index)
            else:
                self.ticks_to_change = 8
                if self.sprite_index == 5:          #speed == 0
                    self.change_sprite(4)
                elif self.sprite_index == 6 and self.esta_no_chao():
                    self.change_sprite(4)

        self.image = pygame.transform.flip(self.sprite[self.player][self.sprite_index], self.orientation, grav < 0)

    def update_player(self):
        self.mana += mana_gain_per_tick
        if self.mana > max_mana:
            self.mana = max_mana
        self.took_damage = 0
        self.get_inputs()
        self.update_position()
        self.update_sprite()

    def explode(self):
        return self.damage()

    def stop_vibration(self):
        self.ticks_to_stop -= 1
        if self.ticks_to_stop == 0:
            try:
                joystick[self.player].set_vibration(0, 0)
            except:
                pass
            finally:
                funcoes_update.remove(self.stop_vibration)

    def grow(self):
        mush_sound.play()
        self.grande = 1
        if self.sprite_index < 4:
            self.change_sprite(self.sprite_index + 4)

    def damage(self, critic = 0):
        global grav
        if self.took_damage == 0:
            try:
                if self.ticks_to_stop == 0:
                    joystick[self.player].set_vibration(1, 1)
                    funcoes_update.append(self.stop_vibration)
                    self.ticks_to_stop = 35
            except:
                pass

            if self.grande and not critic:
                self.grande = 0
                if self.sprite_index >= 3:
                    self.change_sprite(self.sprite_index - 3)
            else:
                self.is_dead = 1
                death_sound.play()
                if self.controlling_grav:
                    grav = signal(grav)*grav
                funcoes_update.remove(self.update_player)
                lista_obj[0].remove(self)
                return 1
            self.took_damage = 1
        return 0

    def print_info(self):
        label = myfont.render(str(self.coins), 1, (0, 0, 0))
        label2 = myfont.render(str(self.bombs), 1, (0, 0, 0))
        if self.player == 0:
            screen.blit(label, (65, 30))
            screen.blit(label2, (165, 30))
            screen.blit(clip_sheet([302, 0, 24, 32]), [30, 27])
            screen.blit(clip_sheet([360, 0, 30, 48]), [130, 12])
            screen.fill(green, Rect(30, 70, (int)(self.mana*150/max_mana),32))
        else:
            screen.blit(label, (1135, 30))
            screen.blit(label2, (1235, 30))
            screen.blit(clip_sheet([302, 0, 24, 32]), [1100, 27])
            screen.blit(clip_sheet([360, 0, 30, 48]), [1200, 12])
            screen.fill(green, Rect(1255 - (int)(self.mana*150/max_mana), 70, (int)(self.mana*150/max_mana),32))

class Temporary_Screen():
    def __init__(self, image, caption, color = (0, 0, 0), tempo = 150):
        self.image = image
        self.t0 = time.clock()
        self.tempo = tempo
        self.caption = caption
        self.color = color
        funcoes_update.append(self.update)

    def update(self):
        self.tempo -= 1
        screen.blit(self.image, (0, 0))
        label = gamefont.render(self.caption, 1, self.color)
        screen.blit(label, ((screen_x - gamefont.size(str(self.caption))[0])/2, (screen_y - gamefont.size(str(self.caption))[1])/2))
        if self.tempo < 0:
            funcoes_update.remove(self.update)
            funcoes_update.append(main_menu.update)

def inicializa_mapa(mapa):
    funcoes_update.append(print_background)
    """Inicializar o cenário"""
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
                Box_headbuttable(32*j, 32*i)
            elif linhas[i][j] == 'M':
                mario = Player(32*j, 32*i)
            elif linhas[i][j] == 'L':
                luigi = Player(32*j, 32*i, 1)
            elif linhas[i][j] == '*':
                Box(32*j, 32*i, random.choice(["Coin", "Bomb", "Cogumelo"]), 5)
            elif linhas[i][j] == 'B':
                Box(32*j, 32*i)
            elif linhas[i][j] == 'Z':
                Box(32*j, 32*i, "Cogumelo")
            elif linhas[i][j] == 'W':
                Box(32 * j, 32 * i, "Bomb", 10)
            elif linhas[i][j] == 'C':
                Coin(32*j, 32*i)
            elif linhas[i][j] == 'Y':
                Cogumelo(32*j, 32*i)
            elif linhas[i][j] == 'F':
                Lava(32 * j, 32 * i)
            elif linhas[i][j] == 'X':
                Bomb(32*j, 32*i)
    funcoes_update.append(print_tela)
    Bloco(0,-200, 1280, 100, None)
    Bloco(1280, -200, 100, 968, None)
    Bloco(-100, -200, 100, 968, None)
    return mario, luigi

def inicializa_jogo():
    mapa  = open('stage.txt', 'r')
    inicializa_mapa(mapa)
    mapa.close()

def print_background():
    screen.blit(background, (0, 0))

def print_tela():
    for i in [1, 0]:
        for obj in lista_obj[i]:
            if(obj.image != None):
                screen.blit(obj.image, obj.position)

def game_restart():
    global grav
    del lista_obj[0][:]
    del lista_obj[1][:]
    del funcoes_update[:]
    grav = signal(grav) * grav

def get_joystick_input(i):
    try:
        joystick[i].dispatch_events()
    except:
        pass
    for event in pygame.event.get():
        if event.type == JOYAXISMOTION:
            if event.axis == 5:
                joystick_commands[i]["R_trigger"] = event.value
            elif event.axis == 2:
                joystick_commands[i]["L_trigger"] = event.value
            elif event.axis == 0:
                joystick_commands[i]["y_axis"] = event.value
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

def start_coin_rush():
    global t0
    global bombs_per_player

    bombs_per_player = 5
    t0 = time.clock()
    mapa  = open('coin_rush.txt', 'r')
    inicializa_mapa(mapa)
    mapa.close()
    funcoes_update.append(update_coin_rush)

def armageddon():
    if random.randrange(1, int(2/deltat)) == 1:
        with lock:
            bomba = Bomb(random.randrange(0, 1250), -50, random.randrange(-6, 6), 1)
            if collides(bomba, lista_obj[0]) != 0:
                bomba.remove()
            else:
                funcoes_update.append(bomba.update)
                bomba.dragger = Dragger(bomba)
                lista_obj[0].append(bomba)

def update_coin_rush():
    tempo = str(int(100-2*(time.clock()- t0)))
    label = gamefont.render(tempo, 1, (0, 0, 0))
    screen.blit(label, ((screen_x - gamefont.size(tempo)[0])/2, 30))

def start_arena():
    global t0
    global bombs_per_player
    global mario, luigi
    global chuva_de_bombas
    chuva_de_bombas = 0
    bombs_per_player = 10
    t0 = time.clock()
    mapa  = open('arena.txt', 'r')
    mario, luigi = inicializa_mapa(mapa)
    mapa.close()
    funcoes_update.append(update_arena)

def update_arena():
    global chuva_de_bombas
    label = gamefont.render("Fight!", 1, (0, 0, 0))
    screen.blit(label, ((screen_x - gamefont.size("Fight!")[0])/2, 30))
    tempo = int(50-2*(time.clock()- t0))
    if tempo > 0:
        label = myfont.render(str(tempo), 1, (0, 0, 0))
        screen.blit(label, ((screen_x - myfont.size(str(tempo))[0])/2, 100))
    elif chuva_de_bombas == 0:
        chuva_de_bombas = 1
        funcoes_update.append(armageddon)
    if mario.is_dead and not luigi.is_dead:
        game_restart()
        funcoes_update.append(mario.stop_vibration)
        funcoes_update.append(luigi.stop_vibration)
        mario.ticks_to_stop = 35
        luigi.ticks_to_stop = 35
        Temporary_Screen(luigi_wins, "Luigi wins!", (255, 0, 0))
        ##mario wins
    elif luigi.is_dead and not mario.is_dead:
        game_restart()
        funcoes_update.append(mario.stop_vibration)
        funcoes_update.append(luigi.stop_vibration)
        mario.ticks_to_stop = 35
        luigi.ticks_to_stop = 35
        Temporary_Screen(mario_wins, "Mario wins!")
        #luigi wins
    elif mario.is_dead:
        game_restart()
        funcoes_update.append(mario.stop_vibration)
        funcoes_update.append(luigi.stop_vibration)
        mario.ticks_to_stop = 35
        luigi.ticks_to_stop = 35
        Temporary_Screen(draw_round, "It's a draw :/")
        #empate

bombs_per_player = 5

q = queue.Queue()
clock = pygame.time.Clock()
lista_obj = [[], []]
funcoes_update = []

comandos = [{"Pula": K_UP, "Abaixa": K_DOWN, "Direita": K_RIGHT, "Esquerda": K_LEFT, "Bomba": K_1, "Poder": K_0, "Comprar Mana": K_2, "Corre": K_RCTRL, "Pause": K_ESCAPE},
            {"Pula": K_w, "Abaixa": K_s, "Direita": K_d, "Esquerda": K_a, "Bomba":K_e, "Poder": K_SPACE, "Comprar Mana": K_q, "Corre": K_RSHIFT, "Pause":K_ESCAPE}]

joystick_commands = [{"L_trigger": 0, "R_trigger": 0, "A": 0, "B": 0, "X": 0, "Y": 0, "Start": 0, "x_axis": 0, "y_axis": 0},
                     {"L_trigger": 0, "R_trigger": 0, "A": 0, "B": 0, "X": 0, "Y": 0, "Start": 0, "x_axis": 0, "y_axis": 0}]

option4 = Option("op4", None)
option5 = Option("op5", None)
option6 = Option("op6", None)
menu1 = Menu(option4, option5, option6)
play = Option("Play", inicializa_jogo)
coin_rush = Option("Coin Rush", start_coin_rush)
arena = Option("Arena", start_arena)
option3 = Option("op3", menu1)
main_menu = Menu(arena, coin_rush, play, option3)
funcoes_update.append(main_menu.update)

last_time = time.clock()

for i in range(1):                                                                                                      #número de Threads usadas
     t = Thread(target=worker)
     t.daemon = True
     t.start()

while(1):
    deltat = time.clock() - last_time
    last_time = time.clock()
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
    get_joystick_input(0)
    get_joystick_input(1)

    for funcao in funcoes_update:
        q.put(funcao)

    pressed_keys = pygame.key.get_pressed()
    if (pressed_keys[K_LCTRL] or pressed_keys[K_RCTRL]) and pressed_keys[K_r]:
        game_restart()
        funcoes_update.append(main_menu.update)
    q.join()
    pygame.display.update()
    clock.tick(50)