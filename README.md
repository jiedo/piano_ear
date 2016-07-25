# PianoEar: A simple ear training system

## Features

* using midi file as music source
* display a simple scaleable staff of current song
* display a virtual piano keyboard
* highlight playing notes in real time
* highlight playing keys in real time
* can enable/disable any midi track while playing
* play midi file by lossless high quality wav samples
* low latency and smooth sound playing. (with out any noise on MacOS)
* running on MacOS/Linux, maybe Windows

## requirements

* python2.7
* pygame
* pyglet
* 88x8 sound wav files, put in:

    data/Piano_Sounds/Grand-021-048.wav

  * 88 keys (value range: 21 ~ 108)
  * 8 level each key (value is 48, 60, 71, 82, 91, 100, 115, 127)

* midi files, put in:

    midi/

  support 2 level directory. All midi files will show as 2 level menu.


## start

python2 main.py


## shortcut keys

KEY |  Description
--- | ---
Esc |  exit
Enter |  reload midi files, refresh menu
s |  stop current song
Space |  pause/play current song
c |  toggle note head as square / time-bar
Left |  playing slower
Right |  playing faster
UP |  staff page up
Down |  staff page down
,(comma) |  previous song
.(period) |  next song
f |  round turn sound strong to smooth
m |  round turn up sound metronome
z |  shrink staff
x |  expand staff
1~9, 0, -, =, Del |  press to play, black keys
Tab, q~p, [, ], \ |  press to play, white keys
v |  set playing pitch offset, low
b |  set playing pitch offset, middle
n |  set playing pitch offset, high
