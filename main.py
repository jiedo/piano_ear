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
    for (dir_full_path, dirnames, filenames) in os.walk("midi"):
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
        # elif not dirnames:
        #     menu_data += [u"."]

    midi_filename_data = []
    menu_data = []
    for data in menu_data_dict["midi"]:
        if not isinstance(data, list):
            continue

        sub_menu_data = []
        for data_inner in data[1:]:
            if not isinstance(data_inner, list):
                sub_menu_data += [data_inner]
                midi_filename_data += [data_inner]
                continue

            subsub_menu_data = []
            for data_inner_inner in data_inner[1:]:
                if not isinstance(data_inner_inner, list):
                    subsub_menu_data += [data_inner_inner]
                    midi_filename_data += [data_inner_inner]
            sub_menu_data += [MenuSystem.Menu(data_inner[0], subsub_menu_data)]

        menu_data += [MenuSystem.Menu(data[0], sub_menu_data)]

    return menu_data, midi_filename_data


WINSIZE = [1248, 740]

class PlayCenter():
    def __init__(self):
        pygame.init()
        screen = pygame.display.set_mode(WINSIZE)
        pygame.display.set_caption('Piano Center')

        # menu
        MenuSystem.init()
        MenuSystem.BGCOLOR = Color(200,200,200, 255)
        MenuSystem.FGCOLOR = Color(0, 0, 0, 0)
        MenuSystem.BGHIGHTLIGHT = Color(40,40,40,40)
        MenuSystem.BORDER_HL = Color(200,200,200,200)

        self.menu_bar = MenuSystem.MenuBar(top=5)
        menus_in_bar, self.midi_filename_data = get_menu_data()
        self.menu_bar.set(menus_in_bar)
        self.menu_bar_info = MenuSystem.MenuBar(top=WINSIZE[1] - self.menu_bar.lineheigth)
        self.piano = Piano(screen, WINSIZE, top=self.menu_bar_info.top - Piano.piano_white_key_height - 2)
        self.piano.draw_piano()
        self.piano.draw_lines(WINSIZE[1] * 0.618)

        self.staff_top = self.menu_bar.top + self.menu_bar.lineheigth + 30

        self.done = False
        self.key_press = None

        self.sounds = {}
        self.enabled_tracks_switch = {}

        self.midi_filename_idx = 0
        if len(self.midi_filename_data) > 0:
            self.midi_filename = self.midi_filename_data[self.midi_filename_idx]

        self.load_resource()


    def get_menus_info_bar(self):
        gen_menu_data = []
        # gen_menu_data += ["Metro: %.1f" % player.g_metronome_volume]
        gen_menu_data += ["Time: %d/%d" % (parse_midi.g_time_signature_n, parse_midi.g_time_signature_note)]
        gen_menu_data += ["Temp: %d" % (60000 / parse_midi.g_mseconds_per_quarter)]
        gen_menu_data += ["Playing: %s" % self.midi_filename.split("/")[-1].replace(".midi", "").replace(".mid", "")]

        return [MenuSystem.Menu(m, ()) for m in gen_menu_data]


    def load_resource(self):
        print self.midi_filename

        self.all_midi_lines, self.notes_in_all_staff, self.enabled_tracks, self.tracks_order_idx = parse_midi.load_midi(self.midi_filename)
        self.piano.timestamp_range = TIMESTAMP_RANGE * parse_midi.g_ticks_per_quarter / parse_midi.g_mseconds_per_quarter
        if self.midi_filename in self.midi_filename_data:
            self.midi_filename_idx = self.midi_filename_data.index(self.midi_filename)
        else:
            print "impossible: file not in menu list"

        # draw track pick
        self.piano.screen.fill(self.piano.color_backgroud,
                               pygame.Rect(0, self.menu_bar.top + self.menu_bar.lineheigth,
                                           self.piano.screen_rect[0], 20))
        for track_idx, idx in self.tracks_order_idx.items():
            if track_idx in self.enabled_tracks_switch:
                sw = self.enabled_tracks_switch[track_idx]
                sw.left = idx * 30
            else:
                sw = pygame.Rect(idx * 30, self.menu_bar.top + self.menu_bar.lineheigth, 29, 20)
                self.enabled_tracks_switch[track_idx] = sw

            note_color = TRACK_COLORS[idx % len(TRACK_COLORS)]
            self.piano.screen.fill(note_color, sw)

        # finish missing sounds
        player.load_sounds(self.all_midi_lines, self.sounds)
        self.piano.draw_piano()

        self.time_pitchs = []
        self.midi_cmd_idx = 0
        self.staff_offset_x = 0
        self.last_timestamp = 0
        self.is_pause = True


    def main(self):
        """Play a midi file with sound samples
        """
        devices = player.init()
        clock = pygame.time.Clock()
        old_time = 0
        last_cmd = ""
        while not self.done:
            # events
            for ev in pygame.event.get():
                menu_bar_screen = self.menu_bar.update(ev)
                if self.menu_bar:
                    self.menu_bar_info.set(self.get_menus_info_bar())
                    pygame.display.update(menu_bar_screen)
                    self.menu_bar_info.update(ev)
                if self.menu_bar.choice:
                    try:
                        self.midi_filename = self.menu_bar.choice_label[-1]
                        self.load_resource()
                    except Exception, e:
                        print "menu error:", e

                    self.menu_bar_info.set(self.get_menus_info_bar())
                    self.menu_bar_info.update(ev)
                    # if have choice, continue event

                elif ev.type == QUIT:
                    self.done = True
                    break
                elif ev.type == MOUSEBUTTONUP:
                    if ev.pos[1] < 60:
                        # progress bar can not click
                        for track_idx in self.enabled_tracks:
                            sw = self.enabled_tracks_switch[track_idx]
                            if sw.collidepoint(ev.pos):
                                self.enabled_tracks[track_idx] = not self.enabled_tracks[track_idx]

                                idx = self.tracks_order_idx[track_idx]
                                note_color = TRACK_COLORS[idx % len(TRACK_COLORS)]
                                if self.enabled_tracks[track_idx]:
                                    self.piano.screen.fill(note_color, sw)
                                else:
                                    self.piano.screen.fill(self.piano.color_lines, sw)

                elif ev.type == MOUSEBUTTONDOWN:
                    if ev.button == 5:
                        self.staff_offset_x += 40

                    elif ev.button == 4:
                        self.staff_offset_x -= 40
                        if self.staff_offset_x < 0:
                            self.staff_offset_x = 0

                    elif ev.button == 3: # right
                        self.is_pause = not self.is_pause

                    elif ev.button == 1:   # left
                        if ev.pos[1] > 60: # progress bar can not click
                            timestamp_offset_x = (
                                self.staff_offset_x +
                                ev.pos[0] +
                                int((ev.pos[1] - self.staff_top) / (28 * self.piano.piano_staff_width)) * self.piano.screen_rect[0]
                            ) * self.piano.timestamp_range / self.piano.screen_rect[0]
                            nearest_idx = 0
                            for idx, midi_line in enumerate(self.all_midi_lines):
                                cmd, pitch, volecity_data, track_idx, pitch_timestamp = midi_line[:5]
                                if timestamp_offset_x > pitch_timestamp:
                                    nearest_idx = idx
                                    continue
                                # # debug
                                # for i in self.all_midi_lines[idx:idx+100]:
                                #     print i
                                if timestamp_offset_x < pitch_timestamp:
                                    break

                            self.piano.draw_piano()
                            self.midi_cmd_idx = nearest_idx
                            self.last_timestamp = -1

                elif ev.type == KEYUP:
                    if ev.key == K_ESCAPE:
                        self.done = True
                        break

                    elif ev.key == K_p:
                        if self.midi_filename_idx > 0:
                            self.midi_filename = self.midi_filename_data[self.midi_filename_idx-1]
                            self.load_resource()

                    elif ev.key == K_n:
                        if self.midi_filename_idx+1 < len(self.midi_filename_data):
                            self.midi_filename = self.midi_filename_data[self.midi_filename_idx+1]
                            self.load_resource()

                    elif ev.key == K_LEFT:
                        parse_midi.g_mseconds_per_quarter = int(60000 / (60000 / parse_midi.g_mseconds_per_quarter - 10))
                        if parse_midi.g_mseconds_per_quarter > 2000:
                            parse_midi.g_mseconds_per_quarter = 2000
                    elif ev.key == K_RIGHT:
                        parse_midi.g_mseconds_per_quarter = int(60000 / (60000 / parse_midi.g_mseconds_per_quarter + 10))
                        if parse_midi.g_mseconds_per_quarter <= 200:
                            parse_midi.g_mseconds_per_quarter = 200

                    elif ev.key == K_DOWN:
                        self.staff_offset_x += WINSIZE[0]
                    elif ev.key == K_UP:
                        self.staff_offset_x -= WINSIZE[0]
                        if self.staff_offset_x < 0:
                            self.staff_offset_x = 0

                    elif ev.key == K_m:
                        if (1.0 - player.g_metronome_volume) / 2 < 0.1:
                            player.g_metronome_volume += 0.1
                        else:
                            player.g_metronome_volume += (1.0 - player.g_metronome_volume) / 2

                    elif ev.key in [K_a, K_b, K_c, K_d, K_e, K_f, K_g, ]:
                        self.key_press = ev.key

                    elif ev.key == K_s: # stop
                        self.piano.draw_piano()
                        self.midi_cmd_idx = 0
                        self.last_timestamp = 0
                        self.is_pause = True

                    elif ev.key in [K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9]:
                        print "Progress:", ev.key - 48
                        self.piano.draw_piano()
                        self.midi_cmd_idx = len(self.all_midi_lines) * (ev.key - 48) / 10
                        self.last_timestamp = -1

                    elif ev.key == K_SPACE:
                        self.is_pause = not self.is_pause

                    elif ev.key == K_RETURN:
                        menus_in_bar, self.midi_filename_data = get_menu_data()
                        self.menu_bar.set(menus_in_bar)

            if self.menu_bar:
                pygame.display.update()
                clock.tick(10)
                continue

            # get cmd
            try:
                if self.is_pause or self.midi_cmd_idx >= len(self.all_midi_lines):
                    raise Exception("paused")
                midi_line = self.all_midi_lines[self.midi_cmd_idx]
                self.midi_cmd_idx += 1
                # print midi_line

                cmd, pitch, volecity_data, track_idx, pitch_timestamp = midi_line[:5]
                volecity = player.get_volecity(volecity_data)
                if pitch not in [0, 1] + player.g_grand_pitch_range:
                    continue
                if track_idx >= 0 and not self.enabled_tracks.get(track_idx, False):
                    continue

                if self.last_timestamp == -1:
                    # init last timestamp
                    self.last_timestamp = pitch_timestamp - 1

            except Exception, e:
                self.piano.show_notes_staff(self.enabled_tracks, self.tracks_order_idx, self.notes_in_all_staff, self.last_timestamp,
                                       self.staff_top,
                                       parse_midi.g_bar_duration,
                                       parse_midi.g_time_signature_n,
                                       self.staff_offset_x, self.is_pause)
                pygame.display.update()
                clock.tick(10)
                continue

            # a chord
            if pitch_timestamp != self.last_timestamp:
                # print "bps:", utils.g_bps.get_bps_count()
                # utils.show_chord_keys_by_ascii(self.time_pitchs)
                is_beat_at_right_most, current_play_percent, progress_multi_lines = self.piano.show_notes_staff(self.enabled_tracks, self.tracks_order_idx, self.notes_in_all_staff, self.last_timestamp,
                                       self.staff_top,
                                       parse_midi.g_bar_duration,
                                       parse_midi.g_time_signature_n,
                                       self.staff_offset_x, self.is_pause)

                # scroll page automatically
                if not self.is_pause and is_beat_at_right_most and (current_play_percent == 0 or current_play_percent > (100 - 50 / progress_multi_lines)):
                    self.staff_offset_x += WINSIZE[0] * progress_multi_lines

                utils.sync_play_time(pitch_timestamp, self.last_timestamp, old_time, self.sounds)
                old_time = time.time()
                self.last_timestamp = pitch_timestamp
                self.time_pitchs = []
                last_cmd = ""

            # playtrack
            if cmd == "NOTE_ON":
                # sleep after pitch off
                if last_cmd == "NOTE_OFF":
                    last_cmd = "NOTE_ON"
                    #time.sleep(0.02)
                player.play(devices, pitch, volecity, self.sounds)
                # build chord
                if pitch not in self.time_pitchs:
                    self.time_pitchs += [pitch]

            elif cmd == "NOTE_OFF":
                last_cmd = "NOTE_OFF"
                player.stop(devices, pitch, volecity, self.sounds)

            elif cmd == "METRO_ON" and player.g_metronome_volume > 0:
                player.play(devices, pitch, volecity, self.sounds)

            # show keys
            if pitch > 1:
                self.piano.show_keys_press(cmd, pitch)
            #clock.tick(10)


if __name__ == '__main__':

    playcenter = PlayCenter()
    playcenter.main()
