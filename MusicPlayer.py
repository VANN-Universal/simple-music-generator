import pygame

freq = 44100
bitsize = -16
channels = 2
buffer = 1024
pygame.mixer.init(freq, bitsize, channels, buffer)


def play_music(music_file):
    clock = pygame.time.Clock()
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        clock.tick(30)
        # print(pygame.mixer.music.get_pos())
