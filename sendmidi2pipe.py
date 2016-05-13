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
import time as jiedotime
import os
import os.path, sys, random
import pygame.mixer, pygame.time
import parsemidi
mixer = pygame.mixer
time = pygame.time

isstop = False
interval = 500
n_track = 0

class playtrack(threading.Thread):
    def __init__(self, i, track, tpq, pipeout, pipeout_show):
        threading.Thread.__init__(self)
        self.i = i
        self.track = track
        self.tpq = tpq
        self.pipeout = pipeout
        self.pipeout_show = pipeout_show
        
    def run(self):
        global isstop        
        global interval
        global n_track
        nth = 240
        for e in self.track.events:
            if isstop : 
                for pitch in range(21,108):
                    os.write(self.pipeout_show,
                             'NOTE_OFF %d %d %d \n' % (pitch, 0, 0,))

                sys.exit(0)
            if e.type == 'NOTE_ON':
                if e.velocity < 1:
                    os.write(self.pipeout,
                             'NOTE_OFF %d %d %d \n' % (e.pitch, e.velocity, e.time,))
                    os.write(self.pipeout_show,
                             'NOTE_OFF %d %d %d \n' % (e.pitch, e.velocity, e.time,))

                else:
                    os.write(self.pipeout,
                             'NOTE_ON %d %d %d \n' % (e.pitch,e.velocity, e.time,))
                    os.write(self.pipeout_show,
                             'NOTE_ON %d %d %d \n' % (e.pitch,e.velocity, e.time,))

                #print self.i, '%-s \t' % e.type,
                #print (e.time * interval / self.tpq), jiedotime.time(),
                #print e.pitch, e.velocity, e.channel
            elif e.type == 'NOTE_OFF':
                os.write(self.pipeout,
                         'NOTE_OFF %d %d %d \n' % (e.pitch,e.velocity, e.time,))
                os.write(self.pipeout_show,
                         'NOTE_OFF %d %d %d \n' % (e.pitch,e.velocity, e.time,))

                #print self.i, '%-s \t' % e.type, e.pitch, e.velocity, e.channel
            elif e.type == 'DeltaTime':
                if e.time > 0:
                    #print self.i, '%-s \t' % e.type, e.time
                    time.wait(int(e.time * interval / self.tpq ))
            elif e.type == 'SET_TEMPO': # a 4,time
                x,y,z = e.data
                v = ord(x) * 256 * 256 + ord(y) * 256 + ord(z)  
                interval = v / 1000

        n_track -= 1
        return


def main(infile=None):
    """Play an audio file as a buffered sound sample

    Option argument:
        the name of an audio file (default data/secosmic_low.wav

    """
    pipe_name = '/tmp/pipe_midi'
    pipe_show_name = '/tmp/pipe_show_midi'
    if not os.path.exists(pipe_name):
        os.mkfifo(pipe_name)  
    if not os.path.exists(pipe_show_name):
        os.mkfifo(pipe_show_name)  
    
    m = parsemidi.MidiFile()
    m.open(infile)
    m.read()
    m.close() 
    tpq = m.ticksPerQuarterNote 
    print 'playing:', infile
    #print 'ticksPerQuarterNote', tpq

    pipeout = os.open(pipe_name, os.O_WRONLY)
    pipeout_show = os.open(pipe_show_name, os.O_WRONLY)
    global n_track
    n_track = len(m.tracks)
    for i,track in enumerate(m.tracks):
        thread_track = playtrack(i, track, tpq, pipeout, pipeout_show)
        thread_track.start()
            #for e in i.
            #print type(i) , dir(i)
    global isstop
    
    while n_track:
        try:
            time.wait(100)
        except:
            isstop = True
            break
    # a = raw_input()
    # if len(a) > 0:
    #     os.system('echo "%s" >> goodmidi-list' % infile)
    isstop = True
    os.close(pipeout)
    #os.close(pipeout_show)
    return 0

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    sys.exit(0)
