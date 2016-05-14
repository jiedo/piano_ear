#!/usr/bin/env python
#encoding: utf8

"""extremely simple demonstration playing a soundfile
and waiting for it to finish. you'll need the pygame.mixer
module for this to work. Note how in this simple example we
don't even bother loading all of the pygame package. Just
pick the mixer for sound and time for the delay function.

Optional command line argument:
  the name of an audio file.


"""


from piano import Piano
from pygame.locals import *
from sys import platform as _platform
import os
import os.path, sys, random
import play_midi
import pygame.time
import threading
import time

import wave
import alsaaudio

_platform = "pygame"


if _platform == "darwin":
    # OS X
    import AppKit
elif _platform == "pygame":
    import pygame.mixer
    pygame.mixer.init(44100) #raises exception on fail


g_all_midi_lines = []
g_midi_cmd_idx = 0
g_done = False
g_key_press = None
WINSIZE = [1280, 750]

def get_volecity(v):
    volecity = [48, 60, 71, 82, 91, 100, 115, 127]
    selectv = 48
    absdit = abs(selectv - v)
    for vo in volecity:
        if abs(vo - v) <= absdit:
            absdit = abs(vo - v)
            selectv = vo
        else:
            return selectv
    return 127


def stop(devices, pitch):
    pcm = None
    for d in devices.values():
        if d['pitch'] == pitch:
            pcm = d
            break
    if pcm:
        try:
            pcm['pcm'].pause(1)
        except:
            pass
        pcm['pitch'] = 0


def play(devices, pitch, volecity, sounds):
    pcm = None
    for d in devices.values():
        if d['pitch'] == 0:
            pcm = d
            break

    for d in devices.values():
        if d['pitch'] == pitch:
            pcm = d
            break

    if pcm:
        #print pitch, volecity
        sound, soundlen = sounds[(pitch, volecity)]
        pcm['pcm'].setperiodsize(soundlen)
        pcm['pcm'].write(sound)
        pcm['pitch'] = pitch


def main():
    """Play an audio file as a buffered sound sample
    """

    pygame.init()
    screen = pygame.display.set_mode(WINSIZE)
    pygame.display.set_caption('Piano Keyboard')

    piano = Piano(screen, WINSIZE)

    piano.draw_piano()
    piano.draw_lines(WINSIZE[1] * 0.618)

    # import os
    # os.system("convert -density 100 -depth 24 -quality 99 data.pdf data.png")

    staff_img_png = pygame.image.load("data.png").convert_alpha()
    staff_img = staff_img_png
    staff_img_rect = staff_img.get_rect()
    print staff_img_rect

    piano.screen.blit(staff_img, staff_img_rect, (0, 0, WINSIZE[0], WINSIZE[1] * 0.618))

    clock = pygame.time.Clock()
    global g_done, g_key_press, g_all_midi_lines, g_midi_cmd_idx

    g_all_midi_lines = play_midi.load_midi("data.midi")
    g_midi_cmd_idx = 0

    volecity_list = [48, 60, 71, 82, 91, 100, 115, 127]
    #volecity_list = [100]
    grand_pitch_range  = range(21,109)
    sounds_keys = []
    sounds = {}
    devices = {}
    channels = []
    if _platform != "darwin":
        for i in range(pygame.mixer.get_num_channels()):
            channels += [[pygame.mixer.Channel(i), None]]
            print "channel", i
        print "finished channel"

    if _platform in ["linux", "linux2"]:
        for i in range(16):
            device = alsaaudio.PCM()
            device.setchannels(2)
            device.setrate(44100)
            device.setformat(alsaaudio.PCM_FORMAT_S16_LE)

            devices[i] = {'pcm': device,
                          'pitch':0
                          }

    for g in grand_pitch_range:
        for v in volecity_list:
            sound_file = "/Users/jie/astudy/jiedo/Piano_Sounds/Grand-%03d-%03d.wav" % (g,v)
            sound_file = "/media/debian/home/jie/astudy/jiedo/ivory-yamaha-wav/Grand-%03d-%03d.wav" % (g,v)
            if _platform == "darwin":
                sounds[(g,v)] = AppKit.NSSound.alloc().initWithContentsOfFile_byReference_(sound_file, False)

            elif _platform == "pygame":
                sounds[(g,v)] = pygame.mixer.Sound(sound_file)

            elif _platform in ["linux", "linux2"]:
                sound = wave.open(sound_file, 'rb')
                sounddata = []
                data = sound.readframes(1024)
                while data:
                    sounddata += [data]
                    data = sound.readframes(1024)
                sound.close()
                sound = ''.join(sounddata)
                soundlen = len(sounddata)/44100
                sounds[(g,v)] = sound, soundlen

            sounds_keys += [(g,v)]


    #print sounds_keys
    time_pitchs = []
    last_timestamp = 0
    timestamp = 0

    is_clear = True
    while not g_done:
        for e in pygame.event.get():
            if e.type == QUIT:
                g_done = True
                break
            elif e.type == KEYUP:
                if e.key == K_ESCAPE:
                    g_done = True
                    break
                elif e.key in [K_a, K_b, K_c, K_d, K_e, K_f, K_g, ]:
                    g_key_press = e.key

                elif e.key == K_RETURN:
                    is_clear = True

                elif e.key == K_SPACE:
                    if is_clear:
                        #g_all_midi_lines = play_midi.load_midi("data.midi")
                        g_midi_cmd_idx = 0
                        is_clear = False

            elif e.type == MOUSEBUTTONDOWN and e.button == 1:
                pass

        # playtrack
        try:
            if g_midi_cmd_idx >= len(g_all_midi_lines):
                time.sleep(1)
                continue

            midi_line = g_all_midi_lines[g_midi_cmd_idx]
            g_midi_cmd_idx += 1
            # print midi_line
            cmd, pitch, volecity_data, pitch_timestamp = midi_line.split()[:4]
            volecity = get_volecity(int(volecity_data))
            pitch = int(pitch)
            pitch_timestamp = int(pitch_timestamp)
        except Exception, e:
            time.sleep(1)
            print "no data: ", e
            continue

        if pitch not in grand_pitch_range:
            continue

        if pitch_timestamp != last_timestamp:
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

            # sleep
            deta_timestamp = pitch_timestamp - last_timestamp
            wait_time = int(deta_timestamp * play_midi.g_interval / play_midi.g_tpq )
            print "wait...", wait_time

            old_time = time.time()
            pygame.display.update()
            deta_time = time.time() - old_time
            if wait_time/1000.0 - deta_time > 0:
                time.sleep(wait_time/1000.0 - deta_time)
            #pygame.time.wait(wait_time)

            last_timestamp = pitch_timestamp
            time_pitchs = []

        pitch_side_blackkeys_rec = []
        if pitch in piano.whitekeys.keys():
            pitch_key_rec = [piano.whitekeys[pitch]]
            key_color = piano.white
            if pitch + 1 in piano.blackkeys.keys():
                pitch_side_blackkeys_rec += [piano.blackkeys[pitch+1]]
            if pitch - 1 in piano.blackkeys.keys():
                pitch_side_blackkeys_rec += [piano.blackkeys[pitch-1]]

        elif pitch in piano.blackkeys.keys():
            pitch_key_rec = [piano.blackkeys[pitch]]
            key_color = piano.black

        key_color_down = piano.color_key_down
        if key_color != piano.black:
            key_color_down = piano.color_key_down

        if cmd == "NOTE_ON":
            if pitch not in time_pitchs:
                time_pitchs += [pitch]
                print "play", pitch

            # note_rec, note_pos = piano.draw_note(pitch, top=WINSIZE[1] * 0.7)
            piano.draw_lines(WINSIZE[1] * 0.618)
            piano.draw_keys(pitch_key_rec, key_color_down)
            piano.draw_keys(pitch_side_blackkeys_rec, piano.black)

            if _platform == "darwin":
                _sound = sounds[(pitch, volecity)]
                _sound.setVolume_(0.9)
                _sound.play()

            elif _platform == "pygame":
                _sound = sounds[(pitch, volecity)]
                _sound.set_volume(0.9)
                for ch_data in channels:
                    ch, ch_pitch = ch_data
                    if not ch_pitch or pitch == ch_pitch:
                        ch_data[1] = pitch
                        ch.play(_sound)
                        break

            elif _platform in ["linux", "linux2"]:
                play(devices, pitch, volecity, sounds)

        elif cmd == "NOTE_OFF":
            if _platform == "darwin":
                _sound = sounds[(pitch, volecity)]
                _sound.setVolume_(0.0)
                _sound.stop()
            elif _platform == "pygame":
                _sound = sounds[(pitch, volecity)]
                _sound.set_volume(0.0)
                for ch_data in channels:
                    ch, ch_pitch = ch_data
                    if pitch == ch_pitch:
                        ch.fadeout(100)
                        ch_data[1] = None

            elif _platform in ["linux", "linux2"]:
                try:
                    stop(devices, pitch)
                except :
                    pass

            # pygame.draw.rect(piano.screen, piano.backgroud_color, note_rec, False)
            piano.draw_lines(WINSIZE[1] * 0.618)
            piano.draw_keys(pitch_key_rec, key_color)
            piano.draw_keys(pitch_side_blackkeys_rec, piano.black)

        #clock.tick(10)

    g_done = True


if __name__ == '__main__':
    main()
