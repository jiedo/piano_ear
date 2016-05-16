#!/usr/bin/env python
#encoding: utf8

""" piano play center
"""


from piano import Piano
from pygame.locals import *

import os
import os.path, sys, random
import parse_midi
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
    p_all_midi_lines, p_notes_in_all_staff = parse_midi.load_midi("data.midi")

    p_staff_offset_x = 0

    time_pitchs = []
    last_timestamp = -1
    old_time = 0
    last_cmd = ""

    last_mouse_pos = None

    is_pause = False
    is_clear = True
    while not p_done:
        # events
        for e in pygame.event.get():
            if e.type == QUIT:
                p_done = True
                break

            if e.type == MOUSEMOTION:
                if last_mouse_pos is not None:
                    p_staff_offset_x = last_mouse_pos - e.pos[0]

            if e.type == MOUSEBUTTONUP:
                last_mouse_pos = None

            if e.type == MOUSEBUTTONDOWN:
                last_mouse_pos = p_staff_offset_x + e.pos[0]

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
                        p_all_midi_lines, p_notes_in_all_staff = parse_midi.load_midi("data.midi")
                        p_midi_cmd_idx = 0
                        is_pause = False
                        is_clear = False

            elif e.type == MOUSEBUTTONDOWN and e.button == 1:
                pass

        # get cmd
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
            print "error:", e
            pygame.display.update()
            clock.tick(2)
            continue

        # show keys
        piano.show_keys_press(cmd, pitch)
        piano.show_notes_staff(p_notes_in_all_staff, pitch_timestamp, WINSIZE[1] * 0.382, p_staff_offset_x)

        # a chord
        if pitch_timestamp != last_timestamp:
            print "bps:", utils.g_bps.get_bps_count()

            utils.show_chord_keys_by_ascii(time_pitchs)
            utils.sync_play_time(pitch_timestamp, last_timestamp, old_time)
            old_time = time.time()
            last_timestamp = pitch_timestamp
            time_pitchs = []


        # playtrack
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

        #clock.tick(10)


if __name__ == '__main__':
    main()
