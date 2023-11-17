#!/usr/bin/env python3

import pygame
import time
import os
import alsaaudio
import contextlib
from screeninfo import get_monitors
from Xlib.display import Display
from Xlib import X
import datetime
import subprocess

os.environ['XDG_RUNTIME_DIR'] = '/run/user/{}'.format(os.getuid())

def get_master_volume():
    mixer = alsaaudio.Mixer()
    return mixer.getvolume()[0]

def set_master_volume(volume):
    mixer = alsaaudio.Mixer()
    mixer.setvolume(volume)

@contextlib.contextmanager
def grab():
    disp = Display()
    root = disp.screen().root
    root.grab_pointer(True, 0, X.GrabModeAsync, X.GrabModeAsync, 0, 0, X.CurrentTime)
    root.grab_keyboard(True, X.GrabModeAsync, X.GrabModeAsync, X.CurrentTime)
    try:
        yield
    finally:
        disp.ungrab_pointer(X.CurrentTime)
        disp.ungrab_keyboard(X.CurrentTime)

def main():
    # Set the window position
    os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'

    pygame.init()

    initial_volume = get_master_volume()  # Store initial volume
    set_master_volume(0)  # Mute the sound

    monitors = get_monitors()
    if not monitors:
        raise Exception("No monitors found")

    primary_monitor = monitors[0]
    SCREEN_WIDTH, SCREEN_HEIGHT = primary_monitor.width, primary_monitor.height

    screen = pygame.display.set_mode((SCREEN_WIDTH+10000, SCREEN_HEIGHT+9000), pygame.NOFRAME)
    pygame.display.set_caption('Shutdown Countdown')

    BLACK = (48, 69, 36)
    RED = (255, 0, 0)

    initial_font_size = int(SCREEN_WIDTH * 0.1)
    font = pygame.font.SysFont(None, initial_font_size)

    def display_countdown(time_left):
        screen.fill(BLACK)
        mins, secs = divmod(time_left, 60)
        time_format = '{:02d}:{:02d}'.format(mins, secs)
        text = font.render(time_format, True, RED)
        text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        screen.blit(text, text_rect)
        pygame.display.flip()

    countdown_seconds = 10 * 1

    with grab():
        running = True
        while running and countdown_seconds >= 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False

            display_countdown(countdown_seconds)
            time.sleep(1)
            countdown_seconds -= 1

    set_master_volume(initial_volume)  # Restore the initial volume

    # Check if current time is between midnight and 6 AM
    current_time = datetime.datetime.now()
    if 1 <= current_time.hour < 6:
        subprocess.call(["sudo", "/usr/bin/systemctl", "suspend"])

    pygame.quit()

if __name__ == "__main__":
    main()
