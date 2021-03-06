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
import os
import os.path, sys
import pygame.mixer
import pygame.time

import midi
from player import g_grand_pitch_range


METRO_TRACK_IDX = -1
METRO_VOLECITY = 48

g_mseconds_per_quarter = 500
g_ticks_per_quarter = 0
g_time_signature_n = 0
g_time_signature_note = 0
g_bar_duration = 0


def parse_midi_track(track_cmds, all_enabled_tracks, track_idx, track):
    global g_mseconds_per_quarter, g_time_signature_n, g_time_signature_note, g_bar_duration

    if not g_bar_duration:
        g_time_signature_n = 4
        g_time_signature_note = 4
        g_bar_duration =  g_ticks_per_quarter * g_time_signature_n * 4 / g_time_signature_note

    for evt in track.events:
        if evt.type == 'NOTE_ON':
            if track_idx not in all_enabled_tracks:
                all_enabled_tracks[track_idx] = 0
            all_enabled_tracks[track_idx] += 1

            if evt.velocity < 1:
                track_cmds += [["NOTE_OFF", evt.pitch, evt.velocity, track_idx, evt.time]]
            else:
                track_cmds += [["NOTE_ON", evt.pitch, evt.velocity, track_idx, evt.time]]

        elif evt.type == 'NOTE_OFF':
            track_cmds += [["NOTE_OFF", evt.pitch, evt.velocity, track_idx, evt.time]]

        elif evt.type == 'TIME_SIGNATURE':
            nn, dd, cc, bb = evt.data
            g_time_signature_n = ord(nn)
            g_time_signature_note = 2**ord(dd)
            g_bar_duration =  g_ticks_per_quarter * g_time_signature_n * 4 / g_time_signature_note

            print " %d / %d" % (g_time_signature_n, g_time_signature_note)
            print "bar: ", g_bar_duration

        elif evt.type == 'SET_TEMPO':
            x,y,z = evt.data
            v = ord(x) * 256 * 256 + ord(y) * 256 + ord(z)
            g_mseconds_per_quarter = v / 1000
            print "%d bps" % (60000 / g_mseconds_per_quarter)


def load_midi(infile=None):
    """Play an audio file as a buffered sound sample
    """
    global g_ticks_per_quarter

    m = midi.MidiFile()
    m.open(infile)
    m.read()
    m.close()
    g_ticks_per_quarter = m.ticksPerQuarterNote
    print 'ticksPerQuarterNote', g_ticks_per_quarter

    all_enabled_tracks = {}
    all_midi_lines = []
    for i, track in enumerate(m.tracks):
        parse_midi_track(all_midi_lines, all_enabled_tracks, i, track)

    all_enabled_tracks_items = all_enabled_tracks.items()
    all_enabled_tracks_items.sort(key=lambda x:x[1])
    all_enabled_tracks_items.reverse()
    all_tracks_order_idx = {track_idx: idx for idx, (track_idx, _) in enumerate(
        all_enabled_tracks_items)}

    all_enabled_tracks = {track_idx: True for track_idx in all_enabled_tracks}

    all_midi_lines.sort(key=lambda x: x[0])
    all_midi_lines.reverse()
    all_midi_lines.sort(key=lambda x: x[-1])

    new_all_midi_lines = []
    pitch_is_on_in_timestamp = {}
    notes_in_all_staff = []
    pitch_start_timestamp = {}
    for cmd_data in all_midi_lines:
        cmd, pitch, _, track_idx, timestamp = cmd_data
        if pitch not in g_grand_pitch_range:
            continue

        if cmd == "NOTE_ON":
            if timestamp not in pitch_is_on_in_timestamp:
                pitch_is_on_in_timestamp[timestamp] = {}
            if pitch_is_on_in_timestamp[timestamp].get(pitch, False):
                print "midi timestamp dup:", cmd_data
                continue
            pitch_is_on_in_timestamp[timestamp][pitch] = True

            start_timestamp = pitch_start_timestamp.get(pitch, None)
            if start_timestamp is not None:
                note_interval = (timestamp - start_timestamp)/(4.0*g_ticks_per_quarter)
                notes_in_all_staff += [(pitch, start_timestamp, timestamp - start_timestamp,
                                        note_interval,
                                        track_idx)]
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
            note_interval = (timestamp - start_timestamp)/(4.0*g_ticks_per_quarter)
            notes_in_all_staff += [(pitch, start_timestamp, timestamp - start_timestamp,
                                    note_interval,
                                    track_idx)]
            pitch_start_timestamp[pitch] = None
            if not pitch_is_on_in_timestamp.get(timestamp, {}).get(pitch, False):
                new_all_midi_lines += [cmd_data + [2]]

    max_timestamp = notes_in_all_staff[-1][1] + notes_in_all_staff[-1][2]
    offset_bar = max_timestamp - (max_timestamp / g_bar_duration * g_bar_duration)

    # add metronome
    _bar_pos = offset_bar
    while _bar_pos < max_timestamp:
        interval = g_bar_duration/g_time_signature_n
        for pos in range(0, g_bar_duration, interval):
            pitch = 1
            if pos == 0:
                pitch = 0
            new_all_midi_lines += [["METRO_ON", pitch, METRO_VOLECITY, METRO_TRACK_IDX, _bar_pos+pos, 1]]
            # new_all_midi_lines += [["METRO_OFF", pitch, 48, _bar_pos+pos+interval/4, 2]]

        _bar_pos += g_bar_duration

    # sort by timestamp
    new_all_midi_lines.sort(key=lambda x: x[-1])
    new_all_midi_lines.sort(key=lambda x: x[-2])

    # debug note type
    for note_data in notes_in_all_staff:
        pitch, timestamp, duration, note_interval, track_idx = note_data
        note_types = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]

        a = int(1/note_interval)
        b = 1/(note_interval*3)
        c = 1/(note_interval*7)
        if a in note_types and b in note_types and c in note_types:
            print "error", a, b, c, note_interval
        else:
            if a in note_types:
                pass
                # print "note interval:", a
            elif b in note_types:
                print "note interval trip:", b
            elif c in note_types:
                print "note interval seven:", c
            else:
                print "error interval:", a, b, c, note_interval

    return new_all_midi_lines, notes_in_all_staff, all_enabled_tracks, all_tracks_order_idx


if __name__ == '__main__':
    if len(sys.argv) > 1:
        all_midi_lines = load_midi(sys.argv[1])
        for line in all_midi_lines:
            print line
