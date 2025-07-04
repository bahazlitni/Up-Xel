import pygame, time
from pygame import gfxdraw
import math
import psutil
import shutil
import json
import sys
import os
from pathlib import Path, PurePosixPath

def resource(rel_path):
    base = getattr(sys, "_MEIPASS", Path(__file__).parent)
    return os.fspath(Path(base) / PurePosixPath(rel_path))

def userdata(rel_path):
    exe_dir = Path(sys.executable).parent
    target  = exe_dir / PurePosixPath(rel_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    return target

transparent_white   =   (255, 255, 255, 127)
transparent_green   =   (112, 223,  32, 127)
light_green         =   (183, 239, 143, 255)
light_grey          =   (200, 200, 200, 255)
light_black         =   ( 43,  43,  43, 255)
light_red           =   (218, 107,  99, 255)
dark_grey           =   ( 63,  63,  63, 255)
dark_red            =   (126,  47,  42, 255)
white               =   (255, 255, 255, 255)
grey                =   (127, 127, 127, 255)
green               =   (112, 223, 32 , 255)
blue                =   ( 63,  63, 255, 255)
red                 =   (255,  90,  80, 255)
transparent         =   (255, 255, 255,   0)
black               =   (  0,   0,   0, 255)
transparent_black   =   (  0,   0,   0, 127)
none                =   (  0,   0,   0,   0)

pygame.mixer.pre_init(44100, -16, 2, 4096)
pygame.init()

def loadData():
    try:
        datafile = open(userdata('career/data.txt'), 'r')
        data = json.load(datafile)
        shutil.copyfile(userdata('career/data.txt'), userdata('career/data_0.txt'), follow_symlinks=True)
        datafile.close()
    except Exception:
        resetfile = open(userdata('career/data_0.txt'), 'r')
        data = json.load(resetfile)
        resetfile.close()
    return data

def save():
    with open(userdata('career/data.txt'), 'w') as writefile:
        json.dump(data, writefile)

data = loadData()

#Video Settings
fps = data['fps']
width = data['width']
height = int(width * 0.8)
button_height = height*0.1
window = pygame.display.set_mode((width, height))
pygame.display.set_caption('Client')
rate = pygame.time.Clock()
switch_rate = pygame.time.Clock()

#layers
layer1 = pygame.Surface((width, height), pygame.SRCALPHA)
layer2 = pygame.Surface((width, height), pygame.SRCALPHA)
#career data
current_chapter = len(data['chapters'])-1
current_level = len(data['chapters'][current_chapter])-1

def load_map(map_file):
    game_map = []
    for line in list(map_file):
        game_map.append(list(line.strip('\n')))
    map_file.close()
    game_map.reverse()
    return game_map

def get_level_specs(ch, lv):
    with open(resource('career/chapter{}/level{}.txt'.format(ch+1, lv+1)), 'r') as map_file:
        specs={}
        this_level_map = load_map(map_file)
        coins_counter = 0
        count_line = 0
        block_size = round(width/len(this_level_map[0]), 0)
        for line in this_level_map:
            count_line += 1
            coins_counter += line.count('2')
            if '-' in line:
                break
        specs['block_size'] = block_size
        specs['total_coins'] = coins_counter
        specs['map_height'] = (count_line)*block_size
        return specs

def refresh_career(current_chapter, current_level):
    ch = len(data['chapters'])-1
    lv = len(data['chapters'][ch])-1
    
    specs = get_level_specs(ch, lv)
    data['chapters'][ch][lv]['map_height'] =  specs['map_height']
    data['chapters'][ch][lv]['total_coins'] =  specs['total_coins']
    data['chapters'][ch][lv]['block_size'] =  specs['block_size']
    
    if ch < current_chapter:
        specs = get_level_specs(current_chapter, 0)
        data['chapters'].append([{'percentage':0, 'score':0, 'coins':0, 'attempts':0, 
        'total_coins': specs['total_coins'], 'map_height': specs['map_height'], 'block_size': specs['block_size']}])
    if lv < current_level:
        specs = get_level_specs(ch, current_level)
        data['chapters'][ch].append({'percentage':0, 'score':0, 'coins':0, 'attempts':0, 
        'total_coins': specs['total_coins'], 'map_height': specs['map_height'], 'block_size': specs['block_size']})
    save()
    
def reset_career():
    global current_level
    global current_chapter
    global data
    specs = get_level_specs(0, 0)
    current_level = 0
    current_chapter = 0
    with open(resource('career/reset-data.txt'), 'r') as resetfile:
        data = json.load(resetfile)
    data['chapters'][0][0]['percentage'] =  0
    data['chapters'][0][0]['map_height'] =  specs['map_height']
    data['chapters'][0][0]['total_coins'] =  specs['total_coins']
    data['chapters'][0][0]['block_size'] =  specs['block_size']

refresh_career(current_chapter, current_level)

#Sound user data
master_volume = int(data['sound'][0])
music_volume = int(data['sound'][1])
sfx_volume = int(data['sound'][2])
def sound_value(sound):
    return round(sound*master_volume/10000, 4)

#Text
font_size = int(width * 0.0333)
font_small_size =int(width * 0.015)
font_medium_size = int(width * 0.025)
font = pygame.font.Font(resource('fonts/ka1.ttf'), font_size)
font_small = pygame.font.Font(resource('fonts/ka1.ttf'), font_medium_size)
poppins = pygame.font.Font(resource('fonts/poppins-bold.ttf'), font_size)
poppins_small = pygame.font.Font(resource('fonts/poppins-bold.ttf'), font_small_size)



#Animationi
def sequence(self, length, extension, size):
    sequence = []
    size = int(size)
    for i in range(length):
        sequence.append(pygame.transform.smoothscale(pygame.image.load(resource('images/{}/Group {}.{}'.format(self, i, extension))).convert_alpha(), (size, size)))
    for i in range(len(sequence)):
        sequence.append(pygame.transform.smoothscale(pygame.image.load(resource('images/{}/Group {}.{}'.format(self, i, extension))).convert_alpha(), (size, size)))
    return sequence

#In-Game
multiplayer = data['multiplayer']
deaths = 0

#Loading images
main_menu_bg = pygame.transform.smoothscale(pygame.image.load(resource('images/background.jpg')), (width, height)).convert()
background = pygame.transform.smoothscale(pygame.image.load(resource('images/background-blur.jpg')), (width, height)).convert()

#Loading sounds
game_start_sound = pygame.mixer.Sound(resource('sound/sfx/game_start.wav'))
alert_sfx = pygame.mixer.Sound(resource('sound/sfx/alert.wav'))
coin_sfx = pygame.mixer.Sound(resource('sound/sfx/coin.wav'))
game_start_sound.set_volume(sound_value(sfx_volume))

'''PLAYER'''
class player(object):
    def __init__(self, surface, skin, x, y, up, ability, left, down, right):
        self.surface = surface
        self.x = x
        self.y = y
        self.width = width*0.025
        self.height = width*0.025
        self.skin = pygame.transform.smoothscale(skin, (int(self.width), int(self.height)))
        
        self.boost_time = 0
        self.slow_time = 0
        self.boost_activated = False
        self.slow_activated = False
        self.boost_x = 1.000
        self.boost_y = 1.025
        self.speed_x = width*0.185*self.boost_x
        self.speed_y = width*0.185*self.boost_y
        
        self.up = up
        self.ability = ability
        self.left = left
        self.down = down
        self.right = right
        
        self.death = False
        self.container = pygame.Rect(0, 0, 0, 0)
        self.x_limit = (1, surface.get_width()- self.width - 1)
        self.y_limit = (1, surface.get_height()- self.height - 1)
        self.is_moving = False
        self.distance_traveled = 0
        
    def move(self, game_level, dt):
        if not(self.death):
            self.speed_x = width*0.185*self.boost_x
            self.speed_y = width*0.185*self.boost_y
            self.is_moving = False
            old_x = self.x
            old_y = self.y
            if pygame.key.get_pressed()[self.up] and self.y  > self.y_limit[0]:
                self.y -= self.speed_y*dt
                self.is_moving = True
            if pygame.key.get_pressed()[self.left] and self.x > self.x_limit[0]:
                self.x -= self.speed_x*dt
                self.is_moving = True
            if pygame.key.get_pressed()[self.down] and self.y  < self.y_limit[1]:
                self.y += self.speed_y*dt
                self.is_moving = True
            if pygame.key.get_pressed()[self.right] and self.x < self.x_limit[1]:
                self.x += self.speed_x*dt
                self.is_moving = True
                
            if self.is_moving:
                self.distance_traveled = (math.sqrt((self.x-old_x)**2 + (self.y-old_y)**2)*(self.speed_x+self.speed_y)/2)/rate.get_fps()
            else:
                self.distance_traveled = 0
                
            self.container = pygame.Rect(self.x, self.y, self.width, self.height)
            self.surface.blit(self.skin, (self.x, self.y))
            
            if game_level > 2:
                if self.boost_activated:
                    boost_delay = time.time() - self.boost_time
                    if boost_delay < 6:
                        self.boost_y = -(boost_delay**2)/32 + 3*boost_delay/16 + 1.025
                        self.boost_x = self.boost_y*1.5 - 0.025
                    elif boost_delay > 6:
                        self.boost_y = 1.025
                        self.boost_x = 1.000
                        self.boost_activated = False
                if self.slow_activated:
                    slow_delay = time.time() - self.slow_time
                    if slow_delay < 4:
                        self.boost_y = (slow_delay**2)/8 - slow_delay/2 + 1.025
                        self.boost_x = self.boost_y - 0.025
                    elif slow_delay > 4:
                        self.boost_y = 1.025
                        self.boost_x = 1.000
                        self.slow_activated = False
        else:
            self.travel = 0
            self.container = pygame.Rect(0, 0, 0, 0)


'''In-Game Objects'''
class element(object):
    def __init__(self, display, width, height):
        self.display = display
        self.width = width
        self.height = height
        self.container = pygame.Rect(0, 0, 0, 0)
    def define(self, surface, x, y):
        self.container = pygame.Rect(x, y + velocity, self.width, self.height)

'''GUI'''
class image(object):
    def __init__(self, file, position, x, y, width, height, scale, bg_color, bg_hover_color, convert_alpha=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.bg_color_stored = bg_color
        self.bg_hover_color = bg_hover_color
        
        self.scale = scale
        self.image_width = self.width*scale
        self.image_height = self.height*scale
        self.file = file
        img = pygame.image.load(self.file)
        if convert_alpha: img = img.convert_alpha()
        self.image = pygame.transform.smoothscale(img, (int(self.image_width), int(self.image_height)))

        self.container = pygame.Rect(self.x, self.y, self.width, self.height)
        self.position = position
        self.hover = False
        self.selected = False
    def display(self, surface):
        try:
            bg = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            bg.fill(self.bg_color)
            surface.blit(bg, (self.x, self.y))
        except Exception:
            pass
        surface.blit(self.image, (self.x + (self.width - self.image_width)/2, self.y + (self.height - self.image_height)/2))
        mx, my = pygame.mouse.get_pos()
        if self.container.collidepoint((mx, my)):
            self.hover = True
            if self.bg_hover_color != None:
                self.bg_color = self.bg_hover_color
        else:
            if self.bg_hover_color != transparent:
                self.bg_color = self.bg_color_stored
            self.hover = False

class text(object):
    def __init__(self, font, x, y, width, height, bg_color, bg_hover_color, margin, align, text_color):
        self.font = font
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.margin = margin
        self.align = align
        self.bg_color = bg_color
        self.bg_hover_color = bg_hover_color
        self.bg_color_stored = bg_color
        self.container = pygame.Rect(self.x, self.y, self.width, self.height)
        self.hover = False
        self.selected = False
        self.text_color = text_color
    def display(self, surface, txt):
        text = self.font.render(txt, True, self.text_color)
        text_w = text.get_width()
        text_h = text.get_height()
        try:
            bg = pygame.Surface((self.width, self.height))
            bg.fill((self.bg_color[0], self.bg_color[1], self.bg_color[2]))
            bg.set_alpha(self.bg_color[3])
            surface.blit(bg, (self.x, self.y))
        except Exception:
            pass
        if self.align == 'center':
            surface.blit(text, (self.x + self.width/2 - text_w/2, self.y + self.height/2 - text_h/2))
        elif self.align == 'left':
            surface.blit(text, (self.x + self.margin, self.y + self.height/2 - text_h/2))
        elif self.align == 'right':
            surface.blit(text, (self.x + self.width - self.margin - text_w, self.y + self.height/2 - text_h/2))
        elif self.align == 'top-center':
            surface.blit(text, (self.x + self.width/2 - text_w/2, self.y + self.margin))
        mx, my = pygame.mouse.get_pos()
        if self.container.collidepoint((mx, my)):
            self.hover = True
            if self.bg_hover_color != None:
                self.bg_color = self.bg_hover_color
        else:
            if self.bg_hover_color != transparent:
                self.bg_color = self.bg_color_stored
            self.hover = False
        if self.selected:
            self.bg_color = green


#previous_button
show_fps = text(poppins_small, width*0.02, 0, width*0.07, height*0.025, black, None, width*0.005, 'left', white)
show_cpu = text(poppins_small, show_fps.x + show_fps.width, 0, width*0.09, height*0.025, black, None, width*0.005, 'left', white)

previous = image(resource('images/previous.png'), 'fit', width/8 - height*0.05, height*0.1, height*0.1, height*0.1, 1, white, light_grey)
title = text(font, width/4, height*0.1, width/2, height*0.1, white, None, 0, 'center', red)

'''Verified'''
play = text(font, width*0.6 - width/6, height*0.2, width/3 - width*0.1, 0.1*height, white, green, 0, 'center', red)
go = text(font, width*0.5 - width/6, height*0.2, width*0.09, height*0.1, green, red, 0, 'center', light_black)
options = text(font, width*0.5 - width/6, height*0.375, width/3, 0.1*height, white, green, 0, 'center', red)
skins = text(font, width*0.5 - width/6, height*0.55, width/3, 0.1*height, white, green, 0, 'center', red)
exit_button = text(font, width*0.5 - width/6, height*0.8, width/3, 0.075*height, white, green, 0, 'center', red)  
press_space = text(poppins_small, width*0.5 - width/6, height*0.2 + go.height, go.width, height*0.02, None, None, 0, 'left', green)
def mainmenu():
    status = True
    while status:
        global current_level
        window.blit(main_menu_bg, (0, 0))
        play.display(window, 'play')
        go.display(window, 'Go')
        press_space.display(window, 'Lv{} > {}'.format(current_level+1, pygame.key.name(data['game_controls']['start'])))
        options.display(window, 'options')
        skins.display(window, 'skins')
        exit_button.display(window, 'exit')
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    status = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if pygame.key.get_pressed()[data['game_controls']['start']]:
                        status = False
                        with open(resource('career/chapter{}/level{}.txt'.format(current_chapter+1, current_level+1)), 'r') as current_map_file:
                            gameplay(load_map(current_map_file), current_level, current_chapter)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if play.hover:
                            status = False
                            level_menu()
                        elif go.hover:
                            status = False
                            with open(resource('career/chapter{}/level{}.txt'.format(current_chapter+1, current_level+1)), 'r') as current_map_file:
                                gameplay(load_map(current_map_file), current_level, current_chapter)
                        elif options.hover:
                            status = False
                            options_menu()
                        elif skins.hover:
                            status = False
                            skins_menu()
                        elif exit_button.hover:
                            status = False
                            pygame.quit()
                            sys.exit()
        pygame.display.update()
        rate.tick(60)



class level(object):
    def __init__(self, font, width, height, unlocked_color, locked_color, bg_hover_color):

        self.font = font
        
        self.width = width
        self.height = height

        self.unlocked_color = unlocked_color
        self.locked_color = locked_color
        self.bg_hover_color = bg_hover_color
        self.icon = pygame.transform.smoothscale(pygame.image.load(resource('images/locked.png')).convert_alpha(), (int(self.width/3), int(self.width/3)))
        
        self.bg_color = None
        self.bg_color_stored = None
            
        self.hover = False
        
    def display(self, surface, x, y, txt, locked):
        if not(locked):
            self.bg_color = self.unlocked_color
            self.bg_color_stored = self.bg_color
            
            self.container = pygame.Rect(x, y, self.width, self.height)
            
            mx, my = pygame.mouse.get_pos()
            if self.container.collidepoint((mx, my)):
                self.hover = True
                if self.bg_hover_color != None:
                    self.bg_color = self.bg_hover_color
                
            else:
                if self.bg_hover_color != transparent:
                    self.bg_color = self.bg_color_stored
                self.hover = False
                
            content = self.font.render(txt, True, self.locked_color)
            bg = pygame.Surface((self.width, self.height))
        else:
            self.bg_color = self.locked_color
            content = self.icon
            self.container = pygame.Rect(x, y, self.width, self.height) 
            bg = pygame.Surface((self.width, self.width))

        bg.fill(self.bg_color)
        surface.blit(bg, (x, y))
        
        surface.blit(content, (x + self.width/2 - content.get_width()/2, y + self.height/2 - content.get_height()/2))



class bar(object):
    def __init__(self, width, height, value_color, rest_color):
        self.width = width
        self.height = height
        self.value_color = value_color
        self.rest_color = rest_color
    def display(self, surface, x, y, value):
        value_width = round(value/100*self.width, 2)
        bg = pygame.Surface((self.width, self.height))
        bg_value = pygame.Surface((value_width, self.height))
        bg.fill(self.rest_color)
        bg_value.fill(self.value_color)
        surface.blit(bg, (x, y))
        surface.blit(bg_value, (x, y))

class card(object):
    def __init__(self, x, y, width, height, bg_color=transparent):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.surface = pygame.Surface(x, y, width, height)


'''level_menu components'''
level_height = width*0.1375
level_width = width*0.15
column1 = width*0.25
column2 = width*0.425
column3 = width*0.6
row1 = height*0.25
row2 = height*0.475
row3 = height*0.7
positions = [(column1, row1), (column2, row1), (column3, row1), (column1, row2), (column2, row2), (column3, row2), (column1, row3), (column2, row3), (column3, row3)]

#self, font, width, height, unlocked_color, locked_color, bg_hover_color, align
level_box = level(font, level_width, level_height, green, red, light_green)
level_bar = bar(level_box.width, height*0.01, green, red)
level_bar_y = level_width - level_bar.height + 1
#self, font, x, y, width, height, bg_color, bg_hover_color, margin, align
reset = text(poppins_small, width*0.1, height*0.9, width*0.05, height*0.05, red, black, 0, 'center', light_black)
warning = text(poppins, width *2.5/12, height/3, width * 7/12, height * 1/3, red, None, width*0.05, 'top-center', white)
line1 = text(poppins_small, width* 2.5/12, height/3, width * 7/12, height * 1/3, None, None, 0, 'center', white)
line2 = text(poppins_small, width * 2.5/12, height/3 + height*0.025, width * 7/12, height * 1/3, None, None, 0, 'center', white)
yes = text(poppins_small, width*0.325, height*0.6, width*0.15, height*0.05, black, light_black, 0, 'center', red)
no = text(poppins_small, width*0.525, height*0.6, width*0.15, height*0.05, green, light_black, 0, 'center', black)
def level_menu():
    status = True
    global data
    alert_sfx.set_volume(sound_value(sfx_volume))
    window.blit(background, (0, 0))
    chapter = 0
    reset_clicked = False
    while status:
        window.blit(background, (0, 0))
        global click
        global current_level
        global current_chapter
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                status = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button:
                    click = True
                    if previous.hover:
                        status = False
                        mainmenu() 
                    elif reset.hover:
                        alert_sfx.play()
                        reset_clicked = True
                
        reset.display(window, 'RESET')  
        previous.display(window)   
        
        if reset_clicked == False:
            #level::self, surface, x, y, txt, locked
            title.display(window, 'Chapter {}'.format(chapter+1))
            for i in range(9):
                if i <= current_level:
                    level_box.display(window, positions[i][0], positions[i][1], str(i+1), False)
                    level_bar.display(window, positions[i][0], positions[i][1] + level_bar_y, data['chapters'][chapter][i]['percentage'])
                else:
                    level_box.display(window, positions[i][0], positions[i][1], str(i+1), True)
                if level_box.hover and click:
                    with open(resource('career/chapter{}/level{}.txt'.format(chapter+1, i+1)), 'r') as this_level:
                        status = False
                        gameplay(load_map(this_level), i, chapter)
                        
        
        elif reset_clicked:
            window.convert()
            warning.display(window, 'Reset the game ?')
            line1.display(window, 'Please notice that all chapters and levels would be reset')
            line2.display(window, 'including all game\'s data.')
            yes.display(window, 'YES')
            no.display(window, 'NO')
            if no.hover and click:
                reset_clicked = False
            elif yes.hover and click:
                reset_career()
                save()
                reset_clicked = False
                
        pygame.display.update()
        rate.tick(60)



'''Verified'''
#font, x, y, width, height, bg_color, bg_hover_color, margin, padding, align
career = text(font, width/4, height*0.1, width/2, height*0.1, white, blue, 0, 'center', red)
players = text(font, width/4, height*0.3, width/2, height*0.1, white, blue, 0, 'center', red)
sound = text(font, width/4, height*0.5, width/2, height*0.1, white, blue, 0, 'center', red)
video = text(font, width/4, height*0.7, width/2, height*0.1, white, blue, 0, 'center', red) 
def options_menu():
    status = True
    window.blit(background, (0, 0))  
    while status:
        global multiplayer
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                status = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if previous.hover:
                        status = False
                        mainmenu()
                    elif players.hover:
                        status = False
                        players_menu()
                    elif career.hover:
                        status = False
                        career_menu()
                    elif sound.hover:
                        status = False
                        sound_menu()
                    elif video.hover:
                        status = False
                        video_menu()
        previous.display(window)
        career.display(window, 'View Career')
        players.display(window, 'Players Settings')
        sound.display(window, 'Sound Settings')
        video.display(window, 'Video Settings')
        pygame.display.update()
        rate.tick(60)
        
player1_select = True
player2_select = False
column1 = width/4
column2 = width*19/36
stats_y = height/4
stats_width = width/2     

player1_career = text(font, column1, previous.y, width*2/9, button_height, white, light_grey, 0, 'center', dark_grey)
player2_career = text(font, column2, previous.y, width*2/9, button_height, white, light_grey, 0, 'center', dark_grey)

attempts_career = text(poppins, column1, stats_y, stats_width, button_height*0.75, transparent_black, transparent_white, width*0.05, 'left', white)
attempts_career_stat = text(poppins, column1, attempts_career.y, stats_width, button_height*0.75, transparent, None, width*0.05, 'right', white)
attempts_career_bar = bar(stats_width, height*0.01, green, black)

coins_career = text(poppins, column1, stats_y*1.4, stats_width, button_height*0.75, transparent_black, transparent_white, width*0.05, 'left', white)
coins_career_stat = text(poppins, column1, coins_career.y, stats_width, button_height*0.75, transparent, transparent, width*0.05, 'right', white)
coins_career_bar = bar(stats_width, height*0.01, green, black)

score_career = text(poppins, column1, stats_y*1.8, stats_width, button_height*0.75, transparent_black, transparent_white, width*0.05, 'left', white)
score_career_stat = text(poppins, column1, score_career.y, stats_width, button_height*0.75, transparent, transparent, width*0.05, 'right', white)
score_career_bar = bar(stats_width, height*0.01, green, black)

distance_career = text(poppins, column1, stats_y*2.2, stats_width, button_height*0.75, transparent_black, transparent_white, width*0.05, 'left', white)
distance_career_stat = text(poppins, column1, distance_career.y, stats_width, button_height*0.75, transparent, transparent, width*0.05, 'right', white)
#distance_career_bar = bar(stats_width, height*0.01, black, black)

#ratings
attempts_career_rating = text(poppins, attempts_career.x-button_height*0.75-width*0.005, stats_y, button_height*0.75, button_height*0.75, transparent_black, None, 0, 'center', white)
coins_career_rating = text(poppins, attempts_career_rating.x, coins_career.y, attempts_career_rating.width, attempts_career_rating.height, transparent_black, None, 0, 'center', white)
score_career_rating = text(poppins, coins_career_rating.x, score_career.y, coins_career_rating.width, coins_career_rating.height, transparent_black, None, 0, 'center', white)

def rgb_hue(color):
    r = color[0]
    g = color[1]
    b = color[2]
    try:
        R = r/255
        G = g/255
        B = b/255
        max_var = max(r/255, g/255, b/255)
        min_var = min(r/255, g/255, b/255)
        if max_var == R:
            hue = ((G-B)/(max_var-min_var))*60
        elif max_var == G:
            hue = (2 + (B-R)/(max_var-min_var))*60
        elif max_var == B:
            hue = (4 + (R-G)/(max_var-min_var))*60
    except Exception:
        hue = 0
    return hue

def getRatingSymbol(i):
    if i <  0: return 'F'
    if i > 14: return 'Z'
    'DCBAS'[i//3] + ('-', '', '+')[i%3]

def getAttemptsPointsRating(x):
    if x <= 0 or x >= 3.5: return '?'
    return getRatingSymbol(round(-2*math.log(3.5/x - 1) + 7, 0))


def smart_career_stats(player):
    default = {
        'attempts_color'         : black, 
        'coins_color'            : black, 
        'score_color'            : black, 
        'score_bar_value'        : 100, 
        'attempts_bar_value'     : 100, 
        'coins_bar_value'        : 100, 
        'attempts_career_comment': '?', 
        'coins_career_comment'   : '?', 
        'score_career_comment'   : '?',
    }

    if player['distance_traveled'] <= 0: return

    total_career_levels = (current_chapter)*9 + current_level + 1
    total_career_coins = 0
    total_career_maps_height = 0
    level_not_checked = total_career_levels
     
    for ch in range(current_chapter+1):
        if level_not_checked//9 > 0:
            for i in range(len(data['chapters'][ch])):
                total_career_coins += data['chapters'][ch][i]['total_coins']
                total_career_maps_height += data['chapters'][ch][i]['map_height']
        else:
            if current_level > 0:
                for i in range(len(data['chapters'][ch])-1):
                    total_career_coins += data['chapters'][ch][i]['total_coins']
                    total_career_maps_height += data['chapters'][ch][i]['map_height']
            else:
                total_career_coins += data['chapters'][ch][0]['total_coins']
                total_career_maps_height += data['chapters'][ch][0]['map_height']
        level_not_checked -= 1
        
    #attempts_color
    if player['attempts'] > 0:
        attempts_points = player['distance_traveled']/((player['attempts']/total_career_levels + 1)*(total_career_maps_height*0.1*player['attempts']))
        default['attempts_color'] = (max(int(255 - 255*attempts_points/2), 0), min(int(255*attempts_points), 255), 0)
        default['attempts_bar_value'] = round(1-(rgb_hue(default['attempts_color'])/rgb_hue((0, 255, 0))), 2)*100
        if default['attempts_bar_value'] < 0:
            default['attempts_bar_value'] *= -1
    else:
        attempts_points = 3.25
        default['attempts_bar_value'] = 100
        default['attempts_color'] = (0, 255, 0)
    
    default['attempts_career_comment'] = getAttemptsPointsRating(14)
   
        
    if player['coins'] > 0:
        coins_points = player['coins']/(total_career_coins-player['coins'])
        default['coins_color'] = (max(int(255 - 255*coins_points), 0), min(int(255*coins_points), 255), 0)
        default['coins_bar_value'] = round(coins_points, 2)*100     
        
        if coins_points > 0.92:                
            default['coins_career_comment'] = 'S+'
        elif coins_points > 0.86:
            default['coins_career_comment'] = 'S'
        elif coins_points > 0.8:
            default['coins_career_comment'] = 'S-'
        elif coins_points > 0.74:
            default['coins_career_comment'] = 'A+'
        elif coins_points > 0.68:
            default['coins_career_comment'] = 'A'
        elif coins_points > 0.62:
            default['coins_career_comment'] = 'A-'
        elif coins_points > 0.58:
            default['coins_career_comment'] = 'B+'
        elif coins_points > 0.54:
            default['coins_career_comment'] = 'B'
        elif coins_points > 0.5:
            default['coins_career_comment'] = 'B-'
        elif coins_points > 0.46:
            default['coins_career_comment'] = 'C+'
        elif coins_points > 0.42:
            default['coins_career_comment'] = 'C'
        elif coins_points > 0.36:
            default['coins_career_comment'] = 'C-'
        elif coins_points > 0.3:
            default['coins_career_comment'] = 'D+'
        elif coins_points > 0.24:
            default['coins_career_comment'] = 'D'
        elif coins_points > 0.18:
            default['coins_career_comment'] = 'D-'
        elif coins_points < 0.12:
            default['coins_career_comment'] = '!'
            
        if player['attempts'] > 0:
            score_points = attempts_points*coins_points
            default['score_color'] = (max(int(255 - 255*score_points/2), 0), min(int(255*score_points/2), 255), 0)
            if default['score_bar_value'] < 0:
                default['score_bar_value'] *= -1
            if score_points > 2.75:
                default['score_career_comment'] = 'S+'
            elif score_points > 2.25:
                default['score_career_comment'] = 'S'
            elif score_points > 1.75:
                default['score_career_comment'] = 'S-'
            elif score_points > 1.45:
                default['score_career_comment'] = 'A+'
            elif score_points > 1.1:
                default['score_career_comment'] = 'A'
            elif score_points > 0.6:
                default['score_career_comment'] = 'A-'
            elif score_points > 0.475:
                default['score_career_comment'] = 'B+'
            elif score_points > 0.375:
                default['score_career_comment'] = 'B'
            elif score_points > 0.3:
                default['score_career_comment'] = 'B-'
            elif score_points > 0.225:
                default['score_career_comment'] = 'C+'
            elif score_points > 0.175:
                default['score_career_comment'] = 'C'
            elif score_points > 0.125:
                default['score_career_comment'] = 'C-'
            elif score_points > 0.1:
                default['score_career_comment'] = 'D+'
            elif score_points > 0.075:
                default['score_career_comment'] = 'D'
            elif score_points > 0.05:
                default['score_career_comment'] = 'D-'
            elif score_points < 0.025:
                default['score_career_comment'] = '!'
            default['score_bar_value'] = round(rgb_hue(default['score_color'])/rgb_hue((0, 255, 0)), 2)*100
            if default['score_bar_value'] < 0:
                default['score_bar_value'] *= -1
    #score color

    default['attempts_alpha_color'] = (default['attempts_color'][0],
    default['attempts_color'][1], default['attempts_color'][2], 127)
    default['coins_alpha_color'] = (default['coins_color'][0], 
    default['coins_color'][1], default['coins_color'][2], 127)
    default['score_alpha_color'] = (default['score_color'][0], 
    default['score_color'][1], default['score_color'][2], 127)
    
    score_value = round(player['score'], 1)
    if score_value > 1000:
        default['score_text'] = '{} K'.format(round(score_value/1000, len(str(int(score_value)))-1))
    else:
        default['score_text'] = str(score_value)

    return default

        
def career_menu():
    status = True
    stats_p1 = smart_career_stats(data['player1'])
    stats_p2 = smart_career_stats(data['player2'])
    window.blit(background, (0, 0))
    attempts_bar_value = 0
    coins_bar_value = 0 
    while status:
        global player1_select
        global player2_select

        window.blit(background, (0, 0))
        previous.display(window)
        player1_career.display(window, 'Player1')
        player2_career.display(window, 'Player2')

        if player1_select:
            x = player1_career.x
            stats = stats_p1
            player_data = data['player1']
        if player2_select:
            x = player2_career.x
            stats = stats_p2
            player_data = data['player2']
            
        attempts_value = player_data['attempts']
        attempts_bar_value = stats['attempts_bar_value']
        attempts_career_bar.value_color = stats['attempts_color']
        attempts_career.bg_hover_color = stats['attempts_alpha_color']
        attempts_career_text = stats['attempts_career_comment']
        attempts_career_rating.bg_color = stats['attempts_alpha_color']
        
        coins_value = player_data['coins']
        coins_bar_value = stats['coins_bar_value']
        coins_career_bar.value_color = stats['coins_color']
        coins_career.bg_hover_color = stats['coins_alpha_color']
        coins_career_text = stats['coins_career_comment']
        coins_career_rating.bg_color = stats['coins_alpha_color']
        
        score_bar_value = stats['score_bar_value']
        score_career_bar.value_color = stats['score_color']
        score_career.bg_hover_color = stats['score_alpha_color']
        score_career_text = stats['score_career_comment']
        score_career_rating.bg_color = stats['score_alpha_color']
        score_value = stats['score_text']
        
        distance_value = int(player_data['distance_traveled']/5)
            
        attempts_career.display(window, 'Attempts')
        attempts_career_stat.display(window, '{}'.format(attempts_value))
        attempts_career_bar.display(window, attempts_career.x, attempts_career.y+attempts_career.height + 1, attempts_bar_value)
        attempts_career_rating.display(window, attempts_career_text)
        
        coins_career.display(window, 'Coins')
        coins_career_stat.display(window, f'{coins_value}')
        coins_career_bar.display(window, coins_career.x, coins_career.y+coins_career.height + 1, coins_bar_value)
        coins_career_rating.display(window, coins_career_text)
        
        score_career.display(window, 'Score')
        score_career_stat.display(window, score_value)
        score_career_bar.display(window, score_career.x, score_career.y+score_career.height + 1, score_bar_value)
        score_career_rating.display(window, score_career_text)
        
        distance_career.display(window, 'Distance')
        distance_career_stat.display(window, str(distance_value))
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return   
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if previous.hover:
                        options_menu()
                        status = False
                    player1_select = player1_career.hover
                    player2_select = player2_career.hover
                        
        pygame.draw.rect(window, green, (x, player1_career.y + player1_career.height + height*0.01, player1_career.width, height*0.005))
        pygame.display.update()
        rate.tick(60)
   
class control(text):
    def set_control(self, source, target):
        if self.hover:
            selected = True
            while selected:
                global status
                try:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            try:
                                if source == 'player_controls':
                                    if player1_select:
                                        data['player1']['controls'][target] = event.key
                                    elif player2_select:
                                        data['player2']['controls'][target] = event.key
                                elif source == 'game_controls':
                                    data['game_controls'][target] = event.key
                                save()
                            except Exception:
                                pass
                            selected = False
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:
                                selected = False
                except Exception:
                    pass
        
'''Verified'''
control_y = height*0.44
control_x = width/3
margin_control = width/3*0.125 + width/12
row1 = previous.y
row2 = height/4

single = text(font, column1, row1, width*2/9, button_height, white, light_grey, 0, 'center', dark_grey)
duo = text(font, column2, row1, width*2/9, button_height, white, light_grey, 0, 'center', dark_grey)

player1_control = text(font, column1, row2, width*2/9, button_height, white, light_grey, 0, 'center', dark_grey)
player2_control = text(font, column2, row2, width*2/9, button_height, white, light_grey, 0, 'center', dark_grey)

pause_control = control(poppins, control_x, control_y, button_height, button_height, red, blue, 0, 'center', dark_grey)
pause_text = text(poppins_small, pause_control.x, pause_control.y + pause_control.height, pause_control.width, margin_control - pause_control.height, transparent, None, 0, 'center', white)

up_control = control(poppins, control_x + margin_control, control_y, button_height, button_height, white, blue, 0, 'center', dark_grey)
up_text = text(poppins_small, up_control.x, up_control.y + up_control.height, up_control.width, margin_control - up_control.height, transparent, None, 0, 'center', white)

ability_control = control(poppins, control_x + margin_control*2, control_y, button_height, button_height, green, blue, 0, 'center', dark_grey)
ability_text = text(poppins_small, ability_control.x, ability_control.y + ability_control.height, ability_control.width, margin_control - ability_control.height, transparent, None, 0, 'center', white)

left_control = control(poppins, control_x, control_y + margin_control, button_height, button_height, white, blue, 0, 'center', dark_grey)
left_text = text(poppins_small, left_control.x + left_control.width, left_control.y, margin_control - left_control.width, left_control.height, transparent, None, 0, 'center', white)

down_control = control(poppins, control_x + margin_control, control_y + margin_control, button_height, button_height, white, blue, 0, 'center', dark_grey)

right_control = control(poppins, control_x + margin_control*2, control_y + margin_control, button_height, button_height, white, blue, 0, 'center', dark_grey)
right_text = text(poppins_small, down_control.x + down_control.width, down_control.y, margin_control - down_control.width, down_control.height, transparent, None, 0, 'center', white)

start_control = control(poppins, control_x, control_y + margin_control*2, width/3, button_height, green, blue, 0, 'center', dark_grey)
start_text = text(poppins_small, start_control.x, start_control.y + start_control.height, start_control.width, start_control.height/3, transparent, None, 0, 'center', white)

def players_menu():
    status = True
    window.blit(background, (0, 0))
    while status:
        global multiplayer
        global player1_select
        global player2_select
        window.blit(background, (0, 0))
        
       
    
        previous.display(window)
        single.display(window, 'SOLO')
        duo.display(window, 'DUO')
        player1_control.display(window, 'Player1')
        player2_control.display(window, 'Player2')
        pause_text.display(window, 'pause')
        up_text.display(window, '^')
        ability_text.display(window, 'ability')
        left_text.display(window, '<')
        right_text.display(window, '>')
        start_text.display(window, 'start game')
    
        if not multiplayer:
            single.bg_color = green
            single.text_color = white
            duo.bg_color = white
            duo.text_color = light_black
        elif multiplayer:
            single.bg_color = white
            single.text_color = light_black
            duo.bg_color = green
            duo.text_color = white
        if player1_select:
            x = player1_control.x
            up_control.display(window, pygame.key.name(data['player1']['controls']['up'])[0:3])
            ability_control.display(window, pygame.key.name(data['player1']['controls']['ability'])[0:3])
            left_control.display(window, pygame.key.name(data['player1']['controls']['left'])[0:3])
            down_control.display(window, pygame.key.name(data['player1']['controls']['down'])[0:3])
            right_control.display(window, pygame.key.name(data['player1']['controls']['right'])[0:3])
            
        elif player2_select:
            x = player2_control.x
            up_control.display(window, pygame.key.name(data['player2']['controls']['up'])[0:3])
            ability_control.display(window, pygame.key.name(data['player2']['controls']['ability'])[0:3])
            left_control.display(window, pygame.key.name(data['player2']['controls']['left'])[0:3])
            down_control.display(window, pygame.key.name(data['player2']['controls']['down'])[0:3])
            right_control.display(window, pygame.key.name(data['player2']['controls']['right'])[0:3])
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                status = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if previous.hover:
                        options_menu()
                        status = False
                    elif single.hover:
                        multiplayer = False
                    elif duo.hover:
                        multiplayer = True
                    elif player1_control.hover:
                        player1_select = True
                        player2_select = False
                    elif player2_control.hover:
                        player1_select = False
                        player2_select = True
                    else:
                        pause_control.set_control('game_controls', 'pause')
                        up_control.set_control('player_controls', 'up')
                        ability_control.set_control('player_controls', 'ability')
                        left_control.set_control('player_controls', 'left')
                        down_control.set_control('player_controls', 'down')
                        right_control.set_control('player_controls', 'right')
                        start_control.set_control('game_controls', 'start')
                        
        
        pause_control.display(window, pygame.key.name(data['game_controls']['pause'])[0:3])
        start_control.display(window, pygame.key.name(data['game_controls']['start']))
        pygame.draw.rect(window, green, (x, player1_control.y + player1_control.height + height*0.01, player1_control.width, height*0.005))
        
        pygame.display.update()
        rate.tick(60)
    data['multiplayer'] = multiplayer
    save()

'''Verified'''
def draw_circle(surface, x, y, radius, color):
    gfxdraw.aacircle(surface, x, y, radius, color)
    gfxdraw.filled_circle(surface, x, y, radius, color)
class slider():
    def __init__(self, x, y, width, height, parent_y, parent_height, value_color, rest_color, value):
        self.width = width
        self.height = height
        self.x = x
        self.y = y - self.height/2
        self.value = value
        self.value_color = value_color
        self.rest_color = rest_color
        self.parent_y = parent_y
        self.parent_height = parent_height
        self.radius = int(width*0.015)
        self.circle_x = 0
        self.circle_y = int(y - self.radius/2 + self.height/2)
        self.hover = False
        self.onclick = False
    def display(self, surface):
        if self.value > 100:
            self.value = 100
        elif self.value < 0:
            self.value = 0
        bg = pygame.Surface((self.width, self.height))
        bg.fill(self.rest_color)
        surface.blit(bg, (self.x, self.y))
        try:
            value_width = round(self.value/100*self.width, 2)
            bg_value = pygame.Surface((value_width, self.height))
            bg_value.fill(self.value_color)
            surface.blit(bg_value, (self.x, self.y))
        except Exception:
            self.value = 0
            self.rect_x = self.x
        mx, my = pygame.mouse.get_pos()
        if self.onclick:
            if mx < self.x:
                self.value = 0
            elif mx < self.x + self.width:
                self.value = ((mx - self.x)*100)/self.width
            else:
                self.value = 100   
        draw_circle(surface, int(self.x + value_width), self.circle_y, self.radius, white)
#font, x, y, width, height, bg_color, bg_hover_color, margin, padding, align
master = text(poppins, width/8 - previous.image.get_width()/2, height*0.3, width - (width/8 - previous.image.get_width()/2)*2, height*0.1, transparent, transparent_black, width*0.01, 'left', white)
music = text(poppins, width/8 - previous.image.get_width()/2, height*0.45, width - (width/8 - previous.image.get_width()/2)*2, height*0.1, transparent, transparent_black, width*0.01, 'left', white)
sfx = text(poppins, width/8 - previous.image.get_width()/2, height*0.6, width - (width/8 - previous.image.get_width()/2)*2, height*0.1, transparent, transparent_black, width*0.01, 'left', white)
master_value = text(poppins, master.x + master.width - width*0.1, master.y, width*0.1, master.height, transparent, transparent_black, 0, 'center', white)
music_value = text(poppins, music.x + music.width - width*0.1, music.y, width*0.1, music.height, transparent, transparent_black, 0, 'center', white)
sfx_value = text(poppins, sfx.x + sfx.width - width*0.1, sfx.y, width*0.1, sfx.height, transparent, transparent_black, 0, 'center', white)
master_bar = slider(width/4, master.y + master.height/2, width/2, height*0.0075, master.y, master.height, green, red, master_volume)
music_bar = slider(width/4, music.y + music.height/2, width/2, height*0.0075, music.y, music.height, green, red, music_volume)
sfx_bar = slider(width/4, sfx.y + sfx.height/2, width/2, height*0.0075, sfx.y, sfx.height, green, red, sfx_volume)
def sound_menu():
    status = True
    window.blit(background, (0, 0))
    while status:
        global master_volume
        global music_volume
        global sfx_volume
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                status = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if previous.hover:
                        status = False
                        options_menu()
                    elif master.hover:
                        master_bar.onclick = True
                    elif music.hover:
                        music_bar.onclick = True
                    elif sfx.hover:
                        sfx_bar.onclick = True
                elif event.button == 4:
                    if master.hover:
                        master_bar.value += 5
                    elif music.hover:
                        music_bar.value += 5
                    elif sfx.hover:
                        sfx_bar.value += 5 
                elif event.button == 5:
                    if master.hover:
                        master_bar.value -= 5
                    elif music.hover:
                        music_bar.value -= 5
                    elif sfx.hover:
                        sfx_bar.value -= 5 
            elif event.type == pygame.MOUSEBUTTONUP:
                sfx_bar.onclick = False
                music_bar.onclick = False
                master_bar.onclick = False
        #+15% CPU USAGE!
        window.blit(background, (0, 0))
        previous.display(window)
        title.display(window, 'Sound Settings')
        master.display(window, 'Master')
        master_bar.display(window)
        master_value.display(window, str(int(master_bar.value)))
        music.display(window, 'Music')
        music_bar.display(window)
        music_value.display(window, str(int(music_bar.value)))
        sfx.display(window, 'SFX')
        sfx_bar.display(window)
        sfx_value.display(window, str(int(sfx_bar.value)))
        master_volume = int(master_bar.value)
        music_volume = int(music_bar.value)
        sfx_volume = int(sfx_bar.value)
        pygame.display.update()
        rate.tick(60)
    data['sound'][0] = master_volume
    data['sound'][1] = music_volume
    data['sound'][2] = sfx_volume
    save()

'''Verified'''
frames = text(poppins, width*0.25, height*0.24, width*0.15, height*0.1, transparent, None, 0, 'left', white)
fps_button = text(poppins_small, width*0.6, frames.y + frames.height/4, width*0.15, frames.height/2, white, light_grey, 0, 'center', light_black)
fps60 = text(font, width*0.25, height*0.33, width*0.15, height*0.1, white, light_grey, 0, 'center', light_black)
fps90 = text(font, width*0.425, height*0.33, width*0.15, height*0.1, white, light_grey, 0, 'center', light_black)
fps120 = text(font, width*0.6, height*0.33, width*0.15, height*0.1, white, light_grey, 0, 'center', light_black)
fps144 = text(font, width*0.25, height*0.45, width*0.15, height*0.1, white, light_grey, 0, 'center', light_black)
fps240 = text(font, width*0.425, height*0.45, width*0.15, height*0.1, white, light_grey, 0, 'center', light_black)
unlimited_fps = text(font, width*0.6, height*0.45, width*0.15, height*0.1, white, light_grey, 0, 'center', light_black)

if fps == 60:
    fps60.selected = True
elif fps == 90:
    fps90.selected = True
elif fps == 120:
    fps120.selected = True
elif fps == 144:
    fps144.selected = True
elif fps == 240:
    fps240.selected = True
elif fps == 999:
    unlimited_fps.selected = True
    
resolutions = text(poppins, width*0.25, height*0.57, width*0.15, height*0.1, transparent, None, 0, 'left', white)
x810 = text(font_small, width*0.25, height*0.66, width*0.15, height*0.1, white, light_grey, 0, 'center', light_black)
x1080 = text(font_small, width*0.425, height*0.66, width*0.15, height*0.1, white, light_grey, 0, 'center', light_black)
x1200 = text(font_small, width*0.6, height*0.66, width*0.15, height*0.1, white, light_grey, 0, 'center', light_black)
x1350 = text(font_small, width*0.25, height*0.78, width*0.15, height*0.1, white, light_grey, 0, 'center', light_black)
x1620 = text(font_small, width*0.425, height*0.78, width*0.15, height*0.1, white, light_grey, 0, 'center', light_black)
x2160 = text(font_small, width*0.6, height*0.78, width*0.15, height*0.1, white, light_grey, 0, 'center', light_black)
cpu_usage_button = text(poppins_small, width*0.6, resolutions.y + resolutions.height/4, width*0.15, resolutions.height/2, white, light_grey, 0, 'center', light_black)


if width == 810:
    x810.selected = True
elif width == 1080:
    x1080.selected = True
elif width == 1200:
    x1200.selected = True
elif width == 1350:
    x1350.selected = True
elif width == 1620:
    x1620.selected = True
elif width == 2160:
    x2160.selected = True
def video_menu():
    status = True
    while status:
        global fps
        window.blit(background, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                status = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if previous.hover:
                        data['fps'] = fps
                        save()
                        status = False
                        options_menu()
                    elif fps60.hover:
                        fps = 60
                        fps60.selected = True
                        fps90.selected = False
                        fps120.selected = False
                        fps144.selected = False
                        fps240.selected = False
                        unlimited_fps.selected = False
                    elif fps90.hover:
                        fps = 90
                        fps60.selected = False
                        fps90.selected = True
                        fps120.selected = False
                        fps144.selected = False
                        fps240.selected = False
                        unlimited_fps.selected = False
                    elif fps120.hover:
                        fps = 120
                        fps60.selected = False
                        fps90.selected = False
                        fps120.selected = True
                        fps144.selected = False
                        fps240.selected = False
                        unlimited_fps.selected = False
                    elif fps144.hover:
                        fps = 144
                        fps60.selected = False
                        fps90.selected = False
                        fps120.selected = False
                        fps144.selected = True
                        fps240.selected = False
                        unlimited_fps.selected = False
                    elif fps240.hover:
                        fps = 240
                        fps60.selected = False
                        fps90.selected = False
                        fps120.selected = False
                        fps144.selected = False
                        fps240.selected = True
                        unlimited_fps.selected = False
                    elif unlimited_fps.hover:
                        fps = 999
                        fps60.selected = False
                        fps90.selected = False
                        fps120.selected = False
                        fps144.selected = False
                        fps240.selected = False
                        unlimited_fps.selected = True
                    elif x810.hover:
                        data['width'] = 810 #!! affecting data not actual game setting !!
                        x810.selected = True
                        x1080.selected = False
                        x1200.selected = False
                        x1350.selected = False
                        x1620.selected = False
                        x2160.selected = False
                    elif x1080.hover:
                        data['width'] = 1080
                        x810.selected = False
                        x1080.selected = True
                        x1200.selected = False
                        x1350.selected = False
                        x1620.selected = False
                        x2160.selected = False
                    elif x1200.hover:
                        data['width'] = 1200
                        x810.selected = False
                        x1080.selected = False
                        x1200.selected = True
                        x1350.selected = False
                        x1620.selected = False
                        x2160.selected = False
                    elif x1350.hover:
                        data['width'] = 1350
                        x810.selected = False
                        x1080.selected = False
                        x1200.selected = False
                        x1350.selected = True
                        x1620.selected = False
                        x2160.selected = False
                    elif x1620.hover:
                        data['width'] = 1620
                        x810.selected = False
                        x1080.selected = False
                        x1200.selected = False
                        x1350.selected = False
                        x1620.selected = True
                        x2160.selected = False
                    elif x2160.hover:
                        data['width'] = 2160
                        x810.selected = False
                        x1080.selected = False
                        x1200.selected = False
                        x1350.selected = False
                        x1620.selected = False
                        x2160.selected = True
                    elif fps_button.hover:
                        data['show_fps'] = not(data['show_fps'])
                        save()
                    elif cpu_usage_button.hover:
                        data['show_cpu_usage'] = not(data['show_cpu_usage'])
                        save()
        if data['show_cpu_usage']:
            cpu_usage_button.bg_color = green
        else:
            cpu_usage_button.bg_color = white
        if data['show_fps']:
            fps_button.bg_color = green
        else:
            fps_button.bg_color = white
        previous.display(window)
        title.display(window, 'video settings')
        frames.display(window, 'In-Game FPS')
        fps60.display(window, '60')
        fps90.display(window, '90')
        fps120.display(window, '120')
        fps144.display(window, '144')
        fps240.display(window, '240')
        unlimited_fps.display(window, 'UNLIM')
        resolutions.display(window, 'Screen Size')
        x810.display(window, '810p')
        x1080.display(window, '1080p')
        x1200.display(window, '1200p')
        x1350.display(window, '1350p')
        x1620.display(window, '1620p')
        x2160.display(window, '2160p')
        cpu_usage_button.display(window, 'Show CPU')
        fps_button.display(window, 'Show FPS')
        pygame.display.update()
        rate.tick(60) 

'''Verified'''
#font, x, y, width, height, bg_color, bg_hover_color, margin, padding, align
container_player1 = text(font, width*0.25, height*0.1, width*0.2 + width*0.033333*5/3, height*0.1, white, light_grey, 0, 'center', light_black)
container_player2 = text(font, width*0.5 + (width*0.0333/2), height*0.1, width*0.25 + width*0.0333/3, height*0.1, white, light_grey, 0, 'center', light_black)
skinp1_preview = image(resource(data['skinp1']), None, previous.x, height*0.425, height*0.15, height*0.15, 0.75, transparent_black, None)
skinp2_preview = image(resource(data['skinp2']), None, width*0.8, height*0.425, height*0.15, height*0.15, 0.75, transparent_black, None)
row1 = height*0.25
row2 = height*0.415
row3 = height*0.58
column1 = width*0.25
column2 = width*0.35 + width*0.0333
column3 = width*0.55 - width*0.0333
column4 = width*0.65
square_size = width*0.1
skin1 = image(resource('images/skins/skin1.png'), None, column1, row1, square_size, square_size, 0.75, transparent, transparent_black)
skin2 = image(resource('images/skins/skin2.png'), None, column2, row1, square_size, square_size, 0.75, transparent, transparent_black)
skin3 = image(resource('images/skins/skin3.png'), None, column3, row1, square_size, square_size, 0.75, transparent, transparent_black)
skin4 = image(resource('images/skins/skin4.png'), None, column4, row1, square_size, square_size, 0.75, transparent, transparent_black)
skin5 = image(resource('images/skins/skin5.png'), None, column1, row2, square_size, square_size, 0.75, transparent, transparent_black)
skin6 = image(resource('images/skins/skin6.png'), None, column2, row2, square_size, square_size, 0.75, transparent, transparent_black)
skin7 = image(resource('images/skins/skin7.png'), None, column3, row2, square_size, square_size, 0.75, transparent, transparent_black)
skin8 = image(resource('images/skins/skin8.png'), None, column4, row2, square_size, square_size, 0.75, transparent, transparent_black)
skin9 = image(resource('images/skins/skin9.png'), None, column1, row3, square_size, square_size, 0.75, transparent, transparent_black)
skin10 = image(resource('images/skins/skin10.png'), None, column2, row3, square_size, square_size, 0.75, transparent, transparent_black)
skin11 = image(resource('images/skins/skin11.png'), None, column3, row3, square_size, square_size, 0.75, transparent, transparent_black)
skin12 = image(resource('images/skins/skin12.png'), None, column4, row3, square_size, square_size, 0.75, transparent, transparent_black)
def pick_skin(self):
    global skinp1
    global skinp2
    global saved_skinp1
    global saved_skinp2
    if self.hover:
        self.selected = True
        self.bg_color_stored = transparent_green
    elif not(self.hover) and not(container_player1.hover or container_player2.hover or previous.hover):
        self.bg_color_stored = transparent
        self.selected = False
    if self.selected and container_player1.hover:
        data['skinp1'] = self.file
        skinp1_preview.image = pygame.transform.smoothscale(pygame.image.load(resource(data['skinp1'])).convert_alpha(), (int(skinp1_preview.image_width), int(skinp1_preview.image_height)))
        save()
    elif self.selected and container_player2.hover:
        data['skinp2'] = self.file 
        skinp2_preview.image = pygame.transform.smoothscale(pygame.image.load(resource(data['skinp2'])).convert_alpha(), (int(skinp2_preview.image_width), int(skinp2_preview.image_height)))
        save()

def skins_menu():
    status = True
    window.blit(background, (0, 0))
    while status:
        window.blit(background, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                status = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button:
                    if previous.hover:
                        status = False
                        mainmenu()
                    pick_skin(skin1)
                    pick_skin(skin2) 
                    pick_skin(skin3)
                    pick_skin(skin4)
                    pick_skin(skin5) 
                    pick_skin(skin6)
                    pick_skin(skin7)
                    pick_skin(skin8) 
                    pick_skin(skin9)
                    pick_skin(skin10)
                    pick_skin(skin11) 
                    pick_skin(skin12)
        previous.display(window)
        container_player1.display(window, 'player 1')
        container_player2.display(window, 'player 2')
        skinp1_preview.display(window)
        skinp2_preview.display(window)
        skin1.display(window)
        skin2.display(window)
        skin3.display(window)
        skin4.display(window)
        skin5.display(window)
        skin6.display(window)
        skin7.display(window)
        skin8.display(window)
        skin9.display(window)
        skin10.display(window)
        skin11.display(window)
        skin12.display(window)
        pygame.display.flip()
        rate.tick(60)


'''win card'''
card_width = width*0.5
card_height = height/3
card_surface = pygame.Rect(width*0.25, height/3, card_width, card_height)
card_bg = pygame.Rect(width*0.25 + card_width*0.025, height/3 + + card_width*0.025, card_width*0.95, card_height - card_width * 0.05)
unlock_message = text(poppins_small, width*0.25, height*0.016 + height/3, card_width, height*0.07, dark_red, None, 0, 'center', green)
congratulations = text(poppins, width*0.25, unlock_message.y + unlock_message.height, card_width, height*0.07, dark_red, None, 0, 'center', white)
see_level_stats = text(poppins_small, width*0.25, congratulations.y + congratulations.height, card_width, height*0.045, dark_red, light_red, 0, 'center', white)
buttons_bg = pygame.Rect(width*0.25, see_level_stats.y + see_level_stats.height, card_width, height*0.12)
level_menu_button = text(poppins_small, width*0.325, buttons_bg[1] - height*0.06 + card_width*3/20, card_width*3/10, height*0.045, red, light_red, 0, 'center', black)
play_next_button = text(poppins_small, width*0.525, buttons_bg[1] - height*0.06 + card_width*3/20, card_width*3/10, height*0.045, green, light_green, 0, 'center', white)
def display_wincard():
    pygame.draw.rect(window, green, card_surface)
    unlock_message.display(window, 'You can play Level {} ! >>> Space'.format(current_level+1))
    congratulations.display(window, 'Congratulations!!')
    see_level_stats.display(window, 'See Level Stats')
    pygame.draw.rect(window, dark_red, buttons_bg)
    play_next_button.display(window, 'Play Next')
    level_menu_button.display(window, 'Level Menu')
    
'''In-Game'''
#font, x, y, width, height, bg_color, bg_hover_color, margin, align
container_coin_collected = text(font, width*0.9, height*0.05, 0, 0, None, None, 0, 'right', white)
container_score = text(font, width*0.1, height*0.05, 0, 0, None, None, 0, 'left', white)
game_paused = text(font, 0, 0, width, height*2/3, transparent, None, 0, 'center', white)
reset_game = text(poppins, 0, 0, width, height*2/3, transparent, None, 0, 'center', red)
game_bar = bar(width, height*0.11, green, red)

def gameplay(game_map, game_level, game_chapter):
    """Optimised (CPU‑lighter) gameplay loop – same mechanics & constants.
    Only the body of this function changes; everything else in the code base
    remains untouched, satisfying the user’s constraints.
    """
    # ------------------------------------------------------------------
    #  ❱❱ Imports / Globals
    # ------------------------------------------------------------------
    global velocity, dt, current_level

    # Local shortcuts (avoid repeated global look‑ups in the hot loop)
    draw_rect     = pygame.draw.rect
    surf_blit     = window.blit
    get_events    = pygame.event.get
    key_pressed   = pygame.key.get_pressed
    cpu_percent   = psutil.cpu_percent
    clock_tick    = rate.tick
    showfps, showcpu = data['show_fps'], data['show_cpu_usage']

    # ------------------------------------------------------------------
    #  ❱❱ One‑shot initialisation (precompute & cache heavy stuff)
    # ------------------------------------------------------------------
    level_specs   = get_level_specs(game_chapter, game_level)
    map_height    = level_specs['map_height']
    block_size    = level_specs['block_size']
    view_field    = int(height / block_size) + 3
    map_lines     = len(game_map)                      # cache for bounds check

    # --- audio ---------------------------------------------------------
    pygame.mixer.music.load(resource(f'career/chapter{game_chapter+1}/level{game_level+1}.mp3'))
    pygame.mixer.music.set_volume(sound_value(music_volume))
    pygame.mixer.music.play(0)
    coin_sfx.set_volume(sound_value(sfx_volume))

    # --- players -------------------------------------------------------
    p1c = data['player1']['controls']
    p2c = data['player2']['controls']
    player1 = player(window, pygame.image.load(resource(data['skinp1'])).convert_alpha(),
                     width/2, height/1.2,
                     p1c['up'], p1c['ability'], p1c['left'], p1c['down'], p1c['right'])
    player2 = player(window, pygame.image.load(resource(data['skinp2'])).convert_alpha(),
                     width/2, height/1.2,
                     p2c['up'], p2c['ability'], p2c['left'], p2c['down'], p2c['right'])

    # --- game state ----------------------------------------------------
    velocity             = 0.0
    coins_collected      = 0
    coins_collected_p1   = data['player1']['coins']
    coins_collected_p2   = data['player2']['coins']

    last_p1_score        = data['player1']['score']
    last_p2_score        = data['player2']['score']
    cur_p1_score         = 0.0
    cur_p2_score         = 0.0

    win                  = False
    paused               = False

    # --- reusable objects ---------------------------------------------
    block_elem  = element(white, block_size, block_size)
    limit_elem  = element(red,   block_size, height * 0.005)

    coin_seq    = sequence('coin', 16, 'png', block_size / 4)
    coin_elem   = element(coin_seq[0], block_size/4, block_size/4)
    coin_delta  = (block_elem.width * 3/8, block_elem.height * 3/8)
    coin_anim_spd = len(coin_seq) * 2      # frames / second
    coin_frame    = 0.0

    # ------------------------------------------------------------------
    #  ❱❱ Runtime loop
    # ------------------------------------------------------------------
    now              = time.perf_counter()  # high‑res timer
    fps_counter_time = now                  # for throttling CPU/fps readouts
    fps_display_val  = 0
    cpu_display_val  = 0
    status           = True

    while status:
        # ---- time & physics ------------------------------------------
        new_now = time.perf_counter()
        dt      = new_now - now
        now     = new_now
        velocity += 2 * block_size * dt   # scrolling speed

        # ---- animate coin --------------------------------------------
        coin_frame = (coin_frame + coin_anim_spd * dt) % len(coin_seq)
        coin_elem.display = coin_seq[int(coin_frame)]

        # ---- event handling (very small)
        for ev in get_events():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # Pause toggle -------------------------------------------------
            if ev.type == pygame.KEYDOWN and key_pressed()[data['game_controls']['pause']]:
                pygame.mixer.music.pause(); paused = True
                snap = window.copy()
                while paused:
                    surf_blit(snap, (0, 0))
                    game_paused.display(layer2, 'Game Paused')
                    for pev in get_events():
                        if pev.type == pygame.KEYDOWN and key_pressed()[data['game_controls']['pause']]:
                            pygame.mixer.music.unpause(); paused = False
                    pygame.display.update(); clock_tick(60)

            # Win‑card mouse clicks ---------------------------------------
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and win:
                if level_menu_button.hover:
                    pygame.mixer.music.fadeout(500)
                    level_menu(); return
                if play_next_button.hover:
                    nxt_lvl = (game_level + 1) % 10
                    nxt_ch  = game_chapter + (1 if game_level == 9 else 0)
                    with open(resource(f'career/chapter{nxt_ch+1}/level{nxt_lvl+1}.txt'), 'r') as f:
                        gameplay(load_map(f), nxt_lvl, nxt_ch)
                    return
        # ---- render background ---------------------------------------
        window.fill(black)

        # ---- player movement -----------------------------------------
        player1.move(game_level, dt)
        data['player1']['distance_traveled'] += player1.distance_traveled
        cur_p1_score += player1.distance_traveled / 50

        if multiplayer:
            player2.move(game_level, dt)
            data['player2']['distance_traveled'] += player2.distance_traveled
            cur_p2_score += player2.distance_traveled / 50
        else:
            player2.container = pygame.Rect(0, 0, 0, 0)  # inert rect for intersects

        # ---- map rendering & collision -------------------------------
        crossed = int(velocity // block_size)
        y_start = velocity / block_size - crossed * block_size + height
        p1_rect, p2_rect = player1.container, player2.container

        for v in range(view_field):
            line_idx = crossed + v
            if line_idx >= map_lines:
                break
            row = game_map[line_idx]
            y   = y_start - v * block_size

            for col_idx, cell in enumerate(row):
                x = col_idx * block_size

                # These if branches are ordered by likelihood (hot first)
                if cell == '1':          # solid block
                    block_elem.define(window, x, y)
                    draw_rect(window, block_elem.display, block_elem.container)
                    if p1_rect.colliderect(block_elem.container): player1.death = True
                    if multiplayer and p2_rect.colliderect(block_elem.container): player2.death = True

                elif cell == '2':        # coin
                    cx, cy = x + coin_delta[0], y + coin_delta[1]
                    coin_elem.define(window, cx, cy)
                    surf_blit(coin_elem.display, coin_elem.container)

                    if p1_rect.colliderect(coin_elem.container):
                        coin_sfx.play(); row[col_idx] = ' '
                        coins_collected_p1 += 1; coins_collected += 1
                    elif multiplayer and p2_rect.colliderect(coin_elem.container):
                        coin_sfx.play(); row[col_idx] = ' '
                        coins_collected_p2 += 1; coins_collected += 1

                elif cell == '-':        # finish line
                    limit_elem.define(window, x, y)
                    draw_rect(window, limit_elem.display, limit_elem.container)
                    if p1_rect.colliderect(limit_elem.container) or p2_rect.colliderect(limit_elem.container):
                        win = True
                        # Update stats once; afterwards loop only displays card
                        data['player1']['coins'] = coins_collected_p1
                        data['player2']['coins'] = coins_collected_p2
                        data['player1']['score'] = cur_p1_score + last_p1_score + coins_collected_p1 * 16
                        data['player2']['score'] = cur_p2_score + last_p2_score + coins_collected_p2 * 16
                        ch_lvl = data['chapters'][game_chapter][game_level]
                        ch_lvl['percentage'] = 100
                        if ch_lvl['percentage'] == data['chapters'][current_chapter][current_level]['percentage']:
                            current_level += 1; refresh_career(current_chapter, current_level)
                        if ch_lvl['coins'] < coins_collected:
                            ch_lvl['coins'] = coins_collected
                        save()

        # ---- progress & death checks --------------------------------
        perc = round(max(
            velocity + height - player1.height - player1.y,
            velocity + height - player1.height - player2.y) / map_height * 100, 2)

        if not win:
            died = (not multiplayer and player1.death) or (multiplayer and player1.death and player2.death)
            if died:
                pygame.mixer.music.fadeout(500)
                ch_lvl = data['chapters'][game_chapter][game_level]
                if ch_lvl['percentage'] < perc:
                    ch_lvl['percentage'] = perc
                ch_lvl['attempts'] += 1 + multiplayer
                save(); mainmenu(); return

            game_bar.display(window, 0, 0, perc)
            container_coin_collected.display(window, str(coins_collected))
            container_score.display(window, str(int(max(cur_p1_score, cur_p2_score))))
        else:
            display_wincard()
            block_elem.display = green  # cosmetic change after win

        # ---- periodic perf overlay (0.33 s throttle) -----------------
        if showfps or showcpu:
            if new_now - fps_counter_time > 0.33:
                fps_counter_time = new_now
                fps_display_val  = int(rate.get_fps())
                cpu_display_val  = cpu_percent()
            if showfps:
                show_fps.display(window, f'FPS {fps_display_val}')
            if showcpu:
                show_cpu.display(window, f'CPU {cpu_display_val}')

        # ---- final blit / sync ---------------------------------------
        pygame.display.flip()
        clock_tick(fps)

def main():
    game_start_sound.set_volume(0.25)
    game_start_sound.play()
    mainmenu()

if __name__ == "__main__":
    main()