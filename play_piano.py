#!/usr/bin/env python
#encoding: utf8

"""extremely simple demonstration playing a soundfile
and waiting for it to finish. you'll need the pygame.mixer
module for this to work. Note how in this simple example we
don't even bother loading all of the pygame package. Just
pick the mixer for sound and time for the delay function.

Optional command line argument:
  the name of an audio file.


"""

import os
import os.path, sys, random

import pygame.time
import threading
import AppKit

from pygame.locals import *
from piano import Piano
import time

g_done = False
g_key_press = None
WINSIZE = [1280, 750]

def get_volecity(v):
    volecity = [48, 60, 71, 82, 91, 100, 115, 127]
    selectv = 48
    absdit = abs(selectv - v)
    for vo in volecity:
        if abs(vo - v) <= absdit:
            absdit = abs(vo - v)
            selectv = vo
        else:
            return selectv
    return 127


class Playtrack(threading.Thread):
    def __init__(self, piano):
        threading.Thread.__init__(self)
        self.piano = piano

    def run(self):
        volecity_list = [48, 60, 71, 82, 91, 100, 115, 127]
        volecity_list = [100]
        grand  = range(21,109)
        sounds_keys = []
        sounds = {}
        for g in grand:
            for v in volecity_list:
                sound_file = '/Users/jie/astudy/jiedo/Piano_Sounds/Grand-%03d-%03d.wav' % (g,v)
                sounds[(g,v)] = AppKit.NSSound.alloc().initWithContentsOfFile_byReference_(sound_file, False)
                sounds_keys += [(g,v)]

        global g_done, g_key_press
        #piano_label_font = pygame.font.SysFont("Bravura Text Regular", 46)
        piano_label_font = pygame.font.Font(pygame.font.match_font('Bravura Text'), 144)
        last_pitch_idx = 43
        last_force_idx = 5

        while not g_done:
            pitch_deta = random.randint(-12, 12)
            last_pitch_idx += pitch_deta
            if last_pitch_idx < 0:
                last_pitch_idx = 0
            if last_pitch_idx > 87:
                last_pitch_idx = 87

            # force_deta = random.randint(-2, 2)
            # last_force_idx += force_deta
            # if last_force_idx < 0:
            #     last_force_idx = 0
            # if last_force_idx > 7:
            #     last_force_idx = 7
            # pitch, volecity = sounds_keys[last_pitch_idx * 8 + last_force_idx]

            pitch, volecity = sounds_keys[last_pitch_idx]
            time_pitchs = [pitch]

            pitch_side_blackkeys_rec = []
            if pitch in self.piano.whitekeys.keys():
                pitch_key_rec = [self.piano.whitekeys[pitch]]
                key_color = self.piano.white
                if pitch + 1 in self.piano.blackkeys.keys():
                    pitch_side_blackkeys_rec += [self.piano.blackkeys[pitch+1]]
                if pitch - 1 in self.piano.blackkeys.keys():
                    pitch_side_blackkeys_rec += [self.piano.blackkeys[pitch-1]]

            elif pitch in self.piano.blackkeys.keys():
                pitch_key_rec = [self.piano.blackkeys[pitch]]
                key_color = self.piano.black

            key_color_down = self.piano.color_key_down
            if key_color != self.piano.black:
                key_color_down = self.piano.color_key_down

            key2color = [(1, 'C'), (1, 'C'), (2, 'D'), (2, 'D'), (3, 'E'), (4, 'F'), (4, 'F'), (5, 'G'), (5, 'G'), (6, 'A'), (6, 'A'), (7, 'B')]
            blackkeys_index = [1, 3, 6, 8, 10]
            last = 0
            for i in time_pitchs:
                between = '-'
                if last == 0: between = ' '
                isBlack = '07'
                if (i % 12) in blackkeys_index:
                    isBlack = '03'
                color, note = key2color[i % 12]
                print('%s%s' % (between * (i - last -1),
                                '\033[%s;3%d;40m%s\033[0m' % (isBlack, color, note)))
                last = i

            note_rec, note_pos = self.piano.draw_note(pitch)
            self.piano.draw_lines(WINSIZE[1]- self.piano.piano_white_key_height)
            # self.piano.screen.blit(ren, (note_pos, 100))
            self.piano.draw_keys(pitch_key_rec, key_color_down)
            self.piano.draw_keys(pitch_side_blackkeys_rec, self.piano.black)

            _sound = sounds[(pitch, volecity)]
            _sound.setVolume_(0.4)
            _sound.play()

            time.sleep(0.4)

            _sound.setVolume_(0.0)
            time.sleep(0.03)
            _sound.stop()

            # off
            pygame.draw.rect(self.piano.screen, self.piano.backgroud_color, note_rec, False)
            self.piano.draw_lines(WINSIZE[1] - self.piano.piano_white_key_height)
            self.piano.draw_keys(pitch_key_rec, key_color)
            self.piano.draw_keys(pitch_side_blackkeys_rec, self.piano.black)


def main():
    """Play an audio file as a buffered sound sample
    """

    pygame.init()
    screen = pygame.display.set_mode(WINSIZE)
    pygame.display.set_caption('Piano Keyboard')

    piano = Piano(screen)
    piano.draw_piano()

    screen = piano.draw_piano(WINSIZE[1]-piano.piano_white_key_height)
    piano.draw_lines(WINSIZE[1]-piano.piano_white_key_height)
    thread_track = Playtrack(piano)
    thread_track.start()

    clock = pygame.time.Clock()
    global g_done, g_key_press
    while not g_done:
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
                g_done = True
                break
            elif e.type == KEYUP:
                if e.key in [K_A, K_B, K_C, K_D, K_E, K_F, K_G, ]:
                    g_key_press = e.key

            elif e.type == MOUSEBUTTONDOWN and e.button == 1:
                #
                pass
        clock.tick(5)
    g_done = True


    # while True:
    # sounds[(pitch, v)].set_volume(.05)
    # channel = sounds[(pitch, v)].fadeout(10)


if __name__ == '__main__':
    main()
