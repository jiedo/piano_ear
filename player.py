#encoding: utf8

"""A simple starfield example. Note you can move the 'center' of
the starfield by leftclicking in the window. This example show
the basics of creating a window, simple pixel plotting, and input
event management"""


import math
import pygame
from pygame.locals import *
from sys import platform as _platform
import sys


__create_time__ = "May 16 2016"

_platform_file = _platform


if "pygame" in sys.argv:
    _platform = "pygame"

if _platform == "darwin":
    # OS X
    import AppKit
elif _platform == "pygame":
    import pygame.mixer
    pygame.mixer.init(44100)    #raises exception on fail


g_grand_pitch_range  = range(21,109)
g_volecity_list = [48, 60, 71, 82, 91, 100, 115, 127]


def get_volecity(v):
    selectv = 48
    absdit = abs(selectv - v)
    for vo in g_volecity_list:
        if abs(vo - v) <= absdit:
            absdit = abs(vo - v)
            selectv = vo
        else:
            return selectv
    return 127


def init():
    if _platform != "darwin":
        pygame.mixer.set_num_channels(88 * 8)

    devices = {}
    if _platform in ["linux", "linux2"]:
        import alsaaudio

        for i in range(16):
            device = alsaaudio.PCM()
            device.setchannels(2)
            device.setrate(44100)
            device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
            devices[i] = {'pcm': device,
                          'pitch':0
                          }
    return devices


def stop(devices, pitch, volecity, sounds):
    if _platform == "darwin":
        for volecity in g_volecity_list:
            _sound = sounds[(pitch, volecity)]
            _sound.setVolume_(0.0)

    elif _platform == "pygame":
        for volecity in g_volecity_list:
            _sound = sounds[(pitch, volecity)]
            _sound.set_volume(0.0)

    elif _platform in ["linux", "linux2"]:
        try:
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
        except :
            pass


def play(devices, pitch, volecity, sounds):
    if _platform == "darwin":
        _sound = sounds[(pitch, volecity)]
        if _sound.isPlaying():
            _sound.stop()

        _sound.setVolume_(0.7)
        is_ok = _sound.play()
        if not is_ok:
            print "playing is:", _sound.isPlaying()

    elif _platform == "pygame":
        _sound = sounds[(pitch, volecity)]
        _sound.stop()

        _sound.set_volume(0.7)
        if pitch < 160:
            _sound.play()

    elif _platform in ["linux", "linux2"]:
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
            sound, soundlen = sounds[(pitch, volecity)]
            pcm['pcm'].setperiodsize(soundlen)
            pcm['pcm'].write(sound)
            pcm['pitch'] = pitch


def test_sounds(sounds_keys, sounds):
    count = 0
    last_time = time.time()
    bps = 0
    while True:
        print "################", bps
        count += 1
        if time.time() - last_time > 1:
            bps = count
            count = 0
            last_time = time.time()

        keys = [random.choice(sounds_keys) for _ in range(3)]

        for key in keys:
            print "play key:", key
            if _platform == "darwin":
                sounds[key].setVolume_(0.8)
            elif _platform == "pygame":
                sounds[key].set_volume(0.8)
            print sounds[key].play()

        time.sleep(0.05)

        for key in keys:
            if _platform == "darwin":
                sounds[key].setVolume_(0.0)
            elif _platform == "pygame":
                sounds[key].set_volume(0.0)

        time.sleep(0.03)

        for key in keys:
            print "stop key:", key
            print sounds[key].stop()


def load_sounds():
    #volecity_list = [100]
    sounds = {}
    sounds_keys = []
    for g in g_grand_pitch_range:
        for v in g_volecity_list:
            if _platform_file == "darwin":
                sound_file = "/Users/jie/astudy/jiedo/Piano_Sounds/Grand-%03d-%03d.wav" % (g,v)
            else:
                sound_file = "/media/debian/home/jie/astudy/jiedo/ivory-yamaha-wav/Grand-%03d-%03d.wav" % (g,v)

            if _platform == "darwin":
                sounds[(g,v)] = AppKit.NSSound.alloc().initWithContentsOfFile_byReference_(sound_file, False)

            elif _platform == "pygame":
                sounds[(g,v)] = pygame.mixer.Sound(sound_file)

            elif _platform in ["linux", "linux2"]:
                import wave
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

    return sounds_keys, sounds


def show_keys_press(piano, cmd, pitch):
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
        key_color = key_color_down

    # note_rec, note_pos = piano.draw_note(pitch, top=WINSIZE[1] * 0.7)
    # piano.draw_lines(WINSIZE[1] * 0.618)

    # pygame.draw.rect(piano.screen, piano.backgroud_color, note_rec, False)
    piano.draw_keys(pitch_key_rec, key_color)
    piano.draw_keys(pitch_side_blackkeys_rec, piano.black)