#encoding: utf8

"""A simple starfield example. Note you can move the 'center' of
the starfield by leftclicking in the window. This example show
the basics of creating a window, simple pixel plotting, and input
event management"""


import math
import pygame
from pygame.locals import *

__create_time__ = "Feb 26 2012"


class Piano():
    def __init__(self, screen, screen_rect):
        self.screen = screen
        self.screen_rect = screen_rect
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

        self.piano_staff_width = 16
        self.timestamp_range = 5000

        self.color_red_line = 130, 0, 0
        self.color_blackkey_edge = 90, 90, 90
        self.color_lines = 180, 180, 180
        self.color_add_lines = 100, 100, 100
        self.color_middle_c_line = self.color_add_lines

        self.white = 250, 230, 200
        self.black = 0, 0, 0

        self.color_backgroud = self.black
        self.color_black_key_down = 100, 100, 200
        self.color_white_key_down = 100, 100, 200
        self.color_key_down = 0, 170, 200
        self.color_key_note = 140, 155, 100

        self.piano_white_key_width = 24
        self.piano_white_key_height = 140
        self.piano_black_key_height = 74
        self.piano_black_key_width = 14


    def add_piano_keys(self, key_type, key_pitch,
                       top=0, left=0, w=1, h=1):
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
            self.whitekeys[pitch] = pygame.Rect(left + offset * (self.piano_white_key_width) * w, top,
                                                self.piano_white_key_width * w - w,
                                                self.piano_white_key_height * h)

        for offset,piano_offset in enumerate(piano_black_key_offset):
            pitch = blackkey_index2pitch[offset] + key_pitch
            self.blackkeys[pitch] = pygame.Rect(left + piano_offset * w, top,
                                                self.piano_black_key_width * w,
                                                self.piano_black_key_height * h)

        return (piano_white_key_n * self.piano_white_key_width * w,
                self.piano_white_key_height * h)


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


    def draw_lines(self, top=0, n=6, left=0):
        bottom = self.top

        middle_c_white_index = 23
        middle_c_white_offset_x = middle_c_white_index * self.piano_white_key_width + self.piano_white_key_width/2
        for i in range(1, int(n*2)-1):
            rx = left + middle_c_white_offset_x + i * 2*self.piano_white_key_width
            lx = left + middle_c_white_offset_x - i * 2*self.piano_white_key_width
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
        note_pos = key_rec.left + self.piano_white_key_width/2
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
                if r.width > self.piano_black_key_width: # white
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


    def draw_piano(self, top=None, left=0):
        if top is None:
            top = self.screen_rect[1] - self.piano_white_key_height

        self.top = top
        # self.screen.fill(self.color_backgroud)

        w, h = self.add_piano_keys('l', 0, top, left)
        left += w
        for i in range(7):
            w, h = self.add_piano_keys('m', i, top, left)
            left += w
        w, h = self.add_piano_keys('r', 0, top, left)

        self.draw_keys(self.whitekeys.values() )
        self.draw_keys(self.blackkeys.values(), self.black)
        # red line
        pygame.draw.line(self.screen, self.color_red_line,
                         (0, self.top - 3),
                         (self.screen_rect[0], self.top - 3), 4)

        pygame.display.update()


    def draw_staff_lines(self, top=0, n=6, left=0):
        rightx = self.screen_rect[0]
        middle_c_white_offset_y = top

        for i in range(1, int(n*2)-1):
            downy = left + middle_c_white_offset_y + i * self.piano_staff_width
            topy = left + middle_c_white_offset_y - i * self.piano_staff_width
            if i < n:
                pygame.draw.line(self.screen, self.color_lines, (left, topy), (rightx, topy))
                pygame.draw.line(self.screen, self.color_lines, (left, downy), (rightx, downy))
            else:
                self.draw_dash_line(self.color_add_lines, (left, topy), (rightx, topy), vertical=False)
                self.draw_dash_line(self.color_add_lines, (left, downy), (rightx, downy), vertical=False)

        y = left + middle_c_white_offset_y
        self.draw_dash_line(self.color_middle_c_line, (left, y), (rightx, y), vertical=False)


    def show_progress_bar(self, max_timestamp, current_timestamp, offset_x):
        max_pos = (max_timestamp) * self.screen_rect[0] / (self.timestamp_range*2)

        current_pos = (current_timestamp) * self.screen_rect[0] / (self.timestamp_range*2) * self.screen_rect[0] / max_pos
        offset_pos = offset_x * self.screen_rect[0] / max_pos
        screen_width_pos = self.screen_rect[0] * self.screen_rect[0] / max_pos

        pygame.draw.line(self.screen, self.color_backgroud,
                         (0, 0),
                         (self.screen_rect[0], 0), 4)

        pygame.draw.line(self.screen, self.color_red_line,
                         (offset_pos, 0),
                         (offset_pos + screen_width_pos, 0), 4)

        pygame.draw.line(self.screen, self.color_key_down,
                         (current_pos-1, 0),
                         (current_pos+1, 0), 4)


    def show_notes_staff(self, p_notes_in_all_staff, current_timestamp, top=0, offset_x=0):
        self.screen.fill(self.color_backgroud, pygame.Rect(
            0, top - 15 * self.piano_staff_width,
            self.screen_rect[0], 30 * self.piano_staff_width))

        self.draw_staff_lines(top=top)
        max_timestamp = p_notes_in_all_staff[-1][1]
        self.show_progress_bar(max_timestamp, current_timestamp, offset_x)

        first_one = False
        for note_data in p_notes_in_all_staff:
            pitch, timestamp, duration = note_data

            note_pos = (timestamp) * self.screen_rect[0] / (self.timestamp_range*2) - offset_x
            if note_pos < 0:
                continue
            if note_pos > self.screen_rect[0]:
                break

            is_black = False
            if pitch in self.blackkeys:
                is_black = True
                pitch = pitch - 1

            key_rec = self.whitekeys[pitch]
            note_top = top - ((key_rec.left / self.piano_white_key_width) - 22.5) * self.piano_staff_width / 2
            note_length =  duration * self.screen_rect[0] / (self.timestamp_range*2) - 1

            note_rec = pygame.Rect(note_pos, note_top, note_length, self.piano_staff_width/2)

            if (timestamp <= current_timestamp and timestamp + duration > current_timestamp) or (
                    not first_one and timestamp > current_timestamp):
                self.screen.fill(self.color_key_down, note_rec)
            else:
                if is_black:
                    pygame.draw.rect(self.screen, self.white, note_rec, 1)
                else:
                    self.screen.fill(self.white, note_rec)
            first_one = True


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
        # self.draw_lines(WINSIZE[1] * 0.618)

        # pygame.draw.rect(self.screen, self.color_backgroud, note_rec, False)
        self.draw_keys(pitch_key_rec, key_color)
        self.draw_keys(pitch_side_blackkeys_rec, self.black)


if __name__ == '__main__':
    pygame.init()
    WINSIZE = [1270, 700]
    screen = pygame.display.set_mode(WINSIZE)
    pygame.display.set_caption('Piano Keyboard')

    piano = Piano(screen, WINSIZE)
    piano.draw_piano()

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
