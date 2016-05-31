#encoding: utf8

"""A simple starfield example. Note you can move the 'center' of
the starfield by leftclicking in the window. This example show
the basics of creating a window, simple pixel plotting, and input
event management"""


import math
import pyglet
from pyglet.gl import *
from pyglet.window import key


__create_time__ = "Feb 26 2012"

TIMESTAMP_RANGE = 8000

PITCH_OF_KEY_ON_KEYBOARD = [key.TAB, key._1,
                            key.Q, key._2,
                            key.W,
                            key.E, key._4,
                            key.R, key._5,
                            key.T, key._6,
                            key.Y,
                            #
                            key.U, key._8,
                            key.I, key._9,
                            key.O,
                            key.P, key.MINUS,
                            key.BRACKETLEFT, key.EQUAL,
                            key.BRACKETRIGHT, key.BACKSPACE,
                            key.BACKSLASH, ]


class Rect():
    def __init__(self, left, top, width, height):
        self.left = left
        self.top = top
        self.width = width
        self.height = height

    def collidepoint(self, pos_x, pos_y):
        if pos_x < self.left:
            return False
        if pos_x > self.left + self.width:
            return False
        if pos_y < self.top:
            return False
        if pos_y > self.top + self.height:
            return False

        return True


class Piano():
    piano_white_key_height = 140
    piano_white_key_width = 24
    piano_white_key_height = 140
    piano_black_key_height = 74
    piano_black_key_width = 14

    gap_keyboad_staff = 60


    def __init__(self, batch, screen_rect, top=None):
        #self.dark_night_theme()
        self.day_light_theme()

        self.batch = batch

        # self.group_bg = pyglet.graphics.OrderedGroup(0)
        # self.group_fg = pyglet.graphics.OrderedGroup(1)
        # self.group_top = pyglet.graphics.OrderedGroup(2)

        # self.group_staff_bg = pyglet.graphics.OrderedGroup(3)
        # self.group_staff = pyglet.graphics.OrderedGroup(4)
        # self.group_note = pyglet.graphics.OrderedGroup(5)
        # self.group_box = pyglet.graphics.OrderedGroup(6)

        # self.group_now = self.group_bg

        self.white_key_image = pyglet.image.create(self.piano_white_key_width - 1,
                                                   self.piano_white_key_height,
                                                   pyglet.image.SolidColorImagePattern(self.white + (255,)))
        self.white_key_press_image = pyglet.image.create(self.piano_white_key_width - 1,
                                                         self.piano_white_key_height,
                                                         pyglet.image.SolidColorImagePattern(
                                                             self.color_white_key_down + (255,)))

        self.black_key_image = pyglet.image.create(self.piano_black_key_width,
                                                   self.piano_black_key_height,
                                                   pyglet.image.SolidColorImagePattern(self.black + (255,)))
        self.black_key_press_image = pyglet.image.create(self.piano_black_key_width,
                                                         self.piano_black_key_height,
                                                         pyglet.image.SolidColorImagePattern(
                                                             self.color_black_key_down + (255,)))

        self.screen_width, self.screen_height = screen_rect

        self.notes = """A2 #A2 B2
    C1 #C1 D1 #D1 E1 F1 #F1 G1 #G1 A1 #A1 B1
    C #C D #D E F #F G #G A #A B
    c #c d #d e f #f g #g a #a b
    c1 #c1 d1 #d1 e1 f1 #f1 g1 #g1 a1 #a1 b1
    c2 #c2 d2 #d2 e2 f2 #f2 g2 #g2 a2 #a2 b2
    c3 #c3 d3 #d3 e3 f3 #f3 g3 #g3 a3 #a3 b3
    c4 #c4 d4 #d4 e4 f4 #f4 g4 #g4 a4 #a4 b4
    c5""".replace("\n", " ").split()

        self.whitekeys = {}
        self.blackkeys = {}

        self.staff_total_lines = 28
        self.staff_total_lines_up = 15
        # distance between lines
        self.piano_staff_line_width = 4
        self.piano_staff_line_width_base = 8

        # time range of window width
        self.timestamp_range = 8000

        if top is None:
            top = self.screen_height - self.piano_white_key_height

        self.top = top
        self.first_line_last_bar_pos = None
        self.second_line_last_bar_pos = None

        self.is_show_longbar_in_staff = True


    def day_light_theme(self):
        self.TRACK_COLORS = [(20, 10, 10),
                             (130,130,130),
	                     (128,128,0),
	                     (128,0,128),
	                     (128,0,0),
	                     (0,128,0),
	                     (0,0,128),
	                     (200,200,0),
	                     (0,200,0),
	                     (200,0,200),
	                     (200,0,0),
	                     (0,0,200),        ]

        self.white = 250, 230, 200
        self.black = 0, 0, 0

        self.color_backgroud = 250, 250, 250

        self.color_red_line = 130, 0, 0

        self.color_lines = 50, 50, 50
        self.color_add_lines = 220, 220, 220
        self.color_middle_c_line = self.color_add_lines

        self.color_blackkey_edge = 90, 90, 90
        self.color_black_key_down = 0, 170, 200
        self.color_white_key_down = 0, 170, 200
        self.color_key_down = 0, 170, 200
        self.color_key_note = 140, 155, 100


    def dark_night_theme(self):
        self.TRACK_COLORS = [(250, 230, 200),
                             (240,240,240),
	                     (200,200,0),
	                     (0,200,0),
	                     (200,0,200),
	                     (200,0,0),
	                     (0,0,200),
	                     (128,128,0),
	                     (128,0,128),
	                     (128,0,0),
	                     (0,128,0),
	                     (0,0,128),]

        self.white = 250, 230, 200
        self.black = 0, 0, 0
        self.color_backgroud = self.black

        self.color_red_line = 130, 0, 0
        self.color_blackkey_edge = 90, 90, 90
        self.color_lines = 180, 180, 180
        self.color_add_lines = 100, 100, 100
        self.color_middle_c_line = self.color_add_lines

        self.color_black_key_down = 100, 100, 200
        self.color_white_key_down = 100, 100, 200
        self.color_key_down = 0, 170, 200
        self.color_key_note = 140, 155, 100


    def add_piano_keys(self, key_type, key_pitch,
                       top=0, left=0):
        '''
        key_type left,3 keys    middle: 12 keys    right:1 white
        return width,height
        '''

        if key_type == 'm':
            piano_key_offset = [15,14, 14, 14,15,14,14,13,14,13, 14,14]
            piano_white_key_n = 7
            piano_black_key_offset = [15, 43, 86, 113, 140]
            key_pitch = 24 + 12 * key_pitch

        elif key_type == 'l':
            piano_white_key_n = 2
            piano_black_key_offset = [17]
            key_pitch = 21

        elif key_type == 'r':
            piano_white_key_n = 1
            piano_black_key_offset = []
            key_pitch = 108

        '''
              15          43                86           113        140
        15     14    14    14    15    14    14    13    14    13    14    14
        +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
        |     |     |     |     |     |     |     |     |     |     |     |     |
        |     |     |     |     |     |     |     |     |     |     |     |     |
        |     |     |     |     |     |     |     |     |     |     |     |     |
        |     |     |     |     |     |     |     |     |     |     |     |     |
        |     +---+-+     +-+---+     |     +---+-+     +--+--+     +-+---+     |
        |         |         |         |         |          |          |         |
        |         |         |         |         |          |          |         |
        |         |         |         |         |          |          |         |
        |         |         |         |         |          |          |         |
        +---------+---------+---------+---------+----------+----------+---------+
          24        24        24        24         24         24        24
        '''

        whitekey_index2pitch = [0, 2, 4, 5, 7, 9, 11]
        blackkey_index2pitch = [1, 3, 6, 8, 10]
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

        for offset in range(piano_white_key_n):
            pitch = whitekey_index2pitch[offset] + key_pitch
            self.whitekeys[pitch] = Rect(left + offset * (self.piano_white_key_width), top,
                                         self.piano_white_key_width - 1,
                                         self.piano_white_key_height)
            # self.whitekeys[pitch] = pyglet.sprite.Sprite(
            #     self.white_key_image, x=left + offset * (self.piano_white_key_width),
            #     y=self.screen_height - top - self.piano_white_key_height,
            #     batch=self.batch, group=self.group_bg)

        for offset,piano_offset in enumerate(piano_black_key_offset):
            pitch = blackkey_index2pitch[offset] + key_pitch
            self.blackkeys[pitch] = Rect(left + piano_offset, top,
                                         self.piano_black_key_width,
                                         self.piano_black_key_height)
            # self.blackkeys[pitch] = pyglet.sprite.Sprite(
            #     self.black_key_image, x=left + piano_offset,
            #     y=self.screen_height - top - self.piano_black_key_height,
            #     batch=self.batch, group=self.group_fg)

        return (piano_white_key_n * self.piano_white_key_width,
                self.piano_white_key_height)


    def draw_dash_line(self, color, start_pos, end_pos, w=1, deta_h=7, vertical=True):
        if vertical:
            x, top = start_pos
            x, bottom = end_pos
            for dh in range(0,int((bottom - top)/deta_h),2):
                self.draw_line_with_gl(color, (x, top + dh * deta_h),
                                 (x, top + (dh+1) * deta_h), 1)
        else:
            top, y = start_pos
            bottom, y = end_pos
            for dh in range(0,int((bottom - top)/deta_h),2):
                self.draw_line_with_gl(color, (top + dh * deta_h, y),
                                 (top + (dh+1) * deta_h, y), 1)


    def draw_vertical_staff_lines(self, top=0, n=6, left=0):
        bottom = self.top

        middle_c_white_index = 23
        middle_c_white_offset_x = middle_c_white_index * self.piano_white_key_width + self.piano_white_key_width/2
        for i in range(1, int(n*2)-1):
            rx = left + middle_c_white_offset_x + i * 2*self.piano_white_key_width
            lx = left + middle_c_white_offset_x - i * 2*self.piano_white_key_width
            if i < n:
                self.draw_line_with_gl(self.color_lines, (lx, top), (lx, bottom))
                self.draw_line_with_gl(self.color_lines, (rx, top), (rx, bottom))
            else:
                self.draw_dash_line(self.color_add_lines, (lx, top), (lx, bottom))
                self.draw_dash_line(self.color_add_lines, (rx, top), (rx, bottom))

        x = left + middle_c_white_offset_x
        self.draw_dash_line(self.color_middle_c_line, (x, top), (x, bottom))


    # def draw_note(self, key_note_idx, top=340):
    #     note = self.notes[key_note_idx-21]
    #     print note

    #     if key_note_idx in self.blackkeys:
    #         vertical_label = u"\ue262\ue0a2"
    #         key_note_idx = key_note_idx - 1
    #     elif key_note_idx in self.whitekeys:
    #         vertical_label = u"\ue0a2"

    #     key_rec = self.whitekeys[key_note_idx]
    #     note_pos = key_rec.left + self.piano_white_key_width/2
    #     note_pos -= 85

    #     self.piano_note_font = pygame.font.Font(pygame.font.match_font('Bravura Text'), 144)

    #     ren = self.piano_note_font.render(vertical_label, True, self.color_lines, self.color_backgroud)
    #     vertical_label_size = self.piano_note_font.size(vertical_label)
    #     #print vertical_label_size
    #     #note_rec = Rect(note_pos, 100, vertical_label_size[0], vertical_label_size[1])
    #     note_rec = Rect(note_pos, top, vertical_label_size[1], vertical_label_size[0])
    #     #pygame.draw.rect(ren, self.black, note_rec, True)

    #     ren = pygame.transform.rotate(ren, 270)
    #     self.screen.blit(ren, (note_pos, top))
    #     return note_rec, note_pos


    def draw_keys(self, keys_rec, color=None):
        dcolor = color
        bdcolor = color
        for r in keys_rec:
            if not color:
                if r.width > self.piano_black_key_width: # white
                    dcolor = self.white
                    bdcolor = self.white
                else:
                    dcolor = self.black
                    bdcolor = self.white

            self.fill_rect_with_gl(dcolor, r)
            self.draw_rect_with_gl(bdcolor, r, 1)
            if bdcolor == self.black:
                self.draw_line_with_gl(self.color_blackkey_edge,
                                 (r.left + 2, r.top),
                                 (r.left + 2, r.top + r.height - 4), 1)
                self.draw_line_with_gl(self.color_blackkey_edge,
                                 (r.left + r.width - 2, r.top),
                                 (r.left + r.width - 2, r.top + r.height - 4), 1)

                self.draw_line_with_gl(self.color_blackkey_edge,
                                 (r.left + 2, r.top + r.height - 4),
                                 (r.left + r.width - 2, r.top + r.height - 4), 1)


    def reset_piano(self):
        for sp in self.whitekeys.values():
            sp.image = self.white_key_image
        for sp in self.blackkeys.values():
            sp.image = self.black_key_image


    def init_piano(self, top=None, left=0):
        if top is None:
            top = self.top

        # self.fill_rect_with_gl(self.color_backgroud)

        w, h = self.add_piano_keys('l', 0, top, left)
        left += w
        for i in range(7):
            w, h = self.add_piano_keys('m', i, top, left)
            left += w
        w, h = self.add_piano_keys('r', 0, top, left)

        # red line
        self.draw_line_with_gl(self.color_red_line,
                               (0, self.top - 4),
                               (self.screen_width, self.top - 4), 4)


    def draw_staff_lines(self, middle=0, n=6, left=0):
        rightx = self.screen_width
        middle_c_white_offset_y = middle

        for i in range(1, int(n*2)-1):
            downy = left + middle_c_white_offset_y + i * self.piano_staff_line_width
            topy = left + middle_c_white_offset_y - i * self.piano_staff_line_width
            if i < n:
                self.draw_line_with_gl(self.color_lines, (left, topy), (rightx, topy))
                self.draw_line_with_gl(self.color_lines, (left, downy), (rightx, downy))
            else:
                self.draw_dash_line(self.color_add_lines, (left, topy), (rightx, topy), deta_h=15, vertical=False)
                self.draw_dash_line(self.color_add_lines, (left, downy), (rightx, downy), deta_h=15, vertical=False)

        y = left + middle_c_white_offset_y
        self.draw_dash_line(self.color_middle_c_line, (left, y), (rightx, y), deta_h=15, vertical=False)


    def show_progress_bar(self, max_timestamp, current_timestamp, offset_x, screen_staff_total_length):
        max_pos = (max_timestamp) * self.screen_width / (self.timestamp_range)

        current_pos = (current_timestamp) * self.screen_width / (self.timestamp_range) * self.screen_width / max_pos
        offset_pos = offset_x * self.screen_width / max_pos
        screen_width_pos = screen_staff_total_length * self.screen_width / max_pos

        # backgroud
        self.draw_line_with_gl(self.color_backgroud,
                               (0, 0),
                               (self.screen_width, 0), 8)

        # vision
        vl = self.draw_line_with_gl(self.white,
                                    (offset_pos, 0),
                                    (offset_pos + screen_width_pos, 0), 8)

        # cursor
        vl = self.draw_line_with_gl(self.color_key_down,
                                    (current_pos-1, 0),
                                    (current_pos+1, 0), 8)

        if current_pos > offset_pos and current_pos <= offset_pos + screen_width_pos:
            return (current_pos - offset_pos) * 100 / screen_width_pos
        else:
            return 0


    def show_notes_staff(self, p_enabled_tracks, p_tracks_order_idx, p_notes_in_all_staff,
                         current_timestamp, p_staff_top, bar_duration, time_signature_n, offset_x, is_pause):

        # now start draw staff
        progress_offset_x = offset_x
        progress_multi_lines = 0
        is_beat_at_right_most = False
        while True:
            if self.top - p_staff_top - self.gap_keyboad_staff < self.staff_total_lines * self.piano_staff_line_width:
                # self.group_now = self.group_staff_bg
                self.fill_rect_with_gl(self.color_backgroud, Rect(
                    0, p_staff_top,
                    self.screen_width, self.top - p_staff_top - self.gap_keyboad_staff))
                break
            middle = p_staff_top + self.staff_total_lines_up * self.piano_staff_line_width
            is_beat_at_right_most, last_bar_pos = self._show_notes_staff(p_enabled_tracks, p_tracks_order_idx, p_notes_in_all_staff,
                                                           current_timestamp, middle, bar_duration, time_signature_n, offset_x, is_pause)
            progress_multi_lines += 1
            if progress_multi_lines == 1:
                self.first_line_last_bar_pos = last_bar_pos
            elif progress_multi_lines == 2:
                self.second_line_last_bar_pos = last_bar_pos

            offset_x += last_bar_pos
            p_staff_top += self.staff_total_lines * self.piano_staff_line_width


        # show_progress_bar
        max_timestamp = p_notes_in_all_staff[-1][1] + p_notes_in_all_staff[-1][2]
        percent_current_page  = self.show_progress_bar(max_timestamp, current_timestamp, progress_offset_x, offset_x - progress_offset_x)
        return is_beat_at_right_most, percent_current_page, progress_multi_lines, offset_x


    def _show_notes_staff(self, p_enabled_tracks, p_tracks_order_idx, p_notes_in_all_staff,
                          current_timestamp, middle, bar_duration, time_signature_n, offset_x, is_pause):

        # set group
        # self.group_now = self.group_staff_bg
        self.fill_rect_with_gl(self.color_backgroud, Rect(
            0, middle - self.staff_total_lines_up * self.piano_staff_line_width,
            self.screen_width, self.staff_total_lines * self.piano_staff_line_width))

        # set group
        # self.group_now = self.group_staff
        # draw_staff_lines
        self.draw_staff_lines(middle=middle)

        max_timestamp = p_notes_in_all_staff[-1][1] + p_notes_in_all_staff[-1][2]
        offset_bar = max_timestamp - (max_timestamp / bar_duration * bar_duration)

        # set group
        # self.group_now = self.group_staff
        # draw bars
        _bar_pos = offset_bar
        bar_pos = 0
        last_bar_pos = 0
        while True:
            last_bar_pos = bar_pos
            bar_pos = _bar_pos * self.screen_width / (self.timestamp_range) - offset_x
            self.draw_line_with_gl(self.color_lines,
                             (bar_pos, middle - 5 * self.piano_staff_line_width),
                             (bar_pos, middle + 5 * self.piano_staff_line_width))
            _bar_pos += bar_duration
            if bar_pos < 0:
                continue
            if bar_pos >= self.screen_width:
                break

        # set group
        # self.group_now = self.group_note
        # draw last bar
        self.draw_line_with_gl(self.color_key_down,
                         (last_bar_pos-1, middle - 14 * self.piano_staff_line_width),
                         (last_bar_pos-1, middle + 12 * self.piano_staff_line_width), 2)

        # set group
        # self.group_now = self.group_note
        # draw visual metronome
        interval = bar_duration / time_signature_n
        _beat_pos = (current_timestamp + bar_duration - offset_bar) / interval * interval - bar_duration + offset_bar
        beat_pos = _beat_pos * self.screen_width / (self.timestamp_range) - offset_x
        beat_length =  interval * self.screen_width / (self.timestamp_range)
        beat_top = middle - 10 * self.piano_staff_line_width
        if beat_pos + beat_length > 0 and beat_pos < self.screen_width:
            beat_rec = Rect(beat_pos, beat_top, beat_length, self.piano_staff_line_width*20)
            self.draw_rect_with_gl(self.color_key_down, beat_rec, 1)

        # set group
        # self.group_now = self.group_note
        # draw notes
        for note_data in p_notes_in_all_staff:
            pitch, timestamp, duration, track_idx = note_data
            if not p_enabled_tracks.get(track_idx, False):
                continue

            note_tail_pos = (timestamp + duration) * self.screen_width / (self.timestamp_range) - offset_x
            if note_tail_pos < 0:
                continue
            note_pos = (timestamp) * self.screen_width / (self.timestamp_range) - offset_x

            # length/height
            if self.is_show_longbar_in_staff:
                note_length =  duration * self.screen_width / (self.timestamp_range) - 1
                note_height = self.piano_staff_line_width /2 + 1
            else:
                note_height = self.piano_staff_line_width # /2 + 1
                note_length = note_height
                note_pos += self.piano_staff_line_width * 1.618 # slight right

            if note_pos > self.screen_width:
                break
            if note_pos < 0:
                note_length = note_length + note_pos
                note_pos = 0

            # top
            is_black = False
            if pitch in self.blackkeys:
                is_black = True
                pitch = pitch - 1
            key_rec = self.whitekeys[pitch]
            key_index = (key_rec.left / self.piano_white_key_width) - 23
            note_center_y = middle - key_index * self.piano_staff_line_width / 2
            note_top = note_center_y - note_height / 2
            note_rec = Rect(note_pos, note_top, note_length, note_height)

            # color
            note_color = self.TRACK_COLORS[0]
            if is_pause:
                note_color = self.TRACK_COLORS[p_tracks_order_idx[track_idx] % len(self.TRACK_COLORS)]

            if timestamp <= current_timestamp and timestamp + duration > current_timestamp:
                note_color = self.color_key_down
                self.fill_rect_with_gl(note_color, note_rec)
            else:
                if is_black:
                    self.draw_rect_with_gl(note_color, note_rec, 1)
                else:
                    self.fill_rect_with_gl(note_color, note_rec)

            # draw flag
            if key_index >= 0:
                note_tail_pos = note_pos
                if key_index >= 14:
                    note_tail = note_center_y + (1 + key_index - 7) * self.piano_staff_line_width / 2
                elif key_index >= 6:
                    note_tail = note_center_y + 7 * self.piano_staff_line_width / 2
                elif key_index < 6:
                    note_tail = note_center_y - 7 * self.piano_staff_line_width / 2
                    note_tail_pos = note_pos + note_length - 1
            else:
                note_tail_pos = note_pos + note_length - 1
                if key_index >= -6:
                    note_tail = note_center_y + 7 * self.piano_staff_line_width / 2
                    note_tail_pos = note_pos
                elif key_index > -14:
                    note_tail = note_center_y - 7 * self.piano_staff_line_width / 2
                elif key_index <= -14:
                    note_tail = note_center_y - (1 - (key_index + 7)) * self.piano_staff_line_width / 2

            self.draw_line_with_gl(note_color,
                             (note_tail_pos, note_center_y),
                             (note_tail_pos, note_tail))


        # retrun is beat_right_most
        beat_right_margin = self.screen_width - beat_pos
        if beat_right_margin >= 0 and beat_right_margin < beat_length:
            is_beat_at_right_most = True
        else:
            is_beat_at_right_most = False
        return is_beat_at_right_most, last_bar_pos


    def show_keys_press(self, cmd, pitch):
        pitch_side_blackkeys_rec = []
        if pitch in self.whitekeys.keys():
            pitch_key_rec = [self.whitekeys[pitch]]
            key_color = self.white
            if pitch + 1 in self.blackkeys.keys():
                pitch_side_blackkeys_rec += [self.blackkeys[pitch+1]]
            if pitch - 1 in self.blackkeys.keys():
                pitch_side_blackkeys_rec += [self.blackkeys[pitch-1]]

        elif pitch in self.blackkeys.keys():
            pitch_key_rec = [self.blackkeys[pitch]]
            key_color = self.black

        key_color_down = self.color_key_down
        if key_color != self.black:
            key_color_down = self.color_key_down

        if cmd == "NOTE_ON":
            key_color = key_color_down

        # note_rec, note_pos = self.draw_note(pitch, top=WINSIZE[1] * 0.7)
        # self.draw_vertical_staff_lines(WINSIZE[1] * 0.618)

        # set group
        # self.group_now = self.group_staff

        # self.draw_rect_with_gl(self.color_backgroud, note_rec, 1)
        self.draw_keys(pitch_key_rec, key_color)
        self.draw_keys(pitch_side_blackkeys_rec, self.black)
        return pitch_key_rec + pitch_side_blackkeys_rec


    def show_keys_press_sp(self, cmd, pitch):
        if pitch in self.whitekeys.keys():
            sp = self.whitekeys[pitch]
            if cmd == "NOTE_ON":
                sp.image = self.white_key_press_image
            else:
                sp.image = self.white_key_image
        elif pitch in self.blackkeys.keys():
            sp = self.blackkeys[pitch]
            if cmd == "NOTE_ON":
                sp.image = self.black_key_press_image
            else:
                sp.image = self.black_key_image
        return


    def fill_rect_with_gl(self, color, rect):
        vertex_data = (rect.left, self.screen_height - rect.top,
                       rect.left + rect.width, self.screen_height - rect.top,
                       rect.left + rect.width, self.screen_height - (rect.top + rect.height),
                       rect.left, self.screen_height - (rect.top + rect.height),)

        color = color + (255,)
        vl = pyglet.graphics.vertex_list(4, ('v2f', vertex_data),
                                         ('c4B', color * 4))
        vl.draw(GL_QUADS)


    def draw_rect_with_gl(self, color, rect, width=1):
        start_pos = (rect.left, rect.top,)
        end_pos = (rect.left + rect.width, rect.top,)
        self.draw_line_with_gl(color, start_pos, end_pos, line_width=width)

        start_pos = (rect.left, (rect.top + rect.height))
        end_pos = (rect.left + rect.width, (rect.top + rect.height))
        self.draw_line_with_gl(color, start_pos, end_pos, line_width=width)

        start_pos = (rect.left, rect.top,)
        end_pos = (rect.left, (rect.top + rect.height))
        self.draw_line_with_gl(color, start_pos, end_pos, line_width=width)

        start_pos = (rect.left + rect.width, rect.top,)
        end_pos = (rect.left + rect.width, (rect.top + rect.height))
        self.draw_line_with_gl(color, start_pos, end_pos, line_width=width)

        return None


    def draw_line_with_gl(self, color, start_pos, end_pos, line_width=1):
        start_pos = (start_pos[0], self.screen_height - start_pos[1])
        end_pos = (end_pos[0], self.screen_height - end_pos[1])
        color = color + (255,)

        if line_width > 1:
            if start_pos[0] == end_pos[0]:
                start_pos_add = (start_pos[0] + line_width, start_pos[1])
                end_pos_add = (end_pos[0] + line_width, end_pos[1])
            elif start_pos[1] == end_pos[1]:
                start_pos_add = (start_pos[0], start_pos[1] - line_width)
                end_pos_add = (end_pos[0], end_pos[1] - line_width)
            vertex_data = start_pos + end_pos + end_pos_add + start_pos_add

            vl = pyglet.graphics.vertex_list(4, ('v2f', vertex_data),
                                             ('c4B', color * 4))
            vl.draw(GL_QUADS)

        else:
            vertex_data = start_pos + end_pos
            vl = pyglet.graphics.vertex_list(2, ('v2f', vertex_data),
                                             ('c4B', color * 2))
            vl.draw(GL_LINES)



if __name__ == '__main__':
    pass
