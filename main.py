#!/usr/bin/env python
#encoding: utf8

""" piano play center
"""


from piano import Piano, TRACK_COLORS, TIMESTAMP_RANGE
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

    menu_bar = MenuSystem.MenuBar(top=5)
    menus_in_bar = get_menu_data()
    menu_bar.set(menus_in_bar)
    menu_bar_info = MenuSystem.MenuBar(top=WINSIZE[1] - menu_bar.lineheigth)
    piano = Piano(screen, WINSIZE, top=menu_bar_info.top - Piano.piano_white_key_height - 2)
    piano.draw_piano()
    piano.draw_lines(WINSIZE[1] * 0.618)

    p_staff_top = menu_bar.top + menu_bar.lineheigth + 30

    clock = pygame.time.Clock()

    p_done = False
    p_key_press = None

    p_midi_filename = "data.midi"
    p_midi_cmd_idx = 0
    p_staff_offset_x = 0
    p_all_midi_lines, p_notes_in_all_staff, p_enabled_tracks, p_tracks_order_idx = parse_midi.load_midi(p_midi_filename)
    piano.timestamp_range = TIMESTAMP_RANGE * parse_midi.g_ticks_per_quarter / parse_midi.g_mseconds_per_quarter
    # draw track pick
    piano.screen.fill(piano.color_backgroud, pygame.Rect(0, menu_bar.top + menu_bar.lineheigth,
                                                         piano.screen_rect[0], 20))
    p_enabled_tracks_switch = {}
    for track_idx, idx in p_tracks_order_idx.items():
        sw = pygame.Rect(idx * 30, menu_bar.top + menu_bar.lineheigth, 29, 20)
        p_enabled_tracks_switch[track_idx] = sw
        note_color = TRACK_COLORS[idx % len(TRACK_COLORS)]
        piano.screen.fill(note_color, sw)

    # load sounds
    devices = player.init()
    sounds = {}
    player.load_sounds(p_all_midi_lines, sounds)

    time_pitchs = []
    last_timestamp = -1
    pitch_timestamp = 0
    old_time = 0
    last_cmd = ""

    is_pause = True
    def get_menus_info_bar():
        gen_menu_data = []
        # gen_menu_data += ["Metro: %.1f" % player.g_metronome_volume]
        gen_menu_data += ["Time: %d/%d" % (parse_midi.g_time_signature_n, parse_midi.g_time_signature_note)]
        gen_menu_data += ["Temp: %d" % (60000 / parse_midi.g_mseconds_per_quarter)]
        gen_menu_data += ["Playing: %s" % p_midi_filename.split("/")[-1].replace(".midi", "").replace(".mid", "")]

        return [MenuSystem.Menu(m, ()) for m in gen_menu_data]

    while not p_done:
        # events
        for ev in pygame.event.get():
            menu_bar_screen = menu_bar.update(ev)
            if menu_bar:
                menu_bar_info.set(get_menus_info_bar())
                pygame.display.update(menu_bar_screen)
                menu_bar_info.update(ev)
            if menu_bar.choice:
                try:
                    p_all_midi_lines, p_notes_in_all_staff, p_enabled_tracks, p_tracks_order_idx = parse_midi.load_midi(
                        menu_bar.choice_label[-1])
                    piano.timestamp_range = TIMESTAMP_RANGE * parse_midi.g_ticks_per_quarter / parse_midi.g_mseconds_per_quarter
                    p_midi_filename = menu_bar.choice_label[-1]
                    print p_midi_filename

                    # draw track pick
                    piano.screen.fill(piano.color_backgroud, pygame.Rect(0, menu_bar.top + menu_bar.lineheigth,
                                                                         piano.screen_rect[0], 20))
                    for track_idx, idx in p_tracks_order_idx.items():
                        if track_idx in p_enabled_tracks_switch:
                            sw = p_enabled_tracks_switch[track_idx]
                            sw.left = idx * 30
                        else:
                            sw = pygame.Rect(idx * 30, menu_bar.top + menu_bar.lineheigth, 29, 20)
                            p_enabled_tracks_switch[track_idx] = sw

                        note_color = TRACK_COLORS[idx % len(TRACK_COLORS)]
                        piano.screen.fill(note_color, sw)

                    # finish missing sounds
                    player.load_sounds(p_all_midi_lines, sounds)

                    piano.draw_piano()
                    p_midi_cmd_idx = 0
                    p_staff_offset_x = 0
                    is_pause = False
                except Exception, e:
                    print "menu error:", e

            if menu_bar.choice:
                menu_bar_info.set(get_menus_info_bar())
                menu_bar_info.update(ev)

            # print pygame.event.event_name(ev.type)
            if ev.type == QUIT:
                p_done = True
                break

            elif ev.type == MOUSEBUTTONUP:
                if ev.pos[1] < 60: # progress bar can not click
                    for track_idx in p_enabled_tracks:
                        sw = p_enabled_tracks_switch[track_idx]
                        if sw.collidepoint(ev.pos):
                            p_enabled_tracks[track_idx] = not p_enabled_tracks[track_idx]

                            idx = p_tracks_order_idx[track_idx]
                            note_color = TRACK_COLORS[idx % len(TRACK_COLORS)]
                            if p_enabled_tracks[track_idx]:
                                piano.screen.fill(note_color, sw)
                            else:
                                piano.screen.fill(piano.color_lines, sw)

            elif ev.type == MOUSEBUTTONDOWN:
                if ev.button == 5:
                    p_staff_offset_x += 40

                elif ev.button == 4:
                    p_staff_offset_x -= 40
                    if p_staff_offset_x < 0:
                        p_staff_offset_x = 0

                elif ev.button == 3: # right
                    is_pause = not is_pause

                elif ev.button == 1:   # left
                    if ev.pos[1] > 60: # progress bar can not click
                        timestamp_offset_x = (
                            p_staff_offset_x +
                            ev.pos[0] +
                            int((ev.pos[1] - p_staff_top) / (28 * piano.piano_staff_width)) * piano.screen_rect[0]
                        ) * piano.timestamp_range / piano.screen_rect[0]
                        nearest_idx = 0
                        for idx, midi_line in enumerate(p_all_midi_lines):
                            cmd, pitch, volecity_data, track_idx, pitch_timestamp = midi_line[:5]
                            if timestamp_offset_x > pitch_timestamp:
                                nearest_idx = idx
                                continue
                            # # debug
                            # for i in p_all_midi_lines[idx:idx+100]:
                            #     print i
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
                    parse_midi.g_mseconds_per_quarter = int(60000 / (60000 / parse_midi.g_mseconds_per_quarter - 10))
                    if parse_midi.g_mseconds_per_quarter > 2000:
                        parse_midi.g_mseconds_per_quarter = 2000
                elif ev.key == K_RIGHT:
                    parse_midi.g_mseconds_per_quarter = int(60000 / (60000 / parse_midi.g_mseconds_per_quarter + 10))
                    if parse_midi.g_mseconds_per_quarter <= 200:
                        parse_midi.g_mseconds_per_quarter = 200

                elif ev.key == K_DOWN:
                    p_staff_offset_x += WINSIZE[0]
                elif ev.key == K_UP:
                    p_staff_offset_x -= WINSIZE[0]
                    if p_staff_offset_x < 0:
                        p_staff_offset_x = 0

                elif ev.key == K_m:
                    if (1.0 - player.g_metronome_volume) / 2 < 0.1:
                        player.g_metronome_volume += 0.1
                    else:
                        player.g_metronome_volume += (1.0 - player.g_metronome_volume) / 2

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
            clock.tick(10)
            continue

        # get cmd
        try:
            if is_pause or p_midi_cmd_idx >= len(p_all_midi_lines):
                raise Exception("paused")
            midi_line = p_all_midi_lines[p_midi_cmd_idx]
            p_midi_cmd_idx += 1
            # print midi_line

            cmd, pitch, volecity_data, track_idx, pitch_timestamp = midi_line[:5]
            volecity = player.get_volecity(volecity_data)
            if pitch not in [0, 1] + player.g_grand_pitch_range:
                continue
            if track_idx >= 0 and not p_enabled_tracks.get(track_idx, False):
                continue

            if last_timestamp == -1:
                # init last timestamp
                last_timestamp = pitch_timestamp - 1

        except Exception, e:
            piano.show_notes_staff(p_enabled_tracks, p_tracks_order_idx, p_notes_in_all_staff, pitch_timestamp,
                                   p_staff_top,
                                   parse_midi.g_bar_duration,
                                   parse_midi.g_time_signature_n,
                                   p_staff_offset_x, is_pause)
            pygame.display.update()
            clock.tick(10)
            continue

        # a chord
        if pitch_timestamp != last_timestamp:
            # print "bps:", utils.g_bps.get_bps_count()
            # utils.show_chord_keys_by_ascii(time_pitchs)
            is_beat_at_right_most, current_play_percent, progress_multi_lines = piano.show_notes_staff(p_enabled_tracks, p_tracks_order_idx, p_notes_in_all_staff, last_timestamp,
                                   p_staff_top,
                                   parse_midi.g_bar_duration,
                                   parse_midi.g_time_signature_n,
                                   p_staff_offset_x, is_pause)

            # scroll page automatically
            if not is_pause and is_beat_at_right_most and current_play_percent > 60:
                p_staff_offset_x += WINSIZE[0] * progress_multi_lines

            utils.sync_play_time(pitch_timestamp, last_timestamp, old_time, sounds)
            old_time = time.time()
            last_timestamp = pitch_timestamp
            time_pitchs = []
            last_cmd = ""

        # playtrack
        if cmd == "NOTE_ON":
            # sleep after pitch off
            if last_cmd == "NOTE_OFF":
                last_cmd = "NOTE_ON"
                #time.sleep(0.02)
            player.play(devices, pitch, volecity, sounds)
            # build chord
            if pitch not in time_pitchs:
                time_pitchs += [pitch]

        elif cmd == "NOTE_OFF":
            last_cmd = "NOTE_OFF"
            player.stop(devices, pitch, volecity, sounds)

        elif cmd == "METRO_ON" and player.g_metronome_volume > 0:
            player.play(devices, pitch, volecity, sounds)

        # show keys
        if pitch > 1:
            piano.show_keys_press(cmd, pitch)
        #clock.tick(10)


if __name__ == '__main__':
    main()
