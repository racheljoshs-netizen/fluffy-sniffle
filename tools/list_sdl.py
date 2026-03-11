import pygame._sdl2.audio as sdl2_audio
from pygame import mixer

def list_sdl_devices():
    mixer.init()
    output_devices = sdl2_audio.get_audio_device_names(False)
    print("SDL Output Devices:")
    for i, name in enumerate(output_devices):
        print(f"  {i}: {name}")
    mixer.quit()

if __name__ == "__main__":
    list_sdl_devices()
