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

import midi


g_queue = Queue.Queue()
g_interval = 500
g_tpq = 0
g_time_signature_n = 4
g_time_signature_note = 4

def parse_midi_track(track_cmds, track_index, track):
    global g_interval, g_time_signature_n, g_time_signature_note

    g_time_signature_n = 4
    g_time_signature_note = 4

    for e in track.events:
        if e.type == 'NOTE_ON':
            if e.velocity < 1:
                # print track_index, "OFF", '%-s \t' % e.type, e.pitch, e.velocity, e.channel
                track_cmds += [["NOTE_OFF", e.pitch, e.velocity, e.time]]
            else:
                # print track_index, "ON ", '%-s \t' % e.type, e.pitch, e.velocity, e.channel
                track_cmds += [["NOTE_ON", e.pitch, e.velocity, e.time]]

        elif e.type == 'NOTE_OFF':
            # print track_index, "OFF", '%-s \t' % e.type, e.pitch, e.velocity, e.channel
            track_cmds += [["NOTE_OFF", e.pitch, e.velocity, e.time]]

        elif e.type == 'TIME_SIGNATURE': # a 4,time
            # Time signature is expressed as 4 numbers. nn and dd represent the "numerator" and "denominator" of the signature as notated on sheet music. The denominator is a negative power of 2: 2 = quarter note, 3 = eighth, etc.
            #print len(e.data)
            nn, dd, cc, bb = e.data
            g_time_signature_n = nn
            g_time_signature_note = 2**dd

        elif e.type == 'DeltaTime':
            if e.time > 0:
                pass
                #print track_index, '%-s \t' % e.type, e.time
                #pygame.time.wait(int(e.time * g_interval / self.tpq ))

        elif e.type == 'SET_TEMPO': # a 4,time
            x,y,z = e.data
            v = ord(x) * 256 * 256 + ord(y) * 256 + ord(z)
            g_interval = v / 1000
            #print track_index, '%-s \t' % e.type, e.data


def load_midi(infile=None):
    """Play an audio file as a buffered sound sample
    """
    global g_tpq

    m = midi.MidiFile()
    m.open(infile)
    m.read()
    m.close()
    g_tpq = m.ticksPerQuarterNote
    print 'ticksPerQuarterNote', g_tpq

    all_midi_lines = []
    for i, track in enumerate(m.tracks):
        parse_midi_track(all_midi_lines, i, track)

    all_midi_lines.sort(key=lambda x: x[0])
    all_midi_lines.reverse()
    all_midi_lines.sort(key=lambda x: x[-1])

    new_all_midi_lines = []
    pitch_is_on_in_timestamp = {}
    notes_in_all_staff = []
    pitch_start_timestamp = {}
    for cmd_data in all_midi_lines:
        cmd, pitch, _, timestamp = cmd_data
        if cmd == "NOTE_ON":
            if timestamp not in pitch_is_on_in_timestamp:
                pitch_is_on_in_timestamp[timestamp] = {}
            if pitch_is_on_in_timestamp[timestamp].get(pitch, False):
                print "midi timestamp dup:", cmd_data
                continue
            pitch_is_on_in_timestamp[timestamp][pitch] = True

            start_timestamp = pitch_start_timestamp.get(pitch, None)
            if start_timestamp is not None:
                notes_in_all_staff += [(pitch, start_timestamp, timestamp - start_timestamp)]
                # add missing OFF:
                new_all_midi_lines += [["NOTE_OFF"] + cmd_data[1:] + [0]]

            pitch_start_timestamp[pitch] = timestamp

            new_all_midi_lines += [cmd_data + [1]]

        elif cmd == "NOTE_OFF":
            start_timestamp = pitch_start_timestamp.get(pitch, None)
            if start_timestamp is None:
                continue
            if timestamp - start_timestamp <= 0:
                continue
            notes_in_all_staff += [(pitch, start_timestamp, timestamp - start_timestamp)]
            pitch_start_timestamp[pitch] = None
            if not pitch_is_on_in_timestamp.get(timestamp, {}).get(pitch, False):
                new_all_midi_lines += [cmd_data + [2]]

    new_all_midi_lines.sort(key=lambda x: x[-1])
    new_all_midi_lines.sort(key=lambda x: x[-2])

    return new_all_midi_lines, notes_in_all_staff


if __name__ == '__main__':
    if len(sys.argv) > 1:
        all_midi_lines = load_midi(sys.argv[1])
        for line in all_midi_lines:
            print line
