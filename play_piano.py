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


from piano import Piano
from pygame.locals import *
from sys import platform as _platform
import os
import os.path, sys, random
import play_midi
import pygame.time
import threading
import time

_platform = "disable"

if _platform == "darwin":
    # OS X
    import AppKit

g_all_midi_lines = []
g_midi_cmd_idx = 0
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
        #volecity_list = [100]
        grand_pitch_range  = range(21,109)
        sounds_keys = []
        sounds = {}
        for g in grand_pitch_range:
            for v in volecity_list:
                sound_file = '/Users/jie/astudy/jiedo/Piano_Sounds/Grand-%03d-%03d.wav' % (g,v)
                if _platform == "darwin":
                    sounds[(g,v)] = AppKit.NSSound.alloc().initWithContentsOfFile_byReference_(sound_file, False)
                sounds_keys += [(g,v)]

        global g_done, g_key_press, g_midi_cmd_idx, g_all_midi_lines

        #print sounds_keys
        time_pitchs = []
        last_timestamp = 0
        timestamp = 0
        while not g_done:
            try:
                if g_midi_cmd_idx >= len(g_all_midi_lines):
                    time.sleep(1)
                    continue

                midi_line = g_all_midi_lines[g_midi_cmd_idx]
                g_midi_cmd_idx += 1
                # print midi_line
                cmd, pitch, volecity_data, pitch_timestamp = midi_line.split()[:4]
                volecity = get_volecity(int(volecity_data))
                pitch = int(pitch)
                pitch_timestamp = int(pitch_timestamp)
            except Exception, e:
                time.sleep(1)
                print "no data: ", e
                continue

            if pitch not in grand_pitch_range:
                continue

            if pitch not in time_pitchs:
                time_pitchs += [pitch]

            if pitch_timestamp != last_timestamp:
                key2color = [(1, 'C'), (1, 'C'), (3, 'D'), (3, 'D'), (8, 'E'),
                             (2, 'F'), (2, 'F'), (6, 'G'), (6, 'G'), (4, 'A'), (4, 'A'), (5, 'B')]
                blackkeys_index = [1, 3, 6, 8, 10]
                last = 0
                for i in time_pitchs:
                    between = '-'
                    if last == 0: between = ' '
                    isBlack = '07'
                    if (i % 12) in blackkeys_index:
                        isBlack = '03'
                    color, note = key2color[i % 12]
                    print ('%s%s' % (between * (i - last -1),
                                     '\033[%s;3%d;40m%s\033[0m' % (isBlack, color, note))),
                    last = i

                print

                # sleep
                deta_timestamp = pitch_timestamp - last_timestamp
                pygame.time.wait(int(deta_timestamp * play_midi.g_interval / play_midi.g_tpq ))

                last_timestamp = pitch_timestamp
                time_pitchs = []



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

            if cmd == "NOTE_ON":
                note_rec, note_pos = self.piano.draw_note(pitch, top=WINSIZE[1] * 0.7)
                self.piano.draw_lines(WINSIZE[1] * 0.618)
                # self.piano.screen.blit(ren, (note_pos, 100))
                self.piano.draw_keys(pitch_key_rec, key_color_down)
                self.piano.draw_keys(pitch_side_blackkeys_rec, self.piano.black)

                if _platform == "darwin":
                    _sound = sounds[(pitch, volecity)]
                    _sound.setVolume_(0.7)
                    _sound.play()

            elif cmd == "NOTE_OFF":

                if _platform == "darwin":
                    _sound.setVolume_(0.1)
                    time.sleep(0.03)
                    _sound.stop()

                pygame.draw.rect(self.piano.screen, self.piano.backgroud_color, note_rec, False)

                self.piano.draw_lines(WINSIZE[1] * 0.618)
                self.piano.draw_keys(pitch_key_rec, key_color)
                self.piano.draw_keys(pitch_side_blackkeys_rec, self.piano.black)


def main():
    """Play an audio file as a buffered sound sample
    """

    pygame.init()
    screen = pygame.display.set_mode(WINSIZE)
    pygame.display.set_caption('Piano Keyboard')

    piano = Piano(screen, WINSIZE)

    piano.draw_piano()
    piano.draw_lines(WINSIZE[1] * 0.618)
    thread_track = Playtrack(piano)
    thread_track.start()

    # import os
    # os.system("convert -density 100 -depth 24 -quality 99 data.pdf data.png")

    staff_img_png = pygame.image.load("data.png").convert_alpha()
    staff_img = staff_img_png
    staff_img_rect = staff_img.get_rect()
    print staff_img_rect

    piano.screen.blit(staff_img, staff_img_rect, (0, 0, WINSIZE[0], WINSIZE[1] * 0.618))

    clock = pygame.time.Clock()
    global g_done, g_key_press, g_all_midi_lines, g_midi_cmd_idx

    g_all_midi_lines = play_midi.load_midi("data.midi")
    g_midi_cmd_idx = 0

    is_clear = True
    while not g_done:
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == QUIT:
                g_done = True
                break
            elif e.type == KEYUP:
                if e.key == K_ESCAPE:
                    g_done = True
                    break
                elif e.key in [K_a, K_b, K_c, K_d, K_e, K_f, K_g, ]:
                    g_key_press = e.key

                elif e.key == K_RETURN:
                    is_clear = True

                elif e.key == K_SPACE:
                    if is_clear:
                        g_all_midi_lines = play_midi.load_midi("data.midi")
                        g_midi_cmd_idx = 0
                        is_clear = False

            elif e.type == MOUSEBUTTONDOWN and e.button == 1:
                pass
        clock.tick(10)
    g_done = True


if __name__ == '__main__':
    main()
