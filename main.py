#!/usr/bin/env python
#encoding: utf8

""" piano play center
"""

import math
import pyglet
from pyglet.gl import *
from pyglet.window import key # 键盘常量，事件


from piano import Piano, TIMESTAMP_RANGE, Rect

import os
import os.path, sys, random
import parse_midi

import time
import player
import utils


class MenuSystem():
    class MenuBar(list):
        def __init__(self, top):
            self.top = top
            self.lineheigth = 10
            pass

    class Menu():
        def __init__(self, name, data):
            pass

    def __init__(self):
        pass

    def init(self):
        pass



WINSIZE = [1248, 740]

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


# def new_line(batch, ):
#     self.batch.add(4, GL_QUADS, None,
#                    ('v2i/static', vertex_data),
#                    ('c4B', (0, 255, 255, 0) * 4))

#     self.batch.add(4, GL_LINES, None,
#                    ('v2i/static', vertex_data),
#                    ('c4B', (0, 255, 255, 0) * 4))

#     blank_image = pyglet.image.create(cw, ch, pyglet.image.SolidColorImagePattern((200,)*4))
#     sprites = [pyglet.sprite.Sprite(blank_image, batch=batch) for i in range(100)]


class PlayCenter(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        # *args,化序列为位置参数：(1,2) -> func(1,2)
        # **kwargs,化字典为关键字参数：{'a':1,'b':2} -> func(a=1,b=2)
        super(PlayCenter, self).__init__(*args, **kwargs)
        self.batch = pyglet.graphics.Batch()

        # 游戏窗口左上角的label参数设置
        self.label = pyglet.text.Label('', font_name='Arial', font_size=18,
            x=10, y=self.height - 10, anchor_x='left', anchor_y='top',
            color=(255, 0, 0, 255))

        # vertex_data = (34, 53, 44, 22, 422, 64, 42, 44)
        # self.batch.add(4, GL_LINES, None,
        #                ('v2i/static', vertex_data),
        #                ('c4B', (0, 255, 255, 255) * 4))

        # GL_LINE_LOOP
        # GL_QUADS

        # vertex_data = (134, 153, 244, 122, 242, 264, 102, 204)
        # self.batch.add(4, GL_QUADS, None,
        #                ('v2i/static', vertex_data),
        #                ('c4B', (0, 255, 255, 0) * 4))

        pyglet.clock.schedule_interval(self.main_loop, 1.0 / 1000)

        self.set_2d()           # 进入2d模式

        ################################################################ init
        # # menu
        # MenuSystem.init()
        # MenuSystem.BGCOLOR = Color(200,200,200, 255)
        # MenuSystem.FGCOLOR = Color(0, 0, 0, 0)
        # MenuSystem.BGHIGHTLIGHT = Color(40,40,40,40)
        # MenuSystem.BORDER_HL = Color(200,200,200,200)

        self.menu_bar = MenuSystem.MenuBar(top=9)
        menus_in_bar, self.midi_filename_data = get_menu_data()
        # self.menu_bar.set(menus_in_bar)

        self.menu_bar_info = MenuSystem.MenuBar(top=WINSIZE[1] - self.menu_bar.lineheigth)
        self.piano = Piano(self.batch, WINSIZE, top=self.menu_bar_info.top - Piano.piano_white_key_height - 2)
        self.piano.draw_piano()
        self.piano.draw_vertical_staff_lines(WINSIZE[1] * 0.618)

        self.staff_top = self.menu_bar.top + self.menu_bar.lineheigth + 30

        self.sounds = {}
        self.enabled_tracks_switch = {}

        self.midi_filename_idx = 0
        if len(self.midi_filename_data) > 0:
            self.midi_filename = self.midi_filename_data[self.midi_filename_idx]

        self.load_resource(self.midi_filename)


        ################################################################ main init
        self.devices = player.init()
        #clock = pygame.time.Clock()
        self.old_time = 0
        self.pitch_offset = 60
        self.pitch_of_key_on_keyboard = [key.TAB, key._1,
                                    key.Q, key._2,
                                    key.W,
                                    key.E, key._4,
                                    key.R, key._5,
                                    key.T, key._6,
                                    key.Y,

                                    key.U, key._8,
                                    key.I, key._9,
                                    key.O,
                                    key.P, key.MINUS,
                                    key.BRACKETLEFT, key.EQUAL,
                                    key.BRACKETRIGHT, key.BACKSPACE,
                                    key.BACKSLASH, ]
        self.need_update_display = True


    # 按下键盘事件
    def on_key_press(self, symbol, modifiers):
        print symbol, modifiers
        # MENU Reload
        if symbol == key.RETURN:
            menus_in_bar, self.midi_filename_data = get_menu_data()
            # self.menu_bar.set(menus_in_bar)

        # Stop
        elif symbol == key.S:
            self.piano.draw_piano()
            self.staff_offset_x = 0
            self.midi_cmd_idx = 0
            self.last_timestamp = 0
            self.is_pause = True

        # Pause/Play
        elif symbol == key.SPACE:
            self.is_pause = not self.is_pause

        # is_show_longbar_in_staff
        elif symbol == key.C:
            self.piano.is_show_longbar_in_staff = not self.piano.is_show_longbar_in_staff

        elif symbol == key.LEFT:
            # Slower
            parse_midi.g_mseconds_per_quarter = int(60000 / (
                60000 / parse_midi.g_mseconds_per_quarter - 10))
            if parse_midi.g_mseconds_per_quarter > 2000:
                parse_midi.g_mseconds_per_quarter = 2000
            # self.menu_bar_info.set(self.get_menus_info_bar())
            # self.menu_bar_info.update(ev)
        elif symbol == key.RIGHT:
            # Faster
            parse_midi.g_mseconds_per_quarter = int(60000 / (
                60000 / parse_midi.g_mseconds_per_quarter + 10))
            if parse_midi.g_mseconds_per_quarter <= 200:
                parse_midi.g_mseconds_per_quarter = 200
            # self.menu_bar_info.set(self.get_menus_info_bar())
            # self.menu_bar_info.update(ev)

        #Page_Up/Page_Down
        elif symbol == key.DOWN:
            self.staff_offset_x += self.piano.first_line_last_bar_pos
        elif symbol == key.UP:
            self.staff_offset_x -= self.piano.first_line_last_bar_pos
            if self.staff_offset_x < 0:
                self.staff_offset_x = 0

        # Previous/Next MIDI
        elif symbol in [key.COMMA, key.PERIOD]:
            need_reload = False
            if symbol == key.COMMA:
                if self.midi_filename_idx > 0:
                    midi_filename_idx = self.midi_filename_idx-1
                    need_reload = True
            elif symbol == key.PERIOD:
                if self.midi_filename_idx+1 < len(self.midi_filename_data):
                    midi_filename_idx = self.midi_filename_idx + 1
                    need_reload = True
            if need_reload:
                midi_filename = self.midi_filename_data[midi_filename_idx]
                self.load_resource(midi_filename)
                # self.menu_bar_info.set(self.get_menus_info_bar())
                # self.menu_bar_info.update(ev)

        # Metronome
        elif symbol == key.M:
            if (1.0 - player.g_metronome_volume) / 2 < 0.1:
                player.g_metronome_volume += 0.1
            else:
                player.g_metronome_volume += (1.0 - player.g_metronome_volume) / 2

        # # Set Progress Percent
        # elif symbol in [key._0, key._1, key._2, key._3, key._4, key._5, key._6, key._7, key._8, key._9]:
        #     self.piano.draw_piano()
        #     self.midi_cmd_idx = len(self.all_midi_lines) * (symbol - 48) / 10
        #     self.last_timestamp = -1

        # Set Pitch Offset
        elif symbol in [key.V, key.B, key.N]:
            self.pitch_offset = {key.V: 36,  key.B: 60,  key.N: 84}[symbol]

        elif symbol in [key.Z]:
            if self.piano.piano_staff_line_width > 2:
                self.piano.piano_staff_line_width /= 2
            self.piano.timestamp_range = TIMESTAMP_RANGE * parse_midi.g_ticks_per_quarter / parse_midi.g_mseconds_per_quarter
            self.piano.timestamp_range = self.piano.timestamp_range * self.piano.piano_staff_line_width_base / self.piano.piano_staff_line_width
        elif symbol in [key.X]:
            if self.piano.piano_staff_line_width < 16:
                self.piano.piano_staff_line_width *= 2
            self.piano.timestamp_range = TIMESTAMP_RANGE * parse_midi.g_ticks_per_quarter / parse_midi.g_mseconds_per_quarter
            self.piano.timestamp_range = self.piano.timestamp_range * self.piano.piano_staff_line_width_base / self.piano.piano_staff_line_width

        # Play Piano with keys
        elif symbol in self.pitch_of_key_on_keyboard:
            pitch = self.pitch_offset + self.pitch_of_key_on_keyboard.index(symbol)
            player.stop(self.devices, pitch, 100, self.sounds)
            player.load_sounds([(pitch, 100)], self.sounds)
            cmd = "NOTE_OFF"
            self.piano.show_keys_press(cmd, pitch)


    # 释放按键
    def on_key_release(self, symbol, modifiers):
        print symbol, modifiers
        if symbol in self.pitch_of_key_on_keyboard:
            pitch = self.pitch_offset + self.pitch_of_key_on_keyboard.index(symbol)
            player.load_sounds([(pitch, 100)], self.sounds)
            player.play(self.devices, pitch, 100, self.sounds)
            cmd = "NOTE_ON"
            self.piano.show_keys_press(cmd, pitch)


    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        move_tick = scroll_y
        if scroll_x > 0:
            move_tick = scroll_x

        self.staff_offset_x += (move_tick * 40)
        if self.staff_offset_x < 0:
            self.staff_offset_x = 0


    # 鼠标释放
    def on_mouse_release(self, pos_x, pos_y, button, modifiers):
        if pos_y > 60:
            return
        # enable/disable tracks
        for track_idx in self.enabled_tracks:
            sw = self.enabled_tracks_switch[track_idx]
            if sw.collidepoint(pos_x, pos_y):
                self.enabled_tracks[track_idx] = not self.enabled_tracks[track_idx]

                idx = self.tracks_order_idx[track_idx]
                note_color = self.piano.TRACK_COLORS[idx % len(self.piano.TRACK_COLORS)]
                if self.enabled_tracks[track_idx]:
                    self.piano.fill_rect_with_gl(note_color, sw)
                else:
                    self.piano.fill_rect_with_gl(self.piano.color_lines, sw)

    # 鼠标按下
    def on_mouse_press(self, pos_x, pos_y, button, modifiers):
        if button == pyglet.window.mouse.RIGHT:
            self.is_pause = not self.is_pause

        elif button == pyglet.window.mouse.LEFT:
            if pos_y < 60: # progress bar can not click
                return
            clicked_staff_number = int((pos_y - self.staff_top) / (self.piano.staff_total_lines * self.piano.piano_staff_line_width))
            wraped_staff_offset = 0
            if clicked_staff_number > 0:
                wraped_staff_offset += self.piano.first_line_last_bar_pos
            if clicked_staff_number > 1:
                wraped_staff_offset += self.piano.second_line_last_bar_pos * (clicked_staff_number-1)

            timestamp_offset_x = (
                self.staff_offset_x +
                pos_x +
                wraped_staff_offset
            ) * self.piano.timestamp_range / self.piano.screen_width

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
            self.piano.draw_piano()


    # 鼠标移动事件，处理视角的变化
    # dx,dy表示鼠标从上一位置移动到当前位置x，y轴上的位移
    # 该函数将这个位移转换成了水平角x和俯仰角y的变化
    # 变化幅度由参数m控制
    def on_mouse_motion(self, x, y, dx, dy):
        pass


    def main_loop(self, dt):
        # must out of events loop
        # if self.menu_bar or self.menu_bar.choice:
        #     time.sleep(0.1)
        #     return

        # get cmd
        try:
            if (self.is_pause and not self.play_one_timestamp_while_paused) or self.midi_cmd_idx >= len(self.all_midi_lines):
                raise Exception("paused")
            midi_line = self.all_midi_lines[self.midi_cmd_idx]
            self.midi_cmd_idx += 1
            cmd, pitch, volecity_data, track_idx, pitch_timestamp = midi_line[:5]
            volecity = player.get_volecity(volecity_data)
            if pitch not in [0, 1] + player.g_grand_pitch_range:
                time.sleep(0.1)
                return
            if track_idx >= 0 and not self.enabled_tracks.get(track_idx, False):
                time.sleep(0.1)
                return
            if self.last_timestamp == -1:
                # init last timestamp
                self.last_timestamp = pitch_timestamp - 1
        except Exception, e:
            self.piano.show_notes_staff(self.enabled_tracks, self.tracks_order_idx, self.notes_in_all_staff, self.last_timestamp,
                                   self.staff_top,
                                   parse_midi.g_bar_duration,
                                   parse_midi.g_time_signature_n,
                                   self.staff_offset_x, self.is_pause)

            has_stoped = player.real_stop(self.sounds)
            if self.need_update_display:
                # pygame.display.update()
                self.need_update_display = False
            time.sleep(0.1)
            return

        # a chord
        if pitch_timestamp != self.last_timestamp:
            # print "bps:", utils.g_bps.get_bps_count()
            # utils.show_chord_keys_by_ascii(self.time_pitchs)
            is_beat_at_right_most, current_play_percent, progress_multi_lines, page_end_offset_x = self.piano.show_notes_staff(self.enabled_tracks, self.tracks_order_idx, self.notes_in_all_staff, self.last_timestamp,
                                   self.staff_top,
                                   parse_midi.g_bar_duration,
                                   parse_midi.g_time_signature_n,
                                   self.staff_offset_x, self.is_pause)

            # scroll page automatically
            if not self.is_pause and is_beat_at_right_most and (current_play_percent == 0 or current_play_percent > (100 - 50 / progress_multi_lines)):
                self.staff_offset_x = page_end_offset_x

            utils.sync_play_time(pitch_timestamp, self.last_timestamp, self.old_time, self.keys_recs, self.sounds)
            self.old_time = time.time()
            self.last_timestamp = pitch_timestamp
            self.time_pitchs = []
            self.keys_recs = []
            if self.is_pause and self.play_one_timestamp_while_paused:
                self.play_one_timestamp_while_paused = False
                time.sleep(0.1)
                return

        # playtrack
        if cmd == "NOTE_ON":
            player.play(self.devices, pitch, volecity, self.sounds)
            # build chord
            if pitch not in self.time_pitchs:
                self.time_pitchs += [pitch]

        elif cmd == "NOTE_OFF":
            player.stop(self.devices, pitch, volecity, self.sounds)

        elif cmd == "METRO_ON" and player.g_metronome_volume > 0:
            player.play(self.devices, pitch, volecity, self.sounds)

        # show keys
        if pitch > 1:
            self.keys_recs += self.piano.show_keys_press(cmd, pitch)
        #clock.tick(10)


    def on_draw(self):
        self.clear()
        # self.set_3d() # 进入3d模式
        # glColor3d(0, 1, 0)

        #self.set_2d()           # 进入2d模式
        self.batch.draw()       # 将batch中保存的顶点列表绘制出来
        self.draw_label()       # 绘制label
        #self.draw_reticle()


    # 窗口大小变化响应事件
    def on_resize(self, width, height):
        # label的纵坐标
        self.label.y = height - 10
        # #reticle更新，包含四个点，绘制成两条直线

        # if self.reticle:
        #     self.reticle.delete()
        # x, y = self.width / 2, self.height / 2
        # n = 10
        # self.reticle = pyglet.graphics.vertex_list(4,
        #     ('v2i', (x - n, y, x + n, y, x, y - n, x, y + n))
        # )


    # # 绘制游戏窗口中间的十字，一条横线加一条竖线
    # def draw_reticle(self):
    #     glColor3d(0, 0, 1)
    #     self.reticle.draw(GL_LINES)


    def draw_label(self):
        text = '%02d ' % (
            pyglet.clock.get_fps())
        self.label.text = text
        self.label.draw() # 绘制label的text


    def set_2d(self):
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()


    def set_3d(self):
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(65.0, width / float(height), 0.1, 60.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        x, y = (0, 0)           # self.rotation
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = (0, 0, 0)     # self.position
        glTranslatef(-x, -y, -z)


    ################################################################
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
        except Exception, e:
            print "midi error:", e
            if midi_filename in self.midi_filename_data:
                self.midi_filename_data.remove(midi_filename)
            return

        self.piano.timestamp_range = TIMESTAMP_RANGE * parse_midi.g_ticks_per_quarter / parse_midi.g_mseconds_per_quarter
        self.piano.timestamp_range = self.piano.timestamp_range * self.piano.piano_staff_line_width_base / self.piano.piano_staff_line_width

        if midi_filename in self.midi_filename_data:
            self.midi_filename_idx = self.midi_filename_data.index(midi_filename)
            self.midi_filename = midi_filename
        else:
            print "impossible: file not in menu list"
            return

        # draw track pick
        self.piano.fill_rect_with_gl(self.piano.color_backgroud,
                               Rect(0, self.menu_bar.top + self.menu_bar.lineheigth,
                                           self.piano.screen_width, 20))
        for track_idx, idx in self.tracks_order_idx.items():
            if track_idx in self.enabled_tracks_switch:
                sw = self.enabled_tracks_switch[track_idx]
                sw.left = idx * 30
            else:
                sw = Rect(idx * 30, self.menu_bar.top + self.menu_bar.lineheigth, 29, 20)
                self.enabled_tracks_switch[track_idx] = sw

            note_color = self.piano.TRACK_COLORS[idx % len(self.piano.TRACK_COLORS)]
            self.piano.fill_rect_with_gl(note_color, sw)

        # finish missing sounds
        player.load_sounds([(midi_data[1], midi_data[2]) for midi_data in self.all_midi_lines],
                           self.sounds)
        self.piano.draw_piano()

        self.time_pitchs = []
        self.keys_recs = []
        self.midi_cmd_idx = 0
        self.staff_offset_x = 0
        self.last_timestamp = 0
        self.is_pause = True
        self.play_one_timestamp_while_paused = False


    def main(self):
        """Play a midi file with sound samples
        """
        pass

        # while not p_done:
        #     # events
        #     for ev in pygame.event.get():
        #         need_update_display = True
        #         menu_bar_screen = self.menu_bar.update(ev)
        #         if self.menu_bar:
        #             self.menu_bar_info.set(self.get_menus_info_bar())
        #             self.menu_bar_info.update(ev)

        #         if self.menu_bar.choice:
        #             try:
        #                 self.load_resource(self.menu_bar.choice_label[-1])
        #             except Exception, e:
        #                 print "menu error:", e

        #             self.menu_bar_info.set(self.get_menus_info_bar())
        #             self.menu_bar_info.update(ev)
        #             # if have choice, continue event
        #             continue


if __name__ == '__main__':
    window = PlayCenter(width=WINSIZE[0], height=WINSIZE[1], caption='Piano Center', resizable=False) # 创建游戏窗口
    #window.set_exclusive_mouse(True) # 隐藏鼠标光标，将所有的鼠标事件都绑定到此窗口
    pyglet.app.run()
