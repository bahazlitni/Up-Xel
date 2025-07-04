import pygame
import Screen

REGULAR_SIZE = 0.0333
MEDIUM_SIZE = 0.025
SMALL_SIZE = 0.015

def Ka1(small=False):
    SIZE = MEDIUM_SIZE if small else REGULAR_SIZE
    return pygame.font.Font(".\\fonts\\ka1.ttf", SIZE*Screen.WIDTH)

def Poppins(small=False):
    SIZE = SMALL_SIZE if small else REGULAR_SIZE
    return pygame.font.Font(".\\fonts\\poppins-bold.ttf", SIZE*Screen.WIDTH)