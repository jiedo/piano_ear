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


class playtrack(threading.Thread):
    def __init__(self, index, track, tpq):
        threading.Thread.__init__(self)
        self.index = index
        self.track = track
        self.tpq = tpq

    def run(self):
        global g_queue
        interval = 500

        for e in self.track.events:
            # if isstop :
            #     for pitch in range(21,108):
            #         g_queue.put('NOTE_OFF %d %d %d' % (pitch, 0, 0,))
            #     return

            if e.type == 'NOTE_ON':
                if e.velocity < 1:
                    g_queue.put('NOTE_OFF %d %d %d' % (e.pitch, e.velocity, e.time,))
                    #print self.index, "OFF", '%-s \t' % e.type, e.pitch, e.velocity, e.channel
                else:
                    g_queue.put('NOTE_ON %d %d %d' % (e.pitch, e.velocity, e.time,))
                    #print self.index, "ON ", '%-s \t' % e.type, e.pitch, e.velocity, e.channel

            elif e.type == 'NOTE_OFF':
                g_queue.put('NOTE_OFF %d %d %d' % (e.pitch, e.velocity, e.time,))
                #print self.index, "OFF", '%-s \t' % e.type, e.pitch, e.velocity, e.channel

            elif e.type == 'DeltaTime':
                if e.time > 0:
                    #print self.index, '%-s \t' % e.type, e.time
                    pygame.time.wait(int(e.time * interval / self.tpq ))

            elif e.type == 'SET_TEMPO': # a 4,time
                x,y,z = e.data
                v = ord(x) * 256 * 256 + ord(y) * 256 + ord(z)
                interval = v / 1000
                #print self.index, '%-s \t' % e.type, e.data




def load_midi(infile=None):
    """Play an audio file as a buffered sound sample
    """

    m = parsemidi.MidiFile()
    m.open(infile)
    m.read()
    m.close()
    tpq = m.ticksPerQuarterNote
    print 'ticksPerQuarterNote', tpq

    for i, track in enumerate(m.tracks):
        thread_track = playtrack(i, track, tpq)
        thread_track.start()

    # for t in all_threads:
    #     t.start()
    #     t.join()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        load_midi(sys.argv[1])

    while True:
        try:
            line = g_queue.get(True, 3)
            print line
        except Exception, e:
            break
