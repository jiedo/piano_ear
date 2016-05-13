#!/usr/bin/env python
#encoding:utf-8
"""extremely simple demonstration playing a soundfile
and waiting for it to finish. you'll need the pygame.mixer
module for this to work. Note how in this simple example we
don't even bother loading all of the pygame package. Just
pick the mixer for sound and time for the delay function.

Optional command line argument:
  the name of an audio file.


"""
__create_time__ = "Feb 26 2012"

import threading
import time as jiedotime
import os
import os.path, sys, random
import pygame.mixer, pygame.time
import parsemidi
from pygame.locals import *
import piano
mixer = pygame.mixer
time = pygame.time

g_done = False

def get_volecity(v):
    return 127
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


class playtrack(threading.Thread):
    def __init__(self, screen, whitekeys, blackkeys):
        threading.Thread.__init__(self)
        self.screen = screen
        self.whitekeys = whitekeys
        self.blackkeys = blackkeys

    def run(self):
        pipe_name = '/tmp/pipe_show_midi'
        if not os.path.exists(pipe_name):
            os.mkfifo(pipe_name)

        pipein = open(pipe_name, 'r')
        print "read opend"

        notes_rec = []
        timestamp = jiedotime.time()
        time_pitchs = []

        global g_done
        while not g_done:
            line = pipein.readline()[:-1]
            if g_done: break
            n = len(line)
            if n < 1:
                print "reopen..."
                pipein.close()
                pipein = open(pipe_name, 'r')

            a = line.split()
            if len(a) > 2:
                cmd, pitch, volecity, pitch_timestamp = a[:4]
            else:
                continue
            pitch = int(pitch)
            volecity = int(volecity)
            pitch_timestamp = int(pitch_timestamp)
            pitch_side_blackkeys_rec = []
            if pitch in self.whitekeys.keys():
                pitch_key_rec = [self.whitekeys[pitch]]
                key_color = piano.white
                if pitch + 1 in self.blackkeys.keys():
                    pitch_side_blackkeys_rec += [self.blackkeys[pitch+1]]
                if pitch - 1 in self.blackkeys.keys():
                    pitch_side_blackkeys_rec += [self.blackkeys[pitch-1]]

            elif pitch in self.blackkeys.keys():
                pitch_key_rec = [self.blackkeys[pitch]]
                key_color = piano.black

            key_color_down = piano.color_key_down
            if key_color != piano.black:
                key_color_down = piano.color_key_down

            #print '\r',' ' * 108,'\r',
            if pitch > 20 and pitch < 109:
                if cmd == 'NOTE_ON':

                    if pitch_timestamp != timestamp:
                        timestamp = pitch_timestamp
                        time_pitchs = []
                        piano.draw_keys(self.screen, notes_rec, piano.backgroud_color)
                        new_notes_rec = []
                        for rec in notes_rec:
                            rec = rec.move(0, - rec.height - 1)
                            if rec.top > 0:
                                new_notes_rec += [rec]
                        notes_rec = new_notes_rec

                        print   # 确定字符输出的一个和弦

                        piano.draw_lines(self.screen,
                                         piano.WINSIZE[1]-piano.piano_white_key_height)
                        piano.draw_keys(self.screen, notes_rec) #
                        #h=1, n=7,top=0,left=10):

                    if pitch not in time_pitchs:
                        time_pitchs += [pitch]

                        height = piano.piano_white_key_height / 10
                        rec = pitch_key_rec[0].copy().move(0,-height)
                        rec.height = height
                        notes_rec += [rec]
                        piano.draw_keys(self.screen, [rec]) #

                    # if 21 not in time_pitchs:
                    #     time_pitchs += [21]
                    # if 60 not in time_pitchs:
                    #     time_pitchs += [60]
                    # if 108 not in time_pitchs:
                    #     time_pitchs += [108]

                    time_pitchs.sort()
                    key2color = [(1, 'C'),
                                 (1, 'C'),
                                 (2, 'D'),
                                 (2, 'D'),
                                 (3, 'E'),
                                 (4, 'F'),
                                 (4, 'F'),
                                 (5, 'G'),
                                 (5, 'G'),
                                 (6, 'A'),
                                 (6, 'A'),
                                 (7, 'B')]
                    blackkeys_index = [1,3,6,8,10]
                    last = 0
                    sys.stdout.write('\r')
                    for i in time_pitchs:
                        between = '-'
                        if last == 0: between = ' '
                        isBlack = '07'
                        if (i % 12) in blackkeys_index:
                            isBlack = '03'
                        color, note = key2color[i % 12]
                        sys.stdout.write('%s%s' % (between * (i - last -1),
                                                   '\033[%s;3%d;40m%s\033[0m' % (isBlack,
                                                                                 color,
                                                                                 note)
                                        ))
                        last = i

                    sys.stdout.write(' ' * (120 - last -1))
                    sys.stdout.flush()

                    volecity = get_volecity(volecity)

                    piano.draw_keys(self.screen, pitch_key_rec, key_color_down)
                    piano.draw_keys(self.screen, pitch_side_blackkeys_rec, piano.black)


                elif cmd == 'NOTE_OFF':
                    #v = 127
                    #for v in volecity_list:
                    #channel = sounds[(pitch, v)].fadeout(500)
                    piano.draw_keys(self.screen, pitch_key_rec, key_color)
                    piano.draw_keys(self.screen, pitch_side_blackkeys_rec, piano.black)

def main():
    """Play an audio file as a buffered sound sample
    Option argument:
        the name of an audio file (default data/secosmic_low.wav
    """
    whitekeys = {}
    blackkeys = {}
    screen = piano.draw_piano(whitekeys, blackkeys, piano.WINSIZE[1]-piano.piano_white_key_height)
    thread_track = playtrack(screen, whitekeys, blackkeys)
    thread_track.start()

    clock = pygame.time.Clock()
    global g_done
    while not g_done:
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
                g_done = True
                break
            elif e.type == MOUSEBUTTONDOWN and e.button == 1:
                #
                pass
        clock.tick(100)
    g_done = True
    sys.exit(0)

if __name__ == '__main__':
    main()
