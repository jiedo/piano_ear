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
WINSIZE = [1248, 740]

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
    # staff_img_png = pygame.image.load("data.png").convert_alpha()
    # staff_img = staff_img_png
    # staff_img_rect = staff_img.get_rect()
    # print staff_img_rect
    # piano.screen.blit(staff_img, staff_img_rect, (0, 0, WINSIZE[0], WINSIZE[1] * 0.618))

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
        pygame.mixer.set_num_channels(88 * 8)

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

    for g in grand_pitch_range:
        for v in volecity_list:
            sound_file = "/Users/jie/astudy/jiedo/Piano_Sounds/Grand-%03d-%03d.wav" % (g,v)
            if _platform == "darwin":
                sounds[(g,v)] = AppKit.NSSound.alloc().initWithContentsOfFile_byReference_(sound_file, False)

            elif _platform == "pygame":
                sounds[(g,v)] = pygame.mixer.Sound(sound_file)

            elif _platform in ["linux", "linux2"]:
                import wave
                sound_file = "/media/debian/home/jie/astudy/jiedo/ivory-yamaha-wav/Grand-%03d-%03d.wav" % (g,v)
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



    # count = 0
    # last_time = time.time()
    # bps = 0
    # while True:
    #     print "################", bps
    #     count += 1
    #     if time.time() - last_time > 1:
    #         bps = count
    #         count = 0
    #         last_time = time.time()

    #     keys = [random.choice(sounds_keys) for _ in range(3)]

    #     for key in keys:
    #         print "play key:", key
    #         sounds[key].setVolume_(0.8)
    #         print sounds[key].play()

    #     time.sleep(0.05)

    #     for key in keys:
    #         sounds[key].setVolume_(0.0)

    #     time.sleep(0.03)

    #     for key in keys:
    #         print "stop key:", key
    #         print sounds[key].stop()


    #print sounds_keys
    time_pitchs = []
    last_timestamp = -1
    old_time = 0
    last_cmd = ""
    timestamp = 0

    bps_count = 0
    count = 0
    last_bps_time = 0
    is_pause = False
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

                elif e.key in [K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9]:
                    print "Progress:", e.key - 48
                    piano.draw_piano()
                    g_midi_cmd_idx = len(g_all_midi_lines) * (e.key - 48) / 10
                    last_timestamp = -1

                elif e.key == K_RETURN:
                    is_clear = True
                    is_pause = not is_pause

                elif e.key == K_SPACE:
                    if is_clear:
                        piano.draw_piano()
                        g_all_midi_lines = play_midi.load_midi("data.midi")
                        g_midi_cmd_idx = 0
                        is_pause = False
                        is_clear = False

            elif e.type == MOUSEBUTTONDOWN and e.button == 1:
                pass

        # playtrack
        try:
            if is_pause or g_midi_cmd_idx >= len(g_all_midi_lines):
                pygame.display.update()
                time.sleep(0.5)
                continue

            midi_line = g_all_midi_lines[g_midi_cmd_idx]
            g_midi_cmd_idx += 1
            # print midi_line
            cmd, pitch, volecity_data, pitch_timestamp = midi_line.split()[:4]
            volecity = get_volecity(int(volecity_data))
            pitch = int(pitch)
            pitch_timestamp = int(pitch_timestamp)
            if last_timestamp == -1:
                last_timestamp = pitch_timestamp - 1

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
            print "midi need wait:", wait_time

            deta_time = time.time() - old_time
            if wait_time - deta_time*1000 > 80:
                pygame.display.update()

            deta_time = time.time() - old_time
            if wait_time/1000.0 - deta_time > 0:
                time.sleep((wait_time/1000.0 - deta_time))

            deta_time = time.time() - old_time
            old_time = time.time()
            last_timestamp = pitch_timestamp
            time_pitchs = []

            print "bps:", bps_count
            # bps
            count += 1
            if time.time() - last_bps_time > 1:
                bps_count = count
                count = 0
                last_bps_time = time.time()


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
            if last_cmd == "NOTE_OFF":
                last_cmd = "NOTE_ON"
                if _platform == "darwin":
                    time.sleep(0.02)

            if pitch not in time_pitchs:
                time_pitchs += [pitch]

            # note_rec, note_pos = piano.draw_note(pitch, top=WINSIZE[1] * 0.7)
            #piano.draw_lines(WINSIZE[1] * 0.618)
            piano.draw_keys(pitch_key_rec, key_color_down)
            piano.draw_keys(pitch_side_blackkeys_rec, piano.black)

            if _platform == "darwin":
                _sound = sounds[(pitch, volecity)]
                # print "play", pitch, volecity
                if _sound.isPlaying():
                    _sound.stop()

                _sound.setVolume_(0.7)
                is_ok = _sound.play()
                if not is_ok:
                    print "playing is:", _sound.isPlaying()

            elif _platform == "pygame":
                _sound = sounds[(pitch, volecity)]
                _sound.set_volume(0.7)
                if pitch < 160:
                    _sound.play()
                # for ch_data in channels:
                #     ch, ch_pitch = ch_data
                #     if not ch_pitch or pitch == ch_pitch:
                #         ch_data[1] = pitch
                #         ch.set_volume(0.8)
                #         ch.play(_sound) #, maxtime=400, fade_ms=50)
                #         break

            elif _platform in ["linux", "linux2"]:
                play(devices, pitch, volecity, sounds)

        elif cmd == "NOTE_OFF":
            last_cmd = "NOTE_OFF"
            if _platform == "darwin":
                volecitys = [48, 60, 71, 82, 91, 100, 115, 127]
                for volecity in volecitys:
                    _sound = sounds[(pitch, volecity)]
                    _sound.setVolume_(0.0)


            elif _platform == "pygame":
                volecitys = [48, 60, 71, 82, 91, 100, 115, 127]
                for volecity in volecitys:
                    _sound = sounds[(pitch, volecity)]
                    _sound.set_volume(0.0)
                    #time.sleep(0.02)
                    _sound.stop()

            elif _platform in ["linux", "linux2"]:
                try:
                    stop(devices, pitch)
                except :
                    pass

            # pygame.draw.rect(piano.screen, piano.backgroud_color, note_rec, False)
            #piano.draw_lines(WINSIZE[1] * 0.618)
            piano.draw_keys(pitch_key_rec, key_color)
            piano.draw_keys(pitch_side_blackkeys_rec, piano.black)

        #clock.tick(10)

    g_done = True


if __name__ == '__main__':
    main()
