#!/usr/bin/env python
#encoding: utf8

""" piano play center
"""


from piano import Piano, TIMESTAMP_RANGE, PITCH_OF_KEY_ON_KEYBOARD
from pygame.locals import *

import os
import os.path, sys, random
import parse_midi
import pygame.time
import threading
import time
import player
import utils
import glblit
import MenuSystem


def get_menu_data():
    menu_data_dict = {}
    for (dir_full_path, dirnames, filenames) in os.walk("midi"):
        dir_full_path = dir_full_path.decode("utf8")
        if dir_full_path not in menu_data_dict:
            menu_data_dict[dir_full_path] = []
        menu_data = menu_data_dict[dir_full_path]
        dirname = dir_full_path.rsplit(u"/", 1)[-1]
        menu_data += [dirname]

        for dirname in dirnames:
            dirname = dirname.decode("utf8")
            subdir_full_path = dir_full_path + u"/" + dirname
            if subdir_full_path not in menu_data_dict:
                menu_data_dict[subdir_full_path] = []
            menu_data += [menu_data_dict[subdir_full_path]]

        midi_filenames = [dir_full_path + u"/" + filename.decode("utf8") for filename in filenames
                          if (filename.endswith(".mid") or filename.endswith(".midi"))]
        if midi_filenames:
            menu_data += midi_filenames
        else:
            menu_data += ["."]

    midi_filename_data = []
    menu_data = []

    # for menu_name in menu_data_dict.keys():
    #     print menu_name

    for data in menu_data_dict["midi"]:
        if not isinstance(data, list):
            continue

        sub_menu_data = []
        for data_inner in data[1:]:
            if not data_inner:
                continue

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
        self.screen = glblit.initializeDisplay(*WINSIZE)
        self.screen_rect = self.screen.get_rect()
        pygame.display.set_caption('Piano Center')

        screen = pygame.Surface(WINSIZE)
        # menu
        MenuSystem.init(screen)
        MenuSystem.BGCOLOR = Color(200,200,200, 255)
        MenuSystem.FGCOLOR = Color(0, 0, 0, 0)
        MenuSystem.BGHIGHTLIGHT = Color(40,40,40,40)
        MenuSystem.BORDER_HL = Color(200,200,200,200)

        self.track_button_height = 20
        self.track_button_width = 30
        self.piano_info_bar_gap = 2

        self.menu_bar = MenuSystem.MenuBar(top=5)
        menus_in_bar, self.midi_filename_data = get_menu_data()
        self.menu_bar.set(menus_in_bar)
        self.menu_bar_info = MenuSystem.MenuBar(top=self.screen_rect.height - self.menu_bar.lineheigth)
        self.piano = Piano(screen, WINSIZE,
                           top=self.menu_bar_info.top - Piano.whitekey_height - self.piano_info_bar_gap)

        self.piano.init_piano()
        self.piano.draw_vertical_staff_lines(self.screen_rect.height * 0.618)

        self.staff_top = self.menu_bar.top + self.menu_bar.lineheigth + self.track_button_height

        self.sounds = {}
        self.enabled_tracks_switch = {}

        self.midi_filename_idx = 0
        if len(self.midi_filename_data) > 0:
            self.midi_filename = self.midi_filename_data[self.midi_filename_idx]

        self.load_resource(self.midi_filename)


    def get_menus_info_bar(self):
        gen_menu_data = []
        # gen_menu_data += ["Metro: %.1f" % player.g_metronome_volume]
        gen_menu_data += ["Time: %d/%d" % (parse_midi.g_time_signature_n, parse_midi.g_time_signature_note)]
        gen_menu_data += ["Temp: %d" % (60000 / parse_midi.g_mseconds_per_quarter)]
        gen_menu_data += ["Playing: %s" % self.midi_filename.split("/")[-1].replace(".midi", "").replace(".mid", "")]

        return [MenuSystem.Menu(m, ()) for m in gen_menu_data]


    def load_resource(self, midi_filename):
        print midi_filename
        try:
            self.all_midi_lines, self.notes_in_all_staff, self.enabled_tracks, self.tracks_order_idx = parse_midi.load_midi(midi_filename)
            self.all_midi_lines_length = len(self.all_midi_lines)
        except Exception, e:
            print "midi error:", e
            if midi_filename in self.midi_filename_data:
                self.midi_filename_data.remove(midi_filename)
            return

        self.piano.timestamp_range = TIMESTAMP_RANGE * parse_midi.g_ticks_per_quarter / parse_midi.g_mseconds_per_quarter
        self.piano.timestamp_range = self.piano.timestamp_range * self.piano.staff_space_height_base / self.piano.staff_space_height

        if midi_filename in self.midi_filename_data:
            self.midi_filename_idx = self.midi_filename_data.index(midi_filename)
            self.midi_filename = midi_filename
        else:
            print "impossible: file not in menu list"
            return

        # draw track pick
        self.piano.screen.fill(self.piano.color_backgroud,
                               pygame.Rect(0, self.menu_bar.top + self.menu_bar.lineheigth,
                                           self.screen_rect.width, self.track_button_height-1))
        for track_idx, idx in self.tracks_order_idx.items():
            if track_idx in self.enabled_tracks_switch:
                sw = self.enabled_tracks_switch[track_idx]
                sw.left = idx * self.track_button_width
            else:
                sw = pygame.Rect(idx * self.track_button_width, self.menu_bar.top + self.menu_bar.lineheigth,
                                 self.track_button_width - 1, self.track_button_height-1)
                self.enabled_tracks_switch[track_idx] = sw

            note_color = self.piano.TRACK_COLORS[idx % len(self.piano.TRACK_COLORS)]
            self.piano.screen.fill(note_color, sw)

        # finish missing sounds
        player.load_sounds([(midi_data[1], midi_data[2]) for midi_data in self.all_midi_lines],
                           self.sounds)
        self.piano.reset_piano()
        self.chord_keys_bound = []
        self.play_commands = []
        self.midi_cmd_idx = 0
        self.staff_offset_x = 0
        self.last_timestamp = -1
        self.is_pause = True
        self.play_one_timestamp_while_paused = False
        self.menu_bar_info.set(self.get_menus_info_bar())


    def gl_screen_blit(self):
        self.textureset = glblit.Textureset()
        self.textureset.set('opengl', glblit.Surface_Texture(self.piano.screen, self.screen_rect))
        sur_image = glblit.GL_Image(self.textureset, 'opengl')
        sur_image.draw((0, 0), rotation=180)


    def main(self):
        """Play a midi file with sound samples
        """
        player.init()
        clock = pygame.time.Clock()
        old_time = 0
        p_done = False

        pitch_offset = 60
        need_update_display = True
        while not p_done:
            # events
            for ev in pygame.event.get():
                need_update_display = True
                menu_bar_screen = self.menu_bar.update(ev)
                if self.menu_bar:
                    self.menu_bar_info.set(self.get_menus_info_bar())
                    # self.menu_bar_info.update(ev)

                if self.menu_bar.choice:
                    try:
                        self.load_resource(self.menu_bar.choice_label[-1])
                    except Exception, e:
                        print "menu error:", e
                    # if have choice, continue event
                    continue

                if ev.type == MOUSEBUTTONUP:
                    if ev.pos[1] > 60:
                        continue
                    # enable/disable tracks
                    for track_idx in self.enabled_tracks:
                        sw = self.enabled_tracks_switch[track_idx]
                        if sw.collidepoint(ev.pos):
                            self.enabled_tracks[track_idx] = not self.enabled_tracks[track_idx]

                            idx = self.tracks_order_idx[track_idx]
                            note_color = self.piano.TRACK_COLORS[idx % len(self.piano.TRACK_COLORS)]
                            if self.enabled_tracks[track_idx]:
                                self.piano.screen.fill(note_color, sw)
                            else:
                                self.piano.screen.fill(self.piano.color_lines, sw)

                elif ev.type == MOUSEBUTTONDOWN:
                    if ev.button == 5: # scroll down
                        self.staff_offset_x += 40

                    elif ev.button == 4: # scroll up
                        self.staff_offset_x -= 40
                        if self.staff_offset_x < 0:
                            self.staff_offset_x = 0

                    elif ev.button == 3: # right button
                        self.is_pause = not self.is_pause

                    elif ev.button == 1:   # left button
                        if ev.pos[1] < 60: # progress bar can not click
                            continue
                        clicked_staff_number = int((ev.pos[1] - self.staff_top) / (self.piano.staff_total_lines * self.piano.staff_space_height))
                        wraped_staff_offset = 0
                        if clicked_staff_number > 0:
                            wraped_staff_offset += self.piano.lastbar_pos_in_line1
                        if clicked_staff_number > 1:
                            wraped_staff_offset += self.piano.lastbar_pos_in_line2 * (clicked_staff_number-1)

                        timestamp_offset_x = (
                            self.staff_offset_x +
                            ev.pos[0] +
                            wraped_staff_offset
                        ) * self.piano.timestamp_range / self.screen_rect.width

                        self.last_timestamp = -1
                        for idx, midi_line in enumerate(self.all_midi_lines):
                            cmd, pitch, volecity_data, track_idx, pitch_timestamp = midi_line[:5]
                            if timestamp_offset_x > pitch_timestamp:
                                if self.last_timestamp != pitch_timestamp:
                                    self.midi_cmd_idx = idx
                                    self.last_timestamp = pitch_timestamp
                            elif timestamp_offset_x < pitch_timestamp:
                                break

                        self.play_one_timestamp_while_paused = True
                        self.piano.reset_piano()


                elif ev.type == KEYUP:
                    if ev.key == K_ESCAPE:
                        p_done = True
                        break

                    # MENU Reload
                    elif ev.key == K_RETURN:
                        menus_in_bar, self.midi_filename_data = get_menu_data()
                        self.menu_bar.set(menus_in_bar)

                    # Stop
                    elif ev.key == K_s:
                        self.piano.reset_piano()
                        self.staff_offset_x = 0
                        self.midi_cmd_idx = 0
                        self.last_timestamp = -1
                        self.is_pause = True

                    # Pause/Play
                    elif ev.key == K_SPACE:
                        self.is_pause = not self.is_pause

                    # is_longbar_show
                    elif ev.key == K_c:
                        self.piano.is_longbar_show = not self.piano.is_longbar_show

                    elif ev.key == K_LEFT:
                        # Slower
                        parse_midi.g_mseconds_per_quarter = int(60000 / (
                            60000 / parse_midi.g_mseconds_per_quarter - 10))
                        if parse_midi.g_mseconds_per_quarter > 2000:
                            parse_midi.g_mseconds_per_quarter = 2000
                        self.menu_bar_info.set(self.get_menus_info_bar())
                    elif ev.key == K_RIGHT:
                        # Faster
                        parse_midi.g_mseconds_per_quarter = int(60000 / (
                            60000 / parse_midi.g_mseconds_per_quarter + 10))
                        if parse_midi.g_mseconds_per_quarter <= 200:
                            parse_midi.g_mseconds_per_quarter = 200
                        self.menu_bar_info.set(self.get_menus_info_bar())

                    #Page_Up/Page_Down
                    elif ev.key == K_DOWN:
                        self.staff_offset_x += self.piano.lastbar_pos_in_line1
                    elif ev.key == K_UP:
                        self.staff_offset_x -= self.piano.lastbar_pos_in_line1
                        if self.staff_offset_x < 0:
                            self.staff_offset_x = 0

                    # Previous/Next MIDI
                    elif ev.key in [K_COMMA, K_PERIOD]:
                        need_reload = False
                        if ev.key == K_COMMA:
                            if self.midi_filename_idx > 0:
                                midi_filename_idx = self.midi_filename_idx-1
                                need_reload = True
                        elif ev.key == K_PERIOD:
                            if self.midi_filename_idx+1 < len(self.midi_filename_data):
                                midi_filename_idx = self.midi_filename_idx + 1
                                need_reload = True
                        if need_reload:
                            midi_filename = self.midi_filename_data[midi_filename_idx]
                            self.load_resource(midi_filename)

                    # Metronome
                    elif ev.key == K_m:
                        if (1.0 - player.g_metronome_volume) / 2 < 0.1:
                            player.g_metronome_volume += 0.1
                        else:
                            player.g_metronome_volume += (1.0 - player.g_metronome_volume) / 2

                    # # Set Progress Percent
                    # elif ev.key in [K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9]:
                    #     self.piano.reset_piano()
                    #     self.midi_cmd_idx = self.all_midi_lines_length * (ev.key - 48) / 10
                    #     self.last_timestamp = -1

                    # Set Pitch Offset
                    elif ev.key in [K_v, K_b, K_n]:
                        pitch_offset = {K_v: 36,  K_b: 60,  K_n: 84}[ev.key]

                    elif ev.key == K_f:
                        player.g_volecity_adjust = (player.g_volecity_adjust+1) % len(player.g_volecity_list)
                        player.load_sounds([(midi_data[1], midi_data[2]) for midi_data in self.all_midi_lines],
                                           self.sounds)

                    elif ev.key == K_z:
                        if self.piano.staff_space_height > 2:
                            self.piano.staff_space_height /= 2
                        self.piano.timestamp_range = TIMESTAMP_RANGE * parse_midi.g_ticks_per_quarter / parse_midi.g_mseconds_per_quarter
                        self.piano.timestamp_range = self.piano.timestamp_range * self.piano.staff_space_height_base / self.piano.staff_space_height
                    elif ev.key == K_x:
                        if self.piano.staff_space_height < 16:
                            self.piano.staff_space_height *= 2
                        self.piano.timestamp_range = TIMESTAMP_RANGE * parse_midi.g_ticks_per_quarter / parse_midi.g_mseconds_per_quarter
                        self.piano.timestamp_range = self.piano.timestamp_range * self.piano.staff_space_height_base / self.piano.staff_space_height

                    # Play Piano with keys
                    elif ev.key in PITCH_OF_KEY_ON_KEYBOARD:
                        pitch = pitch_offset + PITCH_OF_KEY_ON_KEYBOARD.index(ev.key)
                        player.stop(pitch, 100, self.sounds)
                        player.load_sounds([(pitch, 100)], self.sounds)
                        cmd = "NOTE_OFF"
                        self.piano.show_keys_press(cmd, pitch)

                elif ev.type == KEYDOWN:
                    if ev.key in PITCH_OF_KEY_ON_KEYBOARD:
                        pitch = pitch_offset + PITCH_OF_KEY_ON_KEYBOARD.index(ev.key)
                        player.load_sounds([(pitch, 100)], self.sounds)
                        player.play(pitch, 100, self.sounds)
                        cmd = "NOTE_ON"
                        self.piano.show_keys_press(cmd, pitch)

            # must out of events loop
            if self.menu_bar or self.menu_bar.choice:
                self.gl_screen_blit()
                pygame.display.flip()
                clock.tick(10)
                continue

            # get cmd
            try:
                if (self.is_pause and not self.play_one_timestamp_while_paused) or self.midi_cmd_idx >= self.all_midi_lines_length:
                    raise Exception("paused")
                midi_line = self.all_midi_lines[self.midi_cmd_idx]
                self.midi_cmd_idx += 1
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
                if need_update_display:
                    self.piano.show_notes_staff_in_page(self.enabled_tracks, self.tracks_order_idx,
                                            self.notes_in_all_staff, self.last_timestamp,
                                            self.staff_top,
                                            parse_midi.g_bar_duration,
                                            parse_midi.g_time_signature_n,
                                            self.staff_offset_x, self.is_pause)
                    has_stoped = player.real_stop(self.sounds)
                    self.gl_screen_blit()
                    pygame.display.flip()
                    need_update_display = False

                clock.tick(40)
                continue

            # a chord
            if pitch_timestamp != self.last_timestamp:
                # show one step ahead
                # self.piano.draw_vertical_staff_lines(self.screen_rect.height * 0.618)

                midi_cmd_idx_old = self.midi_cmd_idx-1
                while midi_cmd_idx_old < self.all_midi_lines_length:
                    step_head_midi_line = self.all_midi_lines[midi_cmd_idx_old]
                    midi_cmd_idx_old += 1
                    step_head_cmd, step_head_pitch, step_head_volecity_data, step_head_track_idx, step_head_pitch_timestamp = step_head_midi_line[:5]
                    step_head_volecity = player.get_volecity(step_head_volecity_data)
                    if pitch_timestamp != step_head_pitch_timestamp:
                        break
                    if step_head_pitch not in [0, 1] + player.g_grand_pitch_range:
                        continue
                    if step_head_track_idx >= 0 and not self.enabled_tracks.get(step_head_track_idx, False):
                        continue
                    if step_head_pitch > 1:
                        self.piano.show_keys_predict(step_head_cmd, step_head_pitch, step_head_volecity)

                # print "bps:", utils.g_bps.get_bps_count()
                # utils.show_chord_keys_by_ascii(self.chord_keys_bound)
                (is_beat_at_right_most, current_play_percent,
                 progress_multi_lines, page_end_offset_x) = self.piano.show_notes_staff_in_page(
                     self.enabled_tracks, self.tracks_order_idx,
                     self.notes_in_all_staff, self.last_timestamp,
                     self.staff_top,
                     parse_midi.g_bar_duration,
                     parse_midi.g_time_signature_n,
                     self.staff_offset_x, self.is_pause)

                # scroll page automatically
                if not self.is_pause and is_beat_at_right_most and (current_play_percent == 0 or current_play_percent > (100 - 50 / progress_multi_lines)):
                    self.staff_offset_x = page_end_offset_x

                utils.sync_play_time(self, pitch_timestamp, old_time)
                old_time = time.time()
                self.last_timestamp = pitch_timestamp
                self.chord_keys_bound = []
                self.play_commands = []
                if self.is_pause and self.play_one_timestamp_while_paused:
                    self.play_one_timestamp_while_paused = False
                    continue

            self.play_commands += [(cmd, pitch, volecity)]
            # playtrack
            if cmd == "NOTE_ON":
                # build chord
                if pitch not in self.chord_keys_bound:
                    self.chord_keys_bound += [pitch]

            # show keys
            if pitch > 1:
                self.piano.show_keys_press(cmd, pitch, volecity)


if __name__ == '__main__':

    playcenter = PlayCenter()
    playcenter.main()
