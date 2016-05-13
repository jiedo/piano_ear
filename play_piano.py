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


if _platform == "darwin":
    # OS X
    import AppKit


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

        global g_done, g_key_press

        #print sounds_keys
        piano_label_font = pygame.font.Font(pygame.font.match_font('Bravura Text'), 144)
        time_pitchs = []
        timestamp = 0
        while not g_done:
            try:
                midi_line = play_midi.g_queue.get(True, 1)
                print midi_line
                cmd, pitch, volecity_data, pitch_timestamp = midi_line.split()[:4]
                volecity = get_volecity(int(volecity_data))
                pitch = int(pitch)
                pitch_timestamp = int(pitch_timestamp)
            except Exception, e:
                print "no data: ", e
                continue

            if pitch not in grand_pitch_range:
                continue

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
                if pitch_timestamp != timestamp:
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

                    timestamp = pitch_timestamp
                    time_pitchs = []

                if pitch not in time_pitchs:
                    time_pitchs += [pitch]

                note_rec, note_pos = self.piano.draw_note(pitch)
                self.piano.draw_lines(WINSIZE[1]- self.piano.piano_white_key_height)
                # self.piano.screen.blit(ren, (note_pos, 100))
                self.piano.draw_keys(pitch_key_rec, key_color_down)
                self.piano.draw_keys(pitch_side_blackkeys_rec, self.piano.black)

                if _platform == "darwin":
                    _sound = sounds[(pitch, volecity)]
                    _sound.setVolume_(0.4)
                    _sound.play()

            elif cmd == "NOTE_OFF":

                if _platform == "darwin":
                    _sound.setVolume_(0.0)
                    time.sleep(0.03)
                    _sound.stop()

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
                        play_midi.load_midi("data.midi")
                        is_clear = False

            elif e.type == MOUSEBUTTONDOWN and e.button == 1:
                pass
        clock.tick(10)
    g_done = True


if __name__ == '__main__':
    main()
