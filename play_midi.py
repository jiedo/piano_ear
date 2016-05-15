#!/usr/bin/env python

"""extremely simple demonstration playing a soundfile
and waiting for it to finish. you'll need the pygame.mixer
module for this to work. Note how in this simple example we
don't even bother loading all of the pygame package. Just
pick the mixer for sound and time for the delay function.

Optional command line argument:
  the name of an audio file.


"""

import threading
import Queue
import os
import os.path, sys
import pygame.mixer
import pygame.time

import parsemidi


g_queue = Queue.Queue()
g_interval = 500
g_tpq = 0

class playtrack(threading.Thread):
    def __init__(self, index, track, tpq):
        threading.Thread.__init__(self)
        self.index = index
        self.track = track
        self.tpq = tpq

    def run(self):
        global g_queue, g_interval

        for e in self.track.events:
            # if isstop :
            #     for pitch in range(21,108):
            #         g_queue.put('NOTE_OFF %d %d %d' % (pitch, 0, 0,))
            #     return

            if e.type == 'NOTE_ON':
                if e.velocity < 1:
                    # print self.index, "OFF", '%-s \t' % e.type, e.pitch, e.velocity, e.channel
                    g_queue.put('NOTE_OFF %d %d %d' % (e.pitch, e.velocity, e.time,))
                else:
                    # print self.index, "ON ", '%-s \t' % e.type, e.pitch, e.velocity, e.channel
                    g_queue.put('NOTE_ON %d %d %d' % (e.pitch, e.velocity, e.time,))

            elif e.type == 'NOTE_OFF':
                # print self.index, "OFF", '%-s \t' % e.type, e.pitch, e.velocity, e.channel
                g_queue.put('NOTE_OFF %d %d %d' % (e.pitch, e.velocity, e.time,))

            elif e.type == 'DeltaTime':
                if e.time > 0:
                    pass
                    #print self.index, '%-s \t' % e.type, e.time
                    #pygame.time.wait(int(e.time * g_interval / self.tpq ))

            elif e.type == 'SET_TEMPO': # a 4,time
                x,y,z = e.data
                v = ord(x) * 256 * 256 + ord(y) * 256 + ord(z)
                g_interval = v / 1000
                #print self.index, '%-s \t' % e.type, e.data




def load_midi(infile=None):
    """Play an audio file as a buffered sound sample
    """

    global g_tpq

    m = parsemidi.MidiFile()
    m.open(infile)
    m.read()
    m.close()
    g_tpq = m.ticksPerQuarterNote
    print 'ticksPerQuarterNote', g_tpq

    all_threads = []
    for i, track in enumerate(m.tracks):
        thread_track = playtrack(i, track, g_tpq)
        thread_track.start()
        all_threads += [thread_track]

    for t in all_threads:
        t.join()

    all_midi_lines = []
    while True:
        try:
            line = g_queue.get(True, 2)
            all_midi_lines += [line]
        except Exception, e:
            print "get error", e
            break

    all_midi_lines.sort(key=lambda x: x.split()[0])
    all_midi_lines.reverse()
    all_midi_lines.sort(key=lambda x: int(x.split()[-1]))

    new_all_midi_lines = []

    pitch_is_on_in_timestamp = {}
    pitch_status = {}
    for code in all_midi_lines:
        cmd, pitch, _, timestamp = code.split()
        if cmd == "NOTE_ON":

            if timestamp not in pitch_is_on_in_timestamp:
                pitch_is_on_in_timestamp[timestamp] = {}
            if pitch_is_on_in_timestamp[timestamp].get(pitch, False):
                print "midi timestamp dup:", code
                continue
            pitch_is_on_in_timestamp[timestamp][pitch] = True

            if pitch_status.get(pitch, False):
                new_all_midi_lines += [code.replace("ON", "OFF") + " 0"]

            pitch_status[pitch] = True
            new_all_midi_lines += [code + " 1"]

        elif cmd == "NOTE_OFF":
            pitch_status[pitch] = False
            if not pitch_is_on_in_timestamp.get(timestamp, {}).get(pitch, False):
                new_all_midi_lines += [code + " 2"]


    new_all_midi_lines.sort(key=lambda x: x.split()[-1])
    new_all_midi_lines.sort(key=lambda x: int(x.split()[-2]))

    return new_all_midi_lines


if __name__ == '__main__':
    if len(sys.argv) > 1:
        all_midi_lines = load_midi(sys.argv[1])
        for line in all_midi_lines:
            print line
