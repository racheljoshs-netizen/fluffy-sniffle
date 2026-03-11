import pygame
import time
import os

DEVICE_NAME = "Headphones (2- VIPEX VX-SK001)"
FILE = "E:/0x/test_edge.mp3"

def play_test():
    print(f"Playing {FILE} to {DEVICE_NAME}")
    pygame.mixer.init(devicename=DEVICE_NAME)
    pygame.mixer.music.load(FILE)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    print("Done.")

if __name__ == "__main__":
    play_test()
