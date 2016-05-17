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

import MenuSystem


def get_menu_data():
    menu_data_dict = {}
    for (dir_full_path, dirnames, filenames) in os.walk("data"):
        dir_full_path = dir_full_path.decode("utf8")

        dirpath = dir_full_path.split(u"/")[-1]
        if dirpath not in menu_data_dict:
            menu_data_dict[dirpath] = []

        menu_data = menu_data_dict[dirpath]
        menu_data += [dirpath]

        for dirname in dirnames:
            dirname = dirname.decode("utf8")
            if dirname not in menu_data_dict:
                menu_data_dict[dirname] = []
            menu_data += [menu_data_dict[dirname]]

        midi_filenames = [dir_full_path + u"/" + filename.decode("utf8") for filename in filenames
                          if (filename.endswith(".mid") or filename.endswith(".midi"))]
        if midi_filenames:
            menu_data += midi_filenames
        elif not dirnames:
            menu_data += [u"."]

    menu_data = []
    for data in menu_data_dict["data"]:
        if not isinstance(data, list):
            continue

        sub_menu_data = []
        for data_inner in data[1:]:
            if not isinstance(data_inner, list):
                sub_menu_data += [data_inner]
                continue

            subsub_menu_data = []
            for data_inner_inner in data_inner[1:]:
                if not isinstance(data_inner_inner, list):
                    subsub_menu_data += [data_inner_inner]

            sub_menu_data += [MenuSystem.Menu(data_inner[0], subsub_menu_data)]

        menu_data += [MenuSystem.Menu(data[0], sub_menu_data)]

    return menu_data


def main():
    """Play a midi file with sound samples
    """

    pygame.init()
    WINSIZE = [1248, 740]
    screen = pygame.display.set_mode(WINSIZE)
    pygame.display.set_caption('Piano Center')

    # menu
    MenuSystem.init()
    MenuSystem.BGCOLOR = Color(200,200,200, 255)
    MenuSystem.FGCOLOR = Color(0, 0, 0, 0)
    MenuSystem.BGHIGHTLIGHT = Color(40,40,40,40)
    MenuSystem.BORDER_HL = Color(200,200,200,200)

    menu_bar = MenuSystem.MenuBar(top=10)
    menus_in_bar = get_menu_data()
    menu_bar.set(menus_in_bar)

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

    p_is_metro_on = False

    p_midi_cmd_idx = 0
    p_all_midi_lines, p_notes_in_all_staff = parse_midi.load_midi("data.midi")

    p_staff_offset_x = 0

    time_pitchs = []
    last_timestamp = -1
    old_time = 0
    last_cmd = ""

    last_mouse_pos = None
    is_pause = False
    while not p_done:
        # events
        for ev in pygame.event.get():
            menu_bar_screen = menu_bar.update(ev)
            if menu_bar:
                pygame.display.update(menu_bar_screen)
            if menu_bar.choice:
                try:
                    midi_filename = menu_bar.choice_label[-1]
                    print midi_filename

                    p_all_midi_lines, p_notes_in_all_staff = parse_midi.load_midi(midi_filename)
                    piano.draw_piano()
                    p_midi_cmd_idx = 0
                    p_staff_offset_x = 0
                    is_pause = False
                except Exception, e:
                    print "menu error:", e

            # print pygame.event.event_name(ev.type)
            if ev.type == QUIT:
                p_done = True
                break

            elif ev.type == MOUSEBUTTONDOWN:
                if ev.button == 5:
                    p_staff_offset_x += 40

                elif ev.button == 4:
                    p_staff_offset_x -= 40
                    if p_staff_offset_x < 0:
                        p_staff_offset_x = 0

                elif ev.button == 3: # right
                    is_pause = not is_pause

                elif ev.button == 1: # left
                    if ev.pos[1] > 60: # progress bar can not click
                        timestamp_offset_x = (p_staff_offset_x + ev.pos[0]) * piano.timestamp_range * 2 / piano.screen_rect[0]
                        nearest_idx = 0
                        for idx, midi_line in enumerate(p_all_midi_lines):
                            cmd, pitch, volecity_data, pitch_timestamp = midi_line[:4]
                            if timestamp_offset_x > pitch_timestamp:
                                nearest_idx = idx
                                continue
                            if timestamp_offset_x < pitch_timestamp:
                                break

                        piano.draw_piano()
                        p_midi_cmd_idx = nearest_idx
                        last_timestamp = -1

            elif ev.type == KEYUP:
                if ev.key == K_ESCAPE:
                    p_done = True
                    break

                elif ev.key == K_LEFT:
                    p_staff_offset_x -= WINSIZE[0]
                    if p_staff_offset_x < 0:
                        p_staff_offset_x = 0
                elif ev.key == K_RIGHT:
                    p_staff_offset_x += WINSIZE[0]
                elif ev.key == K_DOWN:
                    p_staff_offset_x -= 30
                    if p_staff_offset_x < 0:
                        p_staff_offset_x = 0
                elif ev.key == K_UP:
                    p_staff_offset_x += 30

                elif ev.key == K_m:
                    p_is_metro_on = not p_is_metro_on

                elif ev.key in [K_a, K_b, K_c, K_d, K_e, K_f, K_g, ]:
                    p_key_press = ev.key

                elif ev.key in [K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9]:
                    print "Progress:", ev.key - 48
                    piano.draw_piano()
                    p_midi_cmd_idx = len(p_all_midi_lines) * (ev.key - 48) / 10
                    last_timestamp = -1

                elif ev.key == K_SPACE:
                    is_pause = not is_pause

                elif ev.key == K_RETURN:
                    menus_in_bar = get_menu_data()
                    menu_bar.set(menus_in_bar)

        if menu_bar:
            pygame.display.update()
            clock.tick(7)
            continue

        # get cmd
        try:
            if is_pause or p_midi_cmd_idx >= len(p_all_midi_lines):
                raise Exception("paused")
            midi_line = p_all_midi_lines[p_midi_cmd_idx]
            p_midi_cmd_idx += 1
            # print midi_line

            cmd, pitch, volecity_data, pitch_timestamp = midi_line[:4]
            volecity = player.get_volecity(volecity_data)
            if pitch not in player.g_grand_pitch_range:
                raise Exception("pitch not in range")
            if last_timestamp == -1:
                # init last timestamp
                last_timestamp = pitch_timestamp - 1

        except Exception, e:
            piano.show_notes_staff(p_notes_in_all_staff, pitch_timestamp, WINSIZE[1] * 0.382,
                                   parse_midi.g_bar_duration,
                                   p_staff_offset_x)
            pygame.display.update()
            clock.tick(7)
            continue

        # a chord
        if pitch_timestamp != last_timestamp:
            # print "bps:", utils.g_bps.get_bps_count()
            # utils.show_chord_keys_by_ascii(time_pitchs)

            utils.sync_play_time(pitch_timestamp, last_timestamp, old_time)
            old_time = time.time()
            last_timestamp = pitch_timestamp
            time_pitchs = []
            last_cmd = ""

        # playtrack
        if cmd == "NOTE_ON" or (p_is_metro_on and cmd == "METRO_ON"):
            # sleep after pitch off
            if last_cmd == "NOTE_OFF":
                last_cmd = "NOTE_ON"
                time.sleep(0.02)
            player.play(devices, pitch, volecity, sounds)
            # build chord
            if pitch not in time_pitchs:
                time_pitchs += [pitch]
        elif cmd == "NOTE_OFF" or (p_is_metro_on and cmd == "METRO_OFF"):
            last_cmd = "NOTE_OFF"
            player.stop(devices, pitch, volecity, sounds)

        piano.show_notes_staff(p_notes_in_all_staff, pitch_timestamp, WINSIZE[1] * 0.382,
                               parse_midi.g_bar_duration,
                               p_staff_offset_x)

        # show keys
        piano.show_keys_press(cmd, pitch)
        #clock.tick(10)


if __name__ == '__main__':
    main()
