#encoding: utf8


import pygame
import time
import parse_midi

import player


class Bps():
    def __init__(self):
        self.bps_count = 0
        self.count = 0
        self.last_bps_time = 0

    def get_bps_count(self):
        self.count += 1
        if time.time() - self.last_bps_time > 1:
            self.bps_count = self.count
            self.count = 0
            self.last_bps_time = time.time()

        return self.bps_count


g_bps = Bps()


def sync_play_time(self, pitch_timestamp, old_time):
    # sleep
    deta_time = time.time() - old_time
    deta_timestamp = pitch_timestamp - self.last_timestamp
    wait_time = int(deta_timestamp * parse_midi.g_mseconds_per_quarter / parse_midi.g_ticks_per_quarter )
    # print "---- midi need wait:", wait_time

    ## show before play
    deta_time = time.time() - old_time
    if wait_time - deta_time*1000 > 10:
        self.gl_screen_blit()
        pygame.display.flip()
    deta_time = time.time() - old_time
    # print "after pygame:", int(deta_time*1000)

    for cmd, pitch, volecity in self.play_commands:
        if cmd == "NOTE_ON":
            player.play(pitch, volecity, self.sounds)
        elif cmd == "NOTE_OFF":
            player.stop(pitch, volecity, self.sounds)
        elif cmd == "METRO_ON" and player.g_metronome_volume > 0:
            player.play(pitch, volecity, self.sounds)
    deta_time = time.time() - old_time
    # print "after play:", int(deta_time*1000)

    player.real_stop(self.sounds, wait_time/1000.0 - deta_time - 0.03)
    deta_time = time.time() - old_time
    # print "after stop:", int(deta_time*1000)

    if wait_time/1000.0 - deta_time > 0:
        time.sleep((wait_time/1000.0 - deta_time))
    # deta_time = time.time() - old_time
    # print "after all:", int(deta_time*1000)


def show_chord_keys_by_ascii(time_pitchs):
    time_pitchs.sort()
    key2color = [(1, 'C'), (1, 'C'), (3, 'D'), (3, 'D'), (8, 'E'),
                 (2, 'F'), (2, 'F'), (6, 'G'), (6, 'G'), (4, 'A'), (4, 'A'), (5, 'B')]
    blackkeys_index = [1, 3, 6, 8, 10]
    last = 0
    for i in time_pitchs:
        between = '-'
        if last == 0: between = ' '
        isBlack = '07'
        if (i % 12) in blackkeys_index:
            isBlack = '03'
        color, note = key2color[i % 12]
        print ('%s%s' % (between * (i - last -1),
                         '\033[%s;3%d;40m%s\033[0m' % (isBlack, color, note))),
        last = i
    print
