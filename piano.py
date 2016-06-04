#encoding: utf8

"""A simple starfield example. Note you can move the 'center' of
the starfield by leftclicking in the window. This example show
the basics of creating a window, simple pixel plotting, and input
event management"""


import math
import pygame
from pygame.locals import *

__create_time__ = "Feb 26 2012"

TIMESTAMP_RANGE = 8000
PITCH_OF_KEY_ON_KEYBOARD = [K_TAB, K_1,
                            K_q, K_2,
                            K_w,
                            K_e, K_4,
                            K_r, K_5,
                            K_t, K_6,
                            K_y,
                            #
                            K_u, K_8,
                            K_i, K_9,
                            K_o,
                            K_p, K_MINUS,
                            K_LEFTBRACKET, K_EQUALS,
                            K_RIGHTBRACKET, K_BACKSPACE,
                            K_BACKSLASH, ]

class Piano():
    whitekey_width = 24
    whitekey_height = 140
    blackkey_height = 74
    blackkey_width = 14

    gap_keyboad_staff = 60


    def __init__(self, screen, screen_size, top=None):
        self.screen = screen
        self.screen_width, self.screen_height = screen_size

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
        self.pitch_color = {}

        self.staff_total_lines = 28
        self.staff_total_lines_up = 15
        # distance between lines
        self.staff_space_height = 4
        self.staff_space_height_base = 8

        # time range of window width
        self.timestamp_range = 8000

        if top is None:
            top = self.screen_height - self.whitekey_height

        self.top = top
        self.lastbar_pos_in_line1 = None
        self.lastbar_pos_in_line2 = None

        self.is_longbar_show = True

        self.dark_night_theme()
        # self.day_light_theme()

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
        self.color_black_key_down = 100, 100, 200
        self.color_white_key_down = 100, 100, 200
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

        self.color_lines = 180, 180, 180
        self.color_add_lines = 50, 50, 50
        self.color_middle_c_line = self.color_add_lines

        self.color_blackkey_edge = 90, 90, 90
        self.color_black_key_down = 100, 100, 200
        self.color_white_key_down = 100, 100, 200
        self.color_key_down = 0, 170, 200
        self.color_key_note = 140, 155, 100


    def add_piano_keys(self, key_type, key_pitch,
                       top=0, left=0, w=1, h=1):
        '''
        key_type left,3 keys    middle: 12 keys    right:1 white
        return width,height
        '''

        if key_type == 'm':
            piano_key_offset = [15,14, 14, 14,15,14,14,13,14,13, 14,14]
            whitekey_n = 7
            blackkey_offset = [15, 43, 86, 113, 140]
            key_pitch = 24 + 12 * key_pitch

        elif key_type == 'l':
            whitekey_n = 2
            blackkey_offset = [17]
            key_pitch = 21

        elif key_type == 'r':
            whitekey_n = 1
            blackkey_offset = []
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

        for offset in range(whitekey_n):
            pitch = whitekey_index2pitch[offset] + key_pitch
            self.whitekeys[pitch] = pygame.Rect(left + offset * (self.whitekey_width) * w, top,
                                                self.whitekey_width * w - w,
                                                self.whitekey_height * h)

        for offset,piano_offset in enumerate(blackkey_offset):
            pitch = blackkey_index2pitch[offset] + key_pitch
            self.blackkeys[pitch] = pygame.Rect(left + piano_offset * w, top,
                                                self.blackkey_width * w,
                                                self.blackkey_height * h)

        return (whitekey_n * self.whitekey_width * w,
                self.whitekey_height * h)


    def draw_dash_line(self, color, start_pos, end_pos, w=1, deta_h=7, vertical=True):
        if vertical:
            x, top = start_pos
            x, bottom = end_pos
            for dh in range(0,int((bottom - top)/deta_h),2):
                pygame.draw.line(self.screen, color, (x, top + dh * deta_h),
                                 (x, top + (dh+1) * deta_h), 1)
        else:
            top, y = start_pos
            bottom, y = end_pos
            for dh in range(0,int((bottom - top)/deta_h),2):
                pygame.draw.line(self.screen, color, (top + dh * deta_h, y),
                                 (top + (dh+1) * deta_h, y), 1)


    def draw_vertical_staff_lines(self, top=0, n=6, left=0):
        bottom = self.top

        middle_c_white_index = 23
        middle_c_white_offset_x = middle_c_white_index * self.whitekey_width + self.whitekey_width/2
        for i in range(1, int(n*2)-1):
            rx = left + middle_c_white_offset_x + i * 2*self.whitekey_width
            lx = left + middle_c_white_offset_x - i * 2*self.whitekey_width
            if i < n:
                pygame.draw.line(self.screen, self.color_lines, (lx, top), (lx, bottom))
                pygame.draw.line(self.screen, self.color_lines, (rx, top), (rx, bottom))
            else:
                self.draw_dash_line(self.color_add_lines, (lx, top), (lx, bottom))
                self.draw_dash_line(self.color_add_lines, (rx, top), (rx, bottom))

        x = left + middle_c_white_offset_x
        self.draw_dash_line(self.color_middle_c_line, (x, top), (x, bottom))


    def draw_note(self, key_note_idx, top=340):
        note = self.notes[key_note_idx-21]
        print note

        if key_note_idx in self.blackkeys:
            vertical_label = u"\ue262\ue0a2"
            key_note_idx = key_note_idx - 1
        elif key_note_idx in self.whitekeys:
            vertical_label = u"\ue0a2"

        key_rec = self.whitekeys[key_note_idx]
        note_pos = key_rec.left + self.whitekey_width/2
        note_pos -= 85

        self.piano_note_font = pygame.font.Font(pygame.font.match_font('Bravura Text'), 144)

        ren = self.piano_note_font.render(vertical_label, True, self.color_lines, self.color_backgroud)
        vertical_label_size = self.piano_note_font.size(vertical_label)
        #print vertical_label_size
        #note_rec = pygame.Rect(note_pos, 100, vertical_label_size[0], vertical_label_size[1])
        note_rec = pygame.Rect(note_pos, top, vertical_label_size[1], vertical_label_size[0])
        #pygame.draw.rect(ren, self.black, note_rec, True)

        ren = pygame.transform.rotate(ren, 270)
        self.screen.blit(ren, (note_pos, top))
        return note_rec, note_pos


    def draw_keys(self, keys_rec, color=None):
        dcolor = color
        bdcolor = color
        for r in keys_rec:
            if not color:
                if r.width > self.blackkey_width: # white
                    dcolor = self.white
                    bdcolor = self.white
                else:
                    dcolor = self.black
                    bdcolor = self.white

            self.screen.fill(dcolor, r)
            pygame.draw.rect(self.screen, bdcolor, r, 1)
            if bdcolor == self.black:
                pygame.draw.line(self.screen, self.color_blackkey_edge,
                                 (r.left + 2, r.top),
                                 (r.left + 2, r.top + r.height - 4), 1)
                pygame.draw.line(self.screen, self.color_blackkey_edge,
                                 (r.left + r.width - 2, r.top),
                                 (r.left + r.width - 2, r.top + r.height - 4), 1)

                pygame.draw.line(self.screen, self.color_blackkey_edge,
                                 (r.left + 2, r.top + r.height - 4),
                                 (r.left + r.width - 2, r.top + r.height - 4), 1)


    def reset_piano(self):
        self.pitch_color = {}
        self.draw_keys(self.whitekeys.values(), self.white)
        self.draw_keys(self.blackkeys.values(), self.black)
        # red line
        pygame.draw.line(self.screen, self.color_red_line,
                         (0, self.top - 3),
                         (self.screen_width, self.top - 3), 3)


    def init_piano(self, top=None, left=0):
        if top is None:
            top = self.top
        # self.screen.fill(self.color_backgroud)

        w, h = self.add_piano_keys('l', 0, top, left)
        left += w
        for i in range(7):
            w, h = self.add_piano_keys('m', i, top, left)
            left += w
        w, h = self.add_piano_keys('r', 0, top, left)

        self.reset_piano()


    def draw_staff_lines(self, middle=0, n=6, left=0):
        rightx = self.screen_width
        middle_c_white_offset_y = middle

        for i in range(1, int(n*2)-1):
            downy = left + middle_c_white_offset_y + i * self.staff_space_height
            topy = left + middle_c_white_offset_y - i * self.staff_space_height
            if i < n:
                pygame.draw.line(self.screen, self.color_lines, (left, topy), (rightx, topy))
                pygame.draw.line(self.screen, self.color_lines, (left, downy), (rightx, downy))
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
        pygame.draw.line(self.screen, self.color_backgroud,
                         (0, 0),
                         (self.screen_width, 0), 9)
        # bar
        pygame.draw.line(self.screen, self.white,
                         (offset_pos, 0),
                         (offset_pos + screen_width_pos, 0), 9)
        # point
        pygame.draw.line(self.screen, self.color_key_down,
                         (current_pos-1, 0),
                         (current_pos+1, 0), 9)

        if current_pos > offset_pos and current_pos <= offset_pos + screen_width_pos:
            return (current_pos - offset_pos) * 100 / screen_width_pos
        else:
            return 0


    def show_notes_staff(self, enabled_tracks, tracks_order_idx, notes_of_all_staff,
                         current_timestamp, staff_top, bar_duration, time_signature_n, offset_x, is_pause):
        # now start draw staff
        progress_offset_x = offset_x
        progress_multi_lines = 0
        is_beat_at_right_most = False
        while True:
            if (self.top - staff_top - self.gap_keyboad_staff) < (self.staff_total_lines * self.staff_space_height):
                self.screen.fill(self.color_backgroud, pygame.Rect(
                    0, staff_top,
                    self.screen_width, self.top - staff_top - self.gap_keyboad_staff))
                break
            middle = staff_top + self.staff_total_lines_up * self.staff_space_height
            (is_beat_at_right_most, last_bar_pos) = self._show_notes_staff(
                enabled_tracks, tracks_order_idx, notes_of_all_staff,
                current_timestamp, middle, bar_duration, time_signature_n, offset_x, is_pause)

            progress_multi_lines += 1
            if progress_multi_lines == 1:
                self.lastbar_pos_in_line1 = last_bar_pos
            elif progress_multi_lines == 2:
                self.lastbar_pos_in_line2 = last_bar_pos

            offset_x += last_bar_pos
            staff_top += self.staff_total_lines * self.staff_space_height

        # show_progress_bar
        max_timestamp = notes_of_all_staff[-1][1] + notes_of_all_staff[-1][2]
        percent_current_page  = self.show_progress_bar(max_timestamp, current_timestamp, progress_offset_x, offset_x - progress_offset_x)
        return is_beat_at_right_most, percent_current_page, progress_multi_lines, offset_x


    def _show_notes_staff(self, enabled_tracks, tracks_order_idx, notes_of_all_staff,
                          current_timestamp, middle, bar_duration, time_signature_n, offset_x, is_pause):
        self.screen.fill(self.color_backgroud, pygame.Rect(
            0, middle - self.staff_total_lines_up * self.staff_space_height,
            self.screen_width, self.staff_total_lines * self.staff_space_height))

        # draw_staff_lines
        self.draw_staff_lines(middle=middle)

        max_timestamp = notes_of_all_staff[-1][1] + notes_of_all_staff[-1][2]
        offset_bar = max_timestamp - (max_timestamp / bar_duration * bar_duration)

        # draw bars
        _bar_pos = offset_bar
        bar_pos = 0
        last_bar_pos = 0
        while True:
            last_bar_pos = bar_pos
            bar_pos = _bar_pos * self.screen_width / (self.timestamp_range) - offset_x
            pygame.draw.line(self.screen, self.color_lines,
                             (bar_pos, middle - 5 * self.staff_space_height),
                             (bar_pos, middle + 5 * self.staff_space_height))
            _bar_pos += bar_duration
            if bar_pos < 0:
                continue
            if bar_pos >= self.screen_width:
                break

        # draw last bar
        pygame.draw.line(self.screen, self.color_key_down,
                         (last_bar_pos-1, middle - 14 * self.staff_space_height),
                         (last_bar_pos-1, middle + 12 * self.staff_space_height), 2)


        # draw visual metronome
        interval = bar_duration / time_signature_n
        _beat_pos = (current_timestamp + bar_duration - offset_bar) / interval * interval - bar_duration + offset_bar
        beat_pos = _beat_pos * self.screen_width / (self.timestamp_range) - offset_x
        beat_length =  interval * self.screen_width / (self.timestamp_range)
        beat_top = middle - 10 * self.staff_space_height
        if beat_pos + beat_length > 0 and beat_pos < self.screen_width:
            beat_rec = pygame.Rect(beat_pos, beat_top, beat_length, self.staff_space_height*20)
            pygame.draw.rect(self.screen, self.color_key_down, beat_rec, 1)

        # draw notes
        for note_data in notes_of_all_staff:
            pitch, timestamp, duration, track_idx = note_data
            if not enabled_tracks.get(track_idx, False):
                continue

            note_tail_pos = (timestamp + duration) * self.screen_width / (self.timestamp_range) - offset_x
            if note_tail_pos < 0:
                continue
            note_pos = (timestamp) * self.screen_width / (self.timestamp_range) - offset_x

            # length/height
            if self.is_longbar_show:
                note_length =  duration * self.screen_width / (self.timestamp_range) - 1
                note_height = self.staff_space_height /2 + 1
            else:
                note_height = self.staff_space_height # /2 + 1
                note_length = note_height
                note_pos += self.staff_space_height * 1.618 # slight right

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
            key_index = (key_rec.left / self.whitekey_width) - 23
            note_center_y = middle - key_index * self.staff_space_height / 2
            note_top = note_center_y - note_height / 2
            note_rec = pygame.Rect(note_pos, note_top, note_length, note_height)

            # color
            note_color = self.TRACK_COLORS[0]
            if is_pause:
                note_color = self.TRACK_COLORS[tracks_order_idx[track_idx] % len(self.TRACK_COLORS)]

            if timestamp <= current_timestamp and timestamp + duration > current_timestamp:
                note_color = self.color_key_down
                self.screen.fill(note_color, note_rec)
            else:
                if is_black:
                    pygame.draw.rect(self.screen, note_color, note_rec, 1)
                else:
                    self.screen.fill(note_color, note_rec)

            # draw flag
            if key_index >= 0:
                note_tail_pos = note_pos
                if key_index >= 14:
                    note_tail = note_center_y + (1 + key_index - 7) * self.staff_space_height / 2
                elif key_index >= 6:
                    note_tail = note_center_y + 7 * self.staff_space_height / 2
                elif key_index < 6:
                    note_tail = note_center_y - 7 * self.staff_space_height / 2
                    note_tail_pos = note_pos + note_length - 1
            else:
                note_tail_pos = note_pos + note_length - 1
                if key_index >= -6:
                    note_tail = note_center_y + 7 * self.staff_space_height / 2
                    note_tail_pos = note_pos
                elif key_index > -14:
                    note_tail = note_center_y - 7 * self.staff_space_height / 2
                elif key_index <= -14:
                    note_tail = note_center_y - (1 - (key_index + 7)) * self.staff_space_height / 2

            pygame.draw.line(self.screen, note_color,
                             (note_tail_pos, note_center_y),
                             (note_tail_pos, note_tail))

        # return is beat_right_most
        beat_right_margin = self.screen_width - beat_pos
        if beat_right_margin >= 0 and beat_right_margin < beat_length:
            is_beat_at_right_most = True
        else:
            is_beat_at_right_most = False
        return is_beat_at_right_most, last_bar_pos


    def show_keys_press(self, cmd, pitch):
        pitch_left_blackkeys_rec = None
        pitch_right_blackkeys_rec = None
        if pitch in self.whitekeys.keys():
            pitch_key_rec = self.whitekeys[pitch]
            key_color = self.white
            if pitch + 1 in self.blackkeys.keys():
                pitch_right_blackkeys_rec = self.blackkeys[pitch+1]
            if pitch - 1 in self.blackkeys.keys():
                pitch_left_blackkeys_rec = self.blackkeys[pitch-1]

        elif pitch in self.blackkeys.keys():
            pitch_key_rec = self.blackkeys[pitch]
            key_color = self.black

        key_color_down = self.color_key_down
        if key_color != self.black:
            key_color_down = self.color_key_down

        if cmd == "NOTE_ON":
            key_color = key_color_down

        # store key color
        self.pitch_color[pitch] = key_color

        # note_rec, note_pos = self.draw_note(pitch, top=WINSIZE[1] * 0.7)
        # self.draw_vertical_staff_lines(WINSIZE[1] * 0.618)
        # pygame.draw.rect(self.screen, self.color_backgroud, note_rec, False)

        self.draw_keys([pitch_key_rec], key_color)
        if pitch_left_blackkeys_rec:
            self.draw_keys([pitch_left_blackkeys_rec], self.pitch_color.get(pitch-1, self.black))

        if pitch_right_blackkeys_rec:
            self.draw_keys([pitch_right_blackkeys_rec], self.pitch_color.get(pitch+1, self.black))


if __name__ == '__main__':
    pygame.init()
    WINSIZE = [1270, 700]
    screen = pygame.display.set_mode(WINSIZE)
    pygame.display.set_caption('Piano Keyboard')

    piano = Piano(screen, WINSIZE)
    piano.init_piano()

    clock = pygame.time.Clock()
    done = 0
    while not done:
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
                done = 1
                break
            elif e.type == MOUSEBUTTONDOWN and e.button == 1:
                pass
        clock.tick(30)
