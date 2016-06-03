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
import time
from collections import deque

__create_time__ = "May 16 2016"


_platform_file = _platform

IS_FREE = 0
IS_SET_STOP = 1
IS_PLAYING = 2
SOUND_BUFFER_REPEAT = 5
NON_FREE_LIMIT = 0.03

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
g_metronome_volume = 0

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


def real_stop(sounds, time_dead_line=None):
    count_stop = 0
    count_stop_total = 0
    if _platform == "darwin":
        now_time = time.time()
        s_datas_list = sounds.values()
        s_datas_list_count = []
        for s_datas in s_datas_list:
            count_stop_inner = 0
            for s_data in s_datas:
                _sound_status, mute_time, _sound = s_data
                if _sound_status == IS_FREE:
                    break
                if now_time - mute_time < NON_FREE_LIMIT:
                    break
                count_stop_inner += 1
                count_stop_total += 1
            s_datas_list_count += [(s_datas, count_stop_inner)]

        s_datas_list_count.sort(key=lambda x:x[1])
        s_datas_list_count.reverse()
        for s_datas, count_stop_inner in s_datas_list_count:
            if time_dead_line is not None and time_dead_line < time.time() - now_time:
                break
            if count_stop_inner == 0:
                break
            count_stop += count_stop_inner
            for idx, s_data in enumerate(s_datas):
                if idx == count_stop_inner:
                    break
                _sound_status, mute_time, _sound = s_data
                if _sound_status == IS_SET_STOP:
                    _sound.stop()
                    s_data[0] = IS_FREE
                elif _sound_status == IS_PLAYING:
                    if not _sound.isPlaying():
                        _sound.stop()
                        s_data[0] = IS_FREE
            s_datas.rotate(-count_stop_inner)

        if count_stop:
            print count_stop,"/", count_stop_total, "avg stop time is:", int(10000 * (time.time() - now_time)/count_stop)
    return count_stop, count_stop_total


def stop(devices, pitch, volecity, sounds):
    if _platform == "darwin":
        for volecity in g_volecity_list:
            if (pitch, volecity) not in sounds:
                continue
            for s_data in sounds[(pitch, volecity)]:
                _sound_status, _, _sound = s_data
                if _sound_status == IS_PLAYING:
                    _sound.setVolume_(0.0)
                    s_data[0] = IS_SET_STOP
                    s_data[1] = time.time()

    elif _platform == "pygame":
        for volecity in g_volecity_list:
            if (pitch, volecity) not in sounds:
                continue
            _sound = sounds[(pitch, volecity)]
            _sound.set_volume(0.0)

    elif _platform in ["linux", "linux2"]:
        pcm = None
        for d in devices.values():
            if d['pitch'] == pitch:
                pcm = d
                break
        if pcm:
            pcm['pcm'].pause(1)
            pcm['pitch'] = 0


def play(devices, pitch, volecity, sounds):
    global g_metronome_volume

    if _platform == "darwin":
        found_free = False
        for s_data in sounds[(pitch, volecity)]:
            _sound_status, _, _sound = s_data
            if _sound_status != IS_FREE:
                continue
            found_free = True
            s_data[0] = IS_PLAYING
            if _sound.isPlaying():
                _sound.stop()

            if g_metronome_volume < 0 or g_metronome_volume > 1:
                g_metronome_volume = 0

            if pitch < 2:
                _sound.setVolume_(g_metronome_volume)
            else:
                _sound.setVolume_(0.7 * (1 - g_metronome_volume))
            is_ok = _sound.play()
            if not is_ok:
                print "playing is:", _sound.isPlaying()
            break

        if not found_free:
            stop(devices, pitch, volecity, sounds)

    elif _platform == "pygame":
        _sound = sounds[(pitch, volecity)]
        _sound.stop()

        _sound.set_volume(0.7)
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


def load_sounds(sound_keys, sounds):
    # load sounds needed
    if _platform_file == "darwin":
        sound_file = "data/beat.wav"
        if (0, 48) not in sounds:
            sounds[(0, 48)] = deque([[IS_FREE, 0, AppKit.NSSound.alloc().initWithContentsOfFile_byReference_(sound_file, False)] for _ in range(SOUND_BUFFER_REPEAT)], SOUND_BUFFER_REPEAT)

        sound_file = "data/accent.wav"
        if (1, 48) not in sounds:
            sounds[(1, 48)] = deque([[IS_FREE, 0, AppKit.NSSound.alloc().initWithContentsOfFile_byReference_(sound_file, False)] for _ in range(SOUND_BUFFER_REPEAT)], SOUND_BUFFER_REPEAT)

    for pitch, volecity_data in sound_keys:
        volecity = get_volecity(volecity_data)
        if (pitch, volecity) in sounds:
            continue
        sound_file = "data/Piano_Sounds/Grand-%03d-%03d.wav" % (pitch, volecity)

        if _platform == "darwin":
            sounds[(pitch, volecity)] = deque([[IS_FREE, 0, AppKit.NSSound.alloc().initWithContentsOfFile_byReference_(sound_file, False)] for _ in range(SOUND_BUFFER_REPEAT)], SOUND_BUFFER_REPEAT)

        elif _platform == "pygame":
            sounds[(pitch, volecity)] = pygame.mixer.Sound(sound_file)

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
            sounds[(pitch, volecity)] = sound, soundlen
