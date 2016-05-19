#encoding: utf8

"""
"""


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


def sync_play_time(pitch_timestamp, last_timestamp, old_time, sounds):
    # sleep
    deta_timestamp = pitch_timestamp - last_timestamp
    wait_time = int(deta_timestamp * parse_midi.g_mseconds_per_quarter / parse_midi.g_ticks_per_quarter )
    print "midi need wait:", wait_time

    deta_time = time.time() - old_time
    #print "after python:", int(deta_time*1000)

    for s_data in sounds.values():
        _sound1_status, _sound2_status, _sound1, _sound2 = s_data
        if _sound1_status == player.IS_SET_STOP:
            _sound1.stop()
            s_data[0] = player.IS_FREE
        elif _sound1_status == player.IS_PLAYING:
            if not _sound1.isPlaying():
                _sound1.stop()
            s_data[0] = player.IS_FREE

        if _sound2_status == player.IS_SET_STOP:
            _sound2.stop()
            s_data[1] = player.IS_FREE
        elif _sound2_status == player.IS_PLAYING:
            if not _sound2.isPlaying():
                _sound2.stop()
            s_data[1] = player.IS_FREE


    if wait_time - deta_time*1000 > 80:
        pygame.display.update()
    deta_time = time.time() - old_time
    #print "after pygame:", int(deta_time*1000)

    if wait_time/1000.0 - deta_time > 0:
        time.sleep((wait_time/1000.0 - deta_time))
    deta_time = time.time() - old_time
    #print "after all:", int(deta_time*1000)


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
