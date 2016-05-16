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

import os
import os.path, sys, random
import play_midi
import pygame.time
import threading
import time
import player
import utils


def main():
    """Play a midi file with sound samples
    """

    pygame.init()
    WINSIZE = [1248, 740]
    screen = pygame.display.set_mode(WINSIZE)
    pygame.display.set_caption('Piano Center')

    piano = Piano(screen, WINSIZE)
    piano.draw_piano()
    piano.draw_lines(WINSIZE[1] * 0.618)

    # import os
    # os.system("convert -density 100 -depth 24 -quality 99 data.pdf data.png")
    # staff_img_png = pygame.image.load("data.png").convert_alpha()
    # staff_img = staff_img_png
    # staff_img_rect = staff_img.get_rect()
    # print staff_img_rect
    # piano.screen.blit(staff_img, staff_img_rect, (0, 0, WINSIZE[0], WINSIZE[1] * 0.618))

    clock = pygame.time.Clock()

    p_done = False
    p_key_press = None

    devices = player.init()
    sounds_keys, sounds = player.load_sounds()
    # print sounds_keys
    # player.test_sounds(sounds_keys, sounds)

    p_midi_cmd_idx = 0
    p_all_midi_lines = play_midi.load_midi("data.midi")

    time_pitchs = []
    last_timestamp = -1
    old_time = 0
    last_cmd = ""

    is_pause = False
    is_clear = True
    while not p_done:
        for e in pygame.event.get():
            if e.type == QUIT:
                p_done = True
                break
            elif e.type == KEYUP:
                if e.key == K_ESCAPE:
                    p_done = True
                    break
                elif e.key in [K_a, K_b, K_c, K_d, K_e, K_f, K_g, ]:
                    p_key_press = e.key

                elif e.key in [K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9]:
                    print "Progress:", e.key - 48
                    piano.draw_piano()
                    p_midi_cmd_idx = len(p_all_midi_lines) * (e.key - 48) / 10
                    last_timestamp = -1

                elif e.key == K_RETURN:
                    is_clear = True
                    is_pause = not is_pause

                elif e.key == K_SPACE:
                    if is_clear:
                        piano.draw_piano()
                        p_all_midi_lines = play_midi.load_midi("data.midi")
                        p_midi_cmd_idx = 0
                        is_pause = False
                        is_clear = False

            elif e.type == MOUSEBUTTONDOWN and e.button == 1:
                pass


        # playtrack
        try:
            if is_pause or p_midi_cmd_idx >= len(p_all_midi_lines):
                raise Exception("paused")
            midi_line = p_all_midi_lines[p_midi_cmd_idx]
            p_midi_cmd_idx += 1
            # print midi_line

            cmd, pitch, volecity_data, pitch_timestamp = midi_line.split()[:4]
            volecity = player.get_volecity(int(volecity_data))
            pitch = int(pitch)
            if pitch not in player.g_grand_pitch_range:
                raise Exception("pitch not in range")

            pitch_timestamp = int(pitch_timestamp)
            if last_timestamp == -1:
                # init last timestamp
                last_timestamp = pitch_timestamp - 1
        except Exception, e:
            pygame.display.update()
            clock.tick(10)
            continue

        # a chord
        if pitch_timestamp != last_timestamp:
            print "bps:", utils.g_bps.get_bps_count()

            utils.show_chord_keys_by_ascii(time_pitchs)
            utils.sync_play_time(pitch_timestamp, last_timestamp, old_time)
            old_time = time.time()
            last_timestamp = pitch_timestamp
            time_pitchs = []

        if cmd == "NOTE_ON":
            # sleep after pitch off
            if last_cmd == "NOTE_OFF":
                last_cmd = "NOTE_ON"
                time.sleep(0.02)
            player.play(devices, pitch, volecity, sounds)

            # build chord
            if pitch not in time_pitchs:
                time_pitchs += [pitch]

        elif cmd == "NOTE_OFF":
            last_cmd = "NOTE_OFF"
            player.stop(devices, pitch, volecity, sounds)

        player.show_keys_press(piano, cmd, pitch)

        #clock.tick(10)

    p_done = True


if __name__ == '__main__':
    main()
