import sys
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame as pg
import pygame.midi

######## CONFIG, EDITABLE ########
KEY_COUNT = 88
KEY_WIDTH = 20 # pixels
KEY_HEIGHT = 180 # pixels

# RGB Colors
BACKGROUND_COLOR = (0, 0, 0)
BLACK_KEY_COLOR = (0, 0, 0)
WHITE_KEY_COLOR = (255, 255, 255)
POSSIBLE_PRESS_COLORS = ((128, 255, 255), (255, 128, 255), (255, 255, 128), (128, 128, 255), (255, 128, 128), (128, 255, 128))
CURRENT_PRESS_COLOR = 1 # index of above list

WINDOW_TITLE = "Madeline's MIDI Visualizer"
PANIC_KEY = pg.K_p # key used to reset all notes to not pressed
COLOR_KEY = pg.K_c # key used to cycle PRESS_COLOR through POSSIBLE_COLORS
RESET_KEY = pg.K_r
EXIT_KEY = pg.K_ESCAPE # closes the program

INPUT_DEVICE_ID = None # ID of input device, if none scans 0-9 and picks first one
######## END CONFIG ########

# Probably dont edit these
MIDI_NOTE_ID_OFFSET = -21 # added to midi event key IDs, makes A0 be key zero
MIDI_PRESS = 144
MIDI_RELEASE = 128
SCREENSIZE = (KEY_COUNT * KEY_WIDTH, KEY_HEIGHT)

pg.midi.init()

pg.display.set_caption(WINDOW_TITLE)
pg.display.set_icon(pg.Surface((0, 0)))

display = pg.display.set_mode(SCREENSIZE, pg.DOUBLEBUF|pg.HWACCEL|pg.HWSURFACE)

# Check midi input IDs 0 through 9 for a midi source
input_device = None

def try_connect_midi_device():
    global input_device

    if INPUT_DEVICE_ID is None:
        for i in range(10):
            try:
                input_device = pg.midi.Input(i)
            except:
                pass
    else:
        try:
            input_device = pg.midi.Input(INPUT_DEVICE_ID)
        except:
            pass

def midi_panic(piano_roll):
    for note in piano_roll:
        note.set(False)

try_connect_midi_device()

if not input_device: # Couldn't find one
    print("Could not find MIDI input device!")


class NoteObj():
    def __init__(self, number, screensize):
        self.is_white_note = False
        self.width = screensize[0]//88
        self.height = screensize[1]*(5/9)
        self.x = number * (screensize[0]//88)
        self.y = 0
        self.is_being_played = False

        if number % 12 == 1 or number % 12 == 4 or number % 12 == 6 or number % 12 == 9 or number % 12 == 11:
            self.width -= 2
            self.x += 1
            self.color = BLACK_KEY_COLOR
            self.height -= 2
        else:
            self.is_white_note = True
            self.color = WHITE_KEY_COLOR
            self.lower_width = self.width
            self.lower_x = number * self.width
            if number % 12 == 0 or number % 12 == 2 or number % 12 == 5 or number % 12 == 7 or number % 12 == 10:
                self.lower_x -= self.width / 2
                self.lower_width += self.width / 2
            if number % 12 == 0 or number % 12 == 3 or number % 12 == 5 or number % 12 == 8 or number % 12 == 10:
                self.lower_width += self.width / 2

            if number % 12 == 3 or number % 12 == 8:
                self.lower_width += self.width / 5
            elif number % 12 == 2 or number % 12 == 7:
                self.lower_x -= self.width / 5
                self.lower_width += self.width / 5
            if number % 12 == 5 or number % 12 == 10:
                self.lower_x += self.width / 5
                self.lower_width -= self.width / 5
            if number % 12 == 0 or number % 12 == 5:
                self.lower_width -= self.width / 5

    def set(self, on):
        self.is_being_played = on
        if self.is_being_played:
            self.color = POSSIBLE_PRESS_COLORS[CURRENT_PRESS_COLOR]
        elif self.is_white_note:
            self.color = WHITE_KEY_COLOR
        else:
            self.color = BLACK_KEY_COLOR

    def draw(self, window):
        pg.draw.rect(window, self.color, (self.x + 1, self.y, self.width - 2, self.height), 0)

        if self.is_white_note:
            pg.draw.rect(window, self.color, (self.lower_x + 1, self.y + self.height, self.lower_width - 2, self.height), 0)



piano_roll = [NoteObj(i, SCREENSIZE) for i in range(KEY_COUNT)]

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()
        
        if event.type == pg.KEYDOWN:
            if event.key == PANIC_KEY:
                midi_panic(piano_roll)
            
            elif event.key == COLOR_KEY:
                CURRENT_PRESS_COLOR = (CURRENT_PRESS_COLOR + 1) % len(POSSIBLE_PRESS_COLORS)
    
            elif event.key == RESET_KEY:
                pg.midi.quit()
                pg.midi.init()
                try_connect_midi_device()
                midi_panic(piano_roll)

            elif event.key == EXIT_KEY:
                sys.exit()

    if input_device and input_device.poll():
        events = input_device.read(1)

        for event in events:
            event_type = event[0][0]
            note = event[0][1] + MIDI_NOTE_ID_OFFSET

            if 0 <= note <= (KEY_COUNT - 1):
                if event_type == MIDI_PRESS:
                    piano_roll[note].set(True)
                
                elif event_type == MIDI_RELEASE:
                    piano_roll[note].set(False)

    display.fill(BACKGROUND_COLOR)

    for note in piano_roll:
        note.draw(display)

    pg.display.flip()
