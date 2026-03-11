import pygame
import time
import os

DEVICE_NAME = "Headphones (2- VIPEX VX-SK001)"
LOG = "E:/0x/mixer_diag.log"

def diag():
    with open(LOG, "w") as f:
        f.write(f"Starting Mixer Diag with {DEVICE_NAME}\n")
        try:
            pygame.mixer.init(devicename=DEVICE_NAME)
            f.write("Mixer init OK\n")
            
            # Create a silent wave if no file
            if not os.path.exists("E:/0x/test_edge.mp3"):
                f.write("test_edge.mp3 missing, skipping play test\n")
                return
                
            pygame.mixer.music.load("E:/0x/test_edge.mp3")
            f.write("Music load OK\n")
            pygame.mixer.music.play()
            f.write("Music play OK\n")
            
            start = time.time()
            while time.time() - start < 5:
                if pygame.mixer.music.get_busy():
                    f.write("Music is BUSY (playing)\n")
                    break
                time.sleep(0.5)
            else:
                f.write("Music never became busy\n")
                
        except Exception as e:
            f.write(f"ERROR: {e}\n")

if __name__ == "__main__":
    diag()
